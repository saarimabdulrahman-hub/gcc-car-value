"""Bulk scraper runner — expands DB coverage across all sources and countries.
Run: python scripts/bulk_scrape.py
"""
import sqlite3, requests, time, re, uuid, sys, os
from datetime import datetime, timezone
from bs4 import BeautifulSoup

DB = r'C:\projects\p1\gcc_car_value.db'
USER_AGENT = 'GCCCarValue/1.0 (market research bot; academic project)'
RATE = 1.5  # seconds between requests
NOW = datetime.now(timezone.utc).isoformat()

# ── Known makes/models for validation ──────────────────────────
VALID_MAKES = {
    'Toyota','Nissan','Honda','Hyundai','Kia','Mitsubishi','Mazda','Suzuki','Subaru','Isuzu',
    'Ford','Chevrolet','GMC','Cadillac','Dodge','Jeep','Chrysler','RAM','Lincoln','Tesla',
    'BMW','Mercedes-Benz','Mercedes','Audi','Volkswagen','Porsche','Volvo','Land Rover','Jaguar','Mini',
    'Lexus','Infiniti','Acura','Genesis',
    'MG','Jetour','Geely','Changan','BYD','GAC','Chery','Haval','Great Wall',
    'Renault','Peugeot','Citroen','Fiat','Alfa Romeo',
    'Bentley','Rolls-Royce','Ferrari','Lamborghini','Maserati','Aston Martin','McLaren',
}

def slug(s):
    return re.sub(r'[^a-z0-9]', '_', (s or '').lower().strip())

def make_model_from_title(title):
    """Extract make and model from a listing title."""
    title = title.strip()
    # Try known multi-word makes first
    multi = ['Land Rover','Mercedes Benz','Mercedes-Benz','Alfa Romeo','Aston Martin',
             'Rolls Royce','Rolls-Royce','Great Wall']
    found_make = None
    for m in sorted(multi, key=len, reverse=True):
        if title.lower().startswith(m.lower()):
            found_make = m
            break
    if not found_make:
        found_make = title.split()[0] if title.split() else ''

    remainder = title[len(found_make):].strip()
    # Normalize make name
    make_map = {'Mercedes Benz':'Mercedes-Benz','Mercedes':'Mercedes-Benz',
                'Rolls Royce':'Rolls-Royce','Landrover':'Land Rover'}
    make = make_map.get(found_make, found_make)

    # Extract model (first 1-3 words that aren't year/price/spec)
    model_words = []
    for w in remainder.split():
        if re.match(r'^(20\d{2}|AED|SAR|\d{1,3}(,\d{3})*)$', w):
            break
        if w.lower() in ('gcc','us','japan','european','automatic','manual','petrol','diesel'):
            break
        model_words.append(w)
    model = ' '.join(model_words[:3]) if model_words else ''
    return make, model

def extract_number(text):
    text = re.sub(r'[^\d.]', '', str(text).replace(',', ''))
    try: return float(text) if '.' in text else int(text)
    except: return None

def extract_year(text):
    m = re.search(r'\b(19\d{2}|20[0-2]\d)\b', str(text))
    return int(m.group(1)) if m else None

def extract_mileage(text):
    m = re.search(r'(\d[\d,]*)\s*km', str(text), re.IGNORECASE)
    return int(m.group(1).replace(',', '')) if m else None

def extract_spec(text):
    t = str(text).lower()
    if 'gcc' in t: return 'GCC'
    if 'american' in t or 'us spec' in t: return 'US'
    if 'japan' in t: return 'Japan'
    if 'european' in t: return 'European'
    if 'canadian' in t: return 'Canadian'
    return None

def extract_city_country(text, default_country='AE', default_city='Dubai'):
    """Extract city and country from listing text."""
    t = str(text).lower()
    # UAE cities
    if 'dubai' in t: return ('Dubai', 'AE')
    if 'abu dhabi' in t: return ('Abu Dhabi', 'AE')
    if 'sharjah' in t: return ('Sharjah', 'AE')
    if 'ajman' in t: return ('Ajman', 'AE')
    if 'ras al khaimah' in t or 'rak' in t: return ('Ras Al Khaimah', 'AE')
    if 'fujairah' in t: return ('Fujairah', 'AE')
    if 'al ain' in t: return ('Al Ain', 'AE')
    # KSA cities
    if 'riyadh' in t: return ('Riyadh', 'SA')
    if 'jeddah' in t: return ('Jeddah', 'SA')
    if 'dammam' in t: return ('Dammam', 'SA')
    if 'mecca' in t or 'makkah' in t: return ('Mecca', 'SA')
    if 'medina' in t or 'madinah' in t: return ('Medina', 'SA')
    if 'khobar' in t: return ('Khobar', 'SA')
    # Kuwait
    if 'kuwait' in t: return ('Kuwait City', 'KW')
    # Qatar
    if 'doha' in t: return ('Doha', 'QA')
    # Oman
    if 'muscat' in t: return ('Muscat', 'OM')
    if 'salalah' in t: return ('Salalah', 'OM')
    # Bahrain
    if 'manama' in t: return ('Manama', 'BH')
    return (default_city, default_country)

def insert_listing(db, data):
    """Insert or update a listing in SQLite."""
    cur = db.execute(
        'SELECT id FROM listings WHERE source=? AND external_id=?',
        (data['source'], data['external_id'])
    )
    existing = cur.fetchone()
    if existing:
        # Update last_seen_at
        db.execute('UPDATE listings SET last_seen_at=? WHERE id=?',
                   (NOW, existing[0]))
        return False
    db.execute('''INSERT INTO listings
        (source, external_id, url, first_seen_at, last_seen_at, status,
         make, model, year, spec, body_type, transmission, fuel_type,
         city, country, original_price, original_currency, exchange_rate,
         normalized_price_aed, mileage_km, quality_score, quality_flags,
         schema_version, parser_version, normalizer_version, pipeline_run_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (data['source'], data['external_id'], data.get('url',''), NOW, NOW, 'active',
         data.get('make',''), data.get('model',''), data.get('year'), data.get('spec'),
         data.get('body_type'), data.get('transmission'), data.get('fuel_type'),
         data.get('city',''), data.get('country','AE'),
         data.get('original_price',0), data.get('original_currency','AED'), 1.0,
         data.get('normalized_price_aed',0), data.get('mileage_km'),
         data.get('quality_score',85), data.get('quality_flags',''),
         1, 'bulk_v1', 'bulk_v1', str(uuid.uuid4())))
    return True

# ═══════════════════════════════════════════════════════════════
# SCRAPER: YallaMotor (all 6 GCC countries)
# ═══════════════════════════════════════════════════════════════

YALLAMOTOR_COUNTRIES = {
    'uae': ('AE', 'Dubai', 'AED'),
    'ksa': ('SA', 'Riyadh', 'SAR'),
    'qatar': ('QA', 'Doha', 'QAR'),
    'kuwait': ('KW', 'Kuwait City', 'KWD'),
    'bahrain': ('BH', 'Manama', 'BHD'),
    'oman': ('OM', 'Muscat', 'OMR'),
}

EXCHANGE_RATES = {'AED':1.0, 'SAR':1.0, 'QAR':1.01, 'KWD':12.73, 'BHD':9.76, 'OMR':9.54}

def scrape_yallamotor_country(country_key, max_pages=5):
    """Scrape YallaMotor for a specific GCC country."""
    country_code, default_city, currency = YALLAMOTOR_COUNTRIES[country_key]
    rate = EXCHANGE_RATES.get(currency, 1.0)
    base_url = f'https://{country_key}.yallamotor.com'
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})

    new = 0
    for page in range(1, max_pages + 1):
        try:
            url = f'{base_url}/used-cars?page={page}'
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f'  YallaMotor {country_key} page {page}: HTTP {resp.status_code}')
                if resp.status_code == 403: break
                continue
            soup = BeautifulSoup(resp.text, 'lxml')
            links = []
            for a in soup.select("a[href*='/used-cars/']"):
                href = a.get('href', '')
                if '/used-cars/' in href and href.count('/') > 3:
                    links.append(href if href.startswith('http') else base_url + href)
            links = list(set(links))
            if not links:
                print(f'  YallaMotor {country_key} page {page}: no listings found')
                break

            for link in links:
                time.sleep(RATE)
                try:
                    lr = session.get(link, timeout=30)
                    if lr.status_code != 200: continue
                    lsoup = BeautifulSoup(lr.text, 'lxml')

                    # Title
                    title_el = lsoup.select_one('h1, .car-title, [class*="title"]')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title: continue

                    make, model = make_model_from_title(title)
                    if make not in VALID_MAKES: continue

                    year = extract_year(title)
                    mileage = extract_mileage(title)
                    spec = extract_spec(title) or 'GCC'

                    # Price
                    price_el = lsoup.select_one('[class*="price"], .price-value, .car-price')
                    price_aed = 0
                    if price_el:
                        p = extract_number(price_el.get_text(strip=True)) or 0
                        price_aed = int(p * rate)

                    # City
                    city, country = extract_city_country(lr.text, country_code, default_city)

                    # External ID
                    eid_match = re.search(r'/(\d+)[/$]', link)
                    external_id = eid_match.group(1) if eid_match else slug(link[-20:])

                    # Transmission / fuel
                    t = lr.text.lower()
                    transmission = 'automatic' if 'automatic' in t else ('manual' if 'manual' in t else None)
                    fuel = 'petrol' if 'petrol' in t else ('diesel' if 'diesel' in t else ('hybrid' if 'hybrid' in t else None))
                    body = 'SUV' if 'suv' in t else ('sedan' if 'sedan' in t else None)

                    data = {
                        'source': 'yallamotor', 'external_id': external_id, 'url': link,
                        'make': make, 'model': model, 'year': year, 'spec': spec,
                        'mileage_km': mileage, 'city': city, 'country': country,
                        'original_price': price_aed, 'original_currency': 'AED',
                        'normalized_price_aed': price_aed,
                        'body_type': body, 'transmission': transmission, 'fuel_type': fuel,
                        'quality_score': 85, 'quality_flags': '',
                    }

                    db = sqlite3.connect(DB)
                    is_new = insert_listing(db, data)
                    db.commit()
                    db.close()
                    if is_new: new += 1
                except Exception as e:
                    continue
            print(f'  YallaMotor {country_key} page {page}: {len(links)} links, {new} total new')
        except Exception as e:
            print(f'  YallaMotor {country_key}: error on page {page}: {e}')
            break
    return new


# ═══════════════════════════════════════════════════════════════
# SCRAPER: Dubizzle UAE — more pages, more models
# ═══════════════════════════════════════════════════════════════

def scrape_dubizzle_uae(max_pages=15):
    """Scrape Dubizzle UAE used cars with more pages."""
    base_url = 'https://uae.dubizzle.com'
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})

    new = 0
    for page in range(1, max_pages + 1):
        try:
            url = f'{base_url}/motors/used-cars/?page={page}'
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f'  Dubizzle UAE page {page}: HTTP {resp.status_code}')
                if resp.status_code == 403: break
                continue
            soup = BeautifulSoup(resp.text, 'lxml')
            links = []
            for a in soup.select("a[href*='/motors/used-cars/']"):
                href = a.get('href', '')
                if '/motors/used-cars/' in href and '/ads/' not in href:
                    links.append(href if href.startswith('http') else base_url + href)
            links = list(set(links))
            if not links:
                print(f'  Dubizzle UAE page {page}: no listings found')
                break

            for link in links:
                time.sleep(RATE)
                try:
                    lr = session.get(link, timeout=30)
                    if lr.status_code != 200: continue
                    lsoup = BeautifulSoup(lr.text, 'lxml')

                    # Title
                    title_el = lsoup.select_one('h1, [class*="title"], [data-testid="ad-title"]')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title: continue

                    make, model = make_model_from_title(title)
                    if make not in VALID_MAKES: continue

                    year = extract_year(title)
                    mileage = extract_mileage(lsoup.text)
                    spec = extract_spec(lsoup.text) or 'GCC'

                    # Price
                    price_el = lsoup.select_one('[class*="price"], [data-testid="ad-price"]')
                    price_aed = 0
                    if price_el:
                        p = extract_number(price_el.get_text(strip=True)) or 0
                        price_aed = p

                    # City
                    city, country = extract_city_country(lsoup.text, 'AE', 'Dubai')

                    # External ID
                    eid_match = re.search(r'/(\d{6,})[/-]', link)
                    if not eid_match:
                        eid_match = re.search(r'/(\d+)[/$]', link)
                    external_id = eid_match.group(1) if eid_match else slug(link[-20:])

                    t = lr.text.lower()
                    transmission = 'automatic' if 'automatic' in t else ('manual' if 'manual' in t else None)
                    fuel = 'petrol' if 'petrol' in t else ('diesel' if 'diesel' in t else ('hybrid' if 'hybrid' in t else None))
                    body = 'SUV' if 'suv' in t else ('sedan' if 'sedan' in t else None)

                    data = {
                        'source': 'dubizzle_uae', 'external_id': external_id, 'url': link,
                        'make': make, 'model': model, 'year': year, 'spec': spec,
                        'mileage_km': mileage, 'city': city, 'country': country,
                        'original_price': price_aed, 'original_currency': 'AED',
                        'normalized_price_aed': price_aed,
                        'body_type': body, 'transmission': transmission, 'fuel_type': fuel,
                        'quality_score': 85, 'quality_flags': '',
                    }

                    db = sqlite3.connect(DB)
                    is_new = insert_listing(db, data)
                    db.commit()
                    db.close()
                    if is_new: new += 1
                except Exception as e:
                    continue
            print(f'  Dubizzle UAE page {page}: {len(links)} links, {new} total new')
        except Exception as e:
            print(f'  Dubizzle UAE: error on page {page}: {e}')
            break
    return new


# ═══════════════════════════════════════════════════════════════
# SCRAPER: Haraj KSA — Saudi's largest car marketplace
# ═══════════════════════════════════════════════════════════════

def scrape_haraj_ksa(max_pages=10):
    """Scrape Haraj KSA used cars."""
    base_url = 'https://haraj.com.sa'
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT, 'Accept-Language': 'ar,en;q=0.9'})

    new = 0
    for page in range(1, max_pages + 1):
        try:
            url = f'{base_url}/haraj-cars/?page={page}'
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f'  Haraj KSA page {page}: HTTP {resp.status_code}')
                if resp.status_code == 403: break
                continue
            soup = BeautifulSoup(resp.text, 'lxml')
            links = []
            for a in soup.select("a[href*='/car/'], a[href*='/cars/']"):
                href = a.get('href', '')
                if '/car/' in href or '/cars/' in href:
                    links.append(href if href.startswith('http') else base_url + href)
            links = list(set(links))
            if not links:
                print(f'  Haraj KSA page {page}: no listings found')
                break

            for link in links:
                time.sleep(RATE)
                try:
                    lr = session.get(link, timeout=30)
                    if lr.status_code != 200: continue
                    lsoup = BeautifulSoup(lr.text, 'lxml')

                    title_el = lsoup.select_one('h1, .title, [class*="title"]')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title: continue

                    make, model = make_model_from_title(title)
                    if make not in VALID_MAKES: continue

                    year = extract_year(title + ' ' + lsoup.text)
                    mileage = extract_mileage(title + ' ' + lsoup.text)
                    spec = extract_spec(title + ' ' + lsoup.text) or 'GCC'

                    # Price in SAR
                    price_el = lsoup.select_one('[class*="price"], .price-value')
                    price_aed = 0
                    if price_el:
                        p = extract_number(price_el.get_text(strip=True)) or 0
                        price_aed = int(p)

                    # City (Arabic)
                    city, country = 'Riyadh', 'SA'
                    for arabic, en in [('الرياض','Riyadh'),('جدة','Jeddah'),('الدمام','Dammam'),
                                       ('مكة','Mecca'),('المدينة','Medina'),('الخبر','Khobar'),
                                       ('تبوك','Tabuk'),('القصيم','Qassim')]:
                        if arabic in lsoup.text:
                            city = en
                            break

                    eid_match = re.search(r'/(\d+)[/$]', link)
                    external_id = eid_match.group(1) if eid_match else slug(link[-20:])

                    t = (title + ' ' + lsoup.text).lower()
                    transmission = 'automatic' if ('automatic' in t or 'اوتوماتيك' in t) else ('manual' if ('manual' in t or 'عادي' in t) else None)
                    fuel = 'petrol' if 'petrol' in t else ('diesel' if 'diesel' in t else ('hybrid' if 'hybrid' in t else None))
                    body = 'SUV' if ('suv' in t or 'دفع رباعي' in t) else ('sedan' if 'sedan' in t else None)

                    data = {
                        'source': 'haraj_ksa', 'external_id': external_id, 'url': link,
                        'make': make, 'model': model, 'year': year, 'spec': spec,
                        'mileage_km': mileage, 'city': city, 'country': country,
                        'original_price': price_aed, 'original_currency': 'AED',
                        'normalized_price_aed': price_aed,
                        'body_type': body, 'transmission': transmission, 'fuel_type': fuel,
                        'quality_score': 85, 'quality_flags': '',
                    }

                    db = sqlite3.connect(DB)
                    is_new = insert_listing(db, data)
                    db.commit()
                    db.close()
                    if is_new: new += 1
                except Exception as e:
                    continue
            print(f'  Haraj KSA page {page}: {len(links)} links, {new} total new')
        except Exception as e:
            print(f'  Haraj KSA: error on page {page}: {e}')
            break
    return new


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('=== Bulk Scraper Runner ===')
    print()

    db = sqlite3.connect(DB)
    cur = db.execute('SELECT COUNT(*) FROM listings')
    before = cur.fetchone()[0]
    db.close()
    print(f'Pre-scrape listings: {before:,}')
    print()

    total_new = 0

    # 1. YallaMotor — all 6 GCC countries
    print('--- YallaMotor (all 6 GCC countries) ---')
    for ck in ['uae', 'ksa', 'qatar', 'kuwait', 'bahrain', 'oman']:
        cc = YALLAMOTOR_COUNTRIES[ck][0]
        print(f'  Scraping YallaMotor {ck.upper()} ({cc})...')
        n = scrape_yallamotor_country(ck, max_pages=5)
        total_new += n
        print(f'  -> {n} new listings from YallaMotor {ck.upper()}')
        print()

    # 2. Dubizzle UAE — expanded pages
    print('--- Dubizzle UAE ---')
    n = scrape_dubizzle_uae(max_pages=15)
    total_new += n
    print(f'-> {n} new listings from Dubizzle UAE')
    print()

    # 3. Haraj KSA — expanded pages
    print('--- Haraj KSA ---')
    n = scrape_haraj_ksa(max_pages=10)
    total_new += n
    print(f'-> {n} new listings from Haraj KSA')
    print()

    # Results
    db = sqlite3.connect(DB)
    cur = db.execute('SELECT COUNT(*) FROM listings')
    after = cur.fetchone()[0]
    cur = db.execute('SELECT COUNT(DISTINCT make) FROM listings')
    makes = cur.fetchone()[0]
    cur = db.execute('SELECT COUNT(DISTINCT make||"||"||model) FROM listings')
    models = cur.fetchone()[0]
    cur = db.execute('SELECT country, COUNT(*) FROM listings GROUP BY country ORDER BY COUNT(*) DESC')
    countries = cur.fetchall()
    db.close()

    print(f'=== Results ===')
    print(f'New listings added: {total_new:,}')
    print(f'Total listings: {after:,} (was {before:,})')
    print(f'Unique makes: {makes}')
    print(f'Unique models: {models}')
    print(f'By country: {", ".join(f"{c}: {n}" for c, n in countries)}')
