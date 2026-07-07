"""Haraj KSA scraper using Playwright + GraphQL interception.
Extracts make/model from structured tags array (not title parsing).
Run: python scripts/haraj_gql_scraper.py
"""
import json, re, sqlite3, uuid, time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

DB = r'C:\projects\p1\gcc_car_value.db'
NOW = datetime.now(timezone.utc).isoformat()

ARABIC_MAKES = {
    'تويوتا': 'Toyota',
    'تايوتا': 'Toyota',
    'نيسان': 'Nissan',
    'هوندا': 'Honda',
    'هونداي': 'Hyundai',
    'كيا': 'Kia',
    'ميتسوبيشي': 'Mitsubishi',
    'مازدا': 'Mazda',
    'فورد': 'Ford',
    'شفروليه': 'Chevrolet',
    'جي ام سي': 'GMC',
    'جمس': 'GMC',
    'كاديلاك': 'Cadillac',
    'دودج': 'Dodge',
    'جيب': 'Jeep',
    'كرايسلر': 'Chrysler',
    'بي ام دبليو': 'BMW',
    'مرسيدس': 'Mercedes-Benz',
    'اودي': 'Audi',
    'لكزس': 'Lexus',
    'انفينيتي': 'Infiniti',
    'بورش': 'Porsche',
    'لاند روفر': 'Land Rover',
    'جاكوار': 'Jaguar',
    'فولفو': 'Volvo',
    'سوبارو': 'Subaru',
    'سوزوكي': 'Suzuki',
    'ايسوزو': 'Isuzu',
    'تسلا': 'Tesla',
    'رينو': 'Renault',
    'بيجو': 'Peugeot',
    'فولكس واجن': 'Volkswagen',
    'ام جي': 'MG',
    'جيلي': 'Geely',
    'شانجان': 'Changan',
    'شيري': 'Chery',
    'جيتور': 'Jetour',
    'هافال': 'Haval',
    'جينيسيس': 'Genesis',
    'فيات': 'Fiat',
    'جايكو': 'Jaecoo',
    'لينكولن': 'Lincoln',
    'بنتلي': 'Bentley',
    'فيراري': 'Ferrari',
    'لامبورغيني': 'Lamborghini',
    'مازيراتي': 'Maserati',
    'باجيرو': 'Mitsubishi',
}

ARABIC_CITIES = {
    'الرياض': 'Riyadh',
    'جدة': 'Jeddah',
    'جده': 'Jeddah',
    'الدمام': 'Dammam',
    'مكة': 'Mecca',
    'المدينة': 'Medina',
    'الخبر': 'Khobar',
    'تبوك': 'Tabuk',
    'القصيم': 'Qassim',
    'بريدة': 'Buraidah',
    'الطائف': 'Taif',
    'ابها': 'Abha',
    'حائل': 'Hail',
    'عرعر': 'Arar',
    'جازان': 'Jizan',
    'نجران': 'Najran',
    'الرس': 'Ar Rass',
    'الاحساء': 'Al Ahsa',
    'الجبيل': 'Jubail',
    'ينبع': 'Yanbu',
    'الظهران': 'Dhahran',
}

def extract_number(text):
    if not text: return None
    text = re.sub(r'[^\d.]', '', str(text).replace(',', ''))
    try: return float(text) if '.' in text else int(text)
    except: return None

def extract_make_model(tags, car_info):
    """Extract make and model from structured tags + carInfo."""
    year = car_info.get('model')  # carInfo.model = year

    make = None
    for tag in tags:
        tag_stripped = tag.strip()
        if tag_stripped in ARABIC_MAKES:
            make = ARABIC_MAKES[tag_stripped]
            break

    if not make:
        direct_makes = {'GMC', 'BMW', 'MG', 'BYD', 'RAM', 'GAC'}
        for tag in tags:
            if tag.strip().upper() in direct_makes:
                make = tag.strip().upper()
                break

    if not make:
        eng_makes = sorted(set(ARABIC_MAKES.values()), key=len, reverse=True)
        for tag in tags:
            tl = tag.strip().lower()
            for em in eng_makes:
                if em.lower() in tl:
                    make = em
                    break
            if make: break

    model = None
    candidates = []
    skip_tags = {'حراج السيارات', 'سيارات للتنازل'}
    for tag in tags:
        tag_stripped = tag.strip()
        if tag_stripped in skip_tags: continue
        if tag_stripped in ARABIC_MAKES: continue
        if re.match(r'^\d{4}$', tag_stripped): continue
        cleaned = re.sub(r'\s*\d{4}\s*$', '', tag_stripped).strip()
        if cleaned and len(cleaned) > 1:
            candidates.append(cleaned)
    if candidates:
        candidates.sort(key=len, reverse=True)
        model = candidates[0]
        model = re.sub(r'\s*\d{4}\s*$', '', model).strip()

    return make, model, year


def scrape_haraj(max_pages=8):
    cars = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_response(resp):
            if 'queryName=posts' in resp.url:
                try:
                    body = resp.json()
                    items = body.get('data', {}).get('posts', {}).get('items', [])
                    for item in items:
                        if item.get('carInfo') is not None and item.get('title'):
                            cars.append(item)
                except: pass

        page.on('response', handle_response)
        page.goto('https://haraj.com.sa/', timeout=60000, wait_until='networkidle')
        page.wait_for_timeout(8000)

        for l in page.query_selector_all('a'):
            href = l.get_attribute('href') or ''
            if 'tag' in href and 'حراج السيارات' in href:
                try:
                    l.click()
                    page.wait_for_timeout(10000)
                except: pass
                break

        for _ in range(max_pages):
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(3000)

        browser.close()
    return cars


def insert_cars(cars):
    db = sqlite3.connect(DB)
    new = 0

    for item in cars:
        try:
            tags = item.get('tags', [])
            car_info = item.get('carInfo') or {}
            if not car_info.get('carOrRelated') == 'CAR':
                continue  # Skip parts, accessories, heavy equipment

            make, model, year = extract_make_model(tags, car_info)
            if not make or not model:
                continue

            ext_id = str(item.get('id', ''))
            if not ext_id: continue

            cur = db.execute(
                'SELECT id FROM listings WHERE source=? AND external_id=?',
                ('haraj_ksa', ext_id))
            if cur.fetchone(): continue

            # Price
            price = 0
            price_data = item.get('price') or {}
            p = extract_number(price_data.get('formattedPrice', ''))
            if p and p > 100:
                price = p

            # City
            city_ar = item.get('city', '')
            city = ARABIC_CITIES.get(city_ar, city_ar or 'Riyadh')

            # Mileage: carInfo.mileage is in thousands of km
            mileage = None
            raw_mileage = car_info.get('mileage')
            if raw_mileage and raw_mileage > 0:
                mileage = raw_mileage * 1000

            # Transmission
            gear = car_info.get('gear', '')
            transmission = 'automatic' if gear == 'AUTO' else ('manual' if gear == 'MANUAL' else None)

            # Fuel
            fuel_map = {'GASOLINE': 'petrol', 'DIESEL': 'diesel', 'HYBRID': 'hybrid', 'ELECTRIC': 'electric'}
            fuel = fuel_map.get(car_info.get('fuel', ''), None)

            # URL
            url_slug = item.get('URL', '')
            url = f'https://haraj.com.sa/{url_slug}' if url_slug else ''

            # Body type: Haraj carInfo doesn't have body, infer from tags/title
            body = None
            title_lower = (item.get('title', '')).lower()
            if 'suv' in title_lower: body = 'SUV'
            elif 'sedan' in title_lower: body = 'sedan'
            elif 'hatchback' in title_lower: body = 'hatchback'
            elif 'pickup' in title_lower or 'truck' in title_lower: body = 'pickup'

            db.execute('''INSERT INTO listings
                (id, source, external_id, url, first_seen_at, last_seen_at, status,
                 make, model, year, spec, body_type, transmission, fuel_type, mileage_km,
                 city, country, original_price, original_currency, exchange_rate,
                 exchange_timestamp, normalized_price_aed, quality_score, quality_flags,
                 schema_version, parser_version, normalizer_version, pipeline_run_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (str(uuid.uuid4()), 'haraj_ksa', ext_id, url, NOW, NOW, 'active',
                 make, model, year, 'GCC', body, transmission, fuel, mileage,
                 city, 'SA', price, 'AED', 1.0, NOW, price, 85, '',
                 1, 'haraj_gql_v2', 'haraj_gql_v2', str(uuid.uuid4())))
            new += 1
        except Exception:
            continue

    db.commit()
    db.close()
    return new


if __name__ == '__main__':
    db = sqlite3.connect(DB)
    before = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    db.close()

    print(f'Pre-scrape: {before:,} listings')
    print('Scraping Haraj KSA...')
    cars = scrape_haraj(max_pages=8)
    print(f'Car listings captured: {len(cars)}')

    new = insert_cars(cars)
    print(f'New listings inserted: {new}')

    db = sqlite3.connect(DB)
    after = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    models = db.execute('SELECT COUNT(DISTINCT make||"||"||model) FROM listings').fetchone()[0]
    cur = db.execute('SELECT source, COUNT(*) FROM listings GROUP BY source ORDER BY COUNT(*) DESC')
    sources = cur.fetchall()
    db.close()

    print(f'Total: {after:,} listings, {makes} makes, {models} models')
    sources_str = ', '.join(f'{s}: {n}' for s,n in sources)
    print(f'Sources: {sources_str}')
