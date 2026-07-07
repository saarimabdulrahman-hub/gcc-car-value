"""Production scraper using curl_cffi for YallaMotor (all 6 GCC countries).
Run: python scripts/scrape_prod.py
"""
import re, sqlite3, uuid, time, sys
from datetime import datetime, timezone
from collections import Counter
from curl_cffi import requests
from bs4 import BeautifulSoup

DB = r'C:\projects\p1\gcc_car_value.db'
NOW = datetime.now(timezone.utc).isoformat()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'en-US,en;q=0.9,ar;q=0.5', 'Accept-Encoding': 'gzip, deflate, br'}
RATE = 2.0  # seconds between detail page requests

VALID_MAKES = {'Toyota','Nissan','Honda','Hyundai','Kia','Mitsubishi','Mazda','Suzuki','Subaru','Isuzu',
    'Ford','Chevrolet','GMC','Cadillac','Dodge','Jeep','Chrysler','RAM','Lincoln','Tesla',
    'BMW','Mercedes-Benz','Mercedes','Audi','Volkswagen','Porsche','Volvo','Land Rover','Jaguar','Mini',
    'Lexus','Infiniti','Acura','Genesis','MG','Jetour','Geely','Changan','BYD','GAC','Chery','Haval',
    'Great Wall','Renault','Peugeot','Citroen','Fiat','Bentley','Rolls-Royce','Ferrari','Lamborghini',
    'Maserati','Aston Martin','McLaren','Alfa Romeo','Lincoln','Opel','Skoda','Seat','Cupra','Polestar',
    'Lucid','Rivian','Foton','JAC','Dongfeng','FAW','BAIC','Wuling','Kaiyi','Exeed','Hongqi','NIO','XPeng'}

COUNTRIES = {
    'uae': ('AE','Dubai','AED',1.0,'https://uae.yallamotor.com'),
    'ksa': ('SA','Riyadh','SAR',1.0,'https://ksa.yallamotor.com'),
    'qatar': ('QA','Doha','QAR',1.0,'https://qatar.yallamotor.com'),
    'kuwait': ('KW','Kuwait City','KWD',12.7,'https://kuwait.yallamotor.com'),
    'bahrain': ('BH','Manama','BHD',9.8,'https://bahrain.yallamotor.com'),
    'oman': ('OM','Muscat','OMR',9.5,'https://oman.yallamotor.com'),
}

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

def parse_listing_url(url):
    """Extract make, model, year, city from YallaMotor URL.
    Format: /used-cars/{make}/{model}/{year}/used-{make}-{model}-{year}-{city}-{id}
    """
    parts = url.split('/')
    make = model = year = city = None
    if len(parts) >= 4:
        make = parts[-4].replace('-', ' ').title() if 'used-cars' in url else None
        model = parts[-3].replace('-', ' ').title() if len(parts) >= 3 else None
        year_str = parts[-2] if len(parts) >= 2 else None
        if year_str and year_str.isdigit():
            year = int(year_str)
    return make, model, year

def normalize_make(name):
    """Normalize makes to consistent naming."""
    if not name: return None
    name = name.strip()
    mapping = {
        'Mercedes': 'Mercedes-Benz', 'Mercedes Benz': 'Mercedes-Benz',
        'Landrover': 'Land Rover', 'Land': 'Land Rover',
        'Alfa': 'Alfa Romeo', 'Aston': 'Aston Martin',
        'Rolls': 'Rolls-Royce', 'Great': 'Great Wall',
    }
    for k, v in mapping.items():
        if name.lower() == k.lower():
            return v
    # Title case each word
    return ' '.join(w[0].upper() + w[1:].lower() if len(w) > 1 else w.upper() for w in name.split())

def normalize_model(make, raw_model):
    """Clean up model name."""
    if not raw_model: return None
    model = raw_model.strip()
    # Remove year numbers from model name
    model = re.sub(r'\b(19|20)\d{2}\b', '', model).strip()
    # Remove common prefixes
    prefixes = ['Used ', 'New ', 'The ']
    for p in prefixes:
        if model.lower().startswith(p.lower()):
            model = model[len(p):].strip()
    return model

def scrape_yallamotor_country(ck, max_pages=5):
    """Scrape one YallaMotor country."""
    cc, dc, cur, rate, base_url = COUNTRIES[ck]
    new = 0

    for page in range(1, max_pages + 1):
        try:
            url = f'{base_url}/used-cars?page={page}'
            resp = requests.get(url, headers=HEADERS, impersonate='chrome131', timeout=30)
            if resp.status_code != 200:
                print(f'  Page {page}: HTTP {resp.status_code}')
                if resp.status_code == 403: break
                continue

            soup = BeautifulSoup(resp.text, 'lxml')
            links = set()
            for a in soup.select('a[href*="/used-cars/"]'):
                href = a.get('href', '')
                if '/used-cars/' in href and href.count('/') > 3 and '/search' not in href and re.search(r'\d{6}', href):
                    full = href if href.startswith('http') else base_url + href
                    links.add(full)

            if not links:
                print(f'  Page {page}: 0 links found')
                break

            page_new = 0
            for link in links:
                time.sleep(RATE)
                try:
                    # Parse make/model/year from URL
                    url_make, url_model, url_year = parse_listing_url(link)
                    make = normalize_make(url_make)
                    if not make or make not in VALID_MAKES:
                        continue
                    model = normalize_model(make, url_model)
                    if not model:
                        continue

                    # Extract external ID from URL
                    eid_match = re.search(r'(\d{6,})', link)
                    if not eid_match:
                        continue
                    external_id = eid_match.group(1)

                    # Check if already exists
                    db = sqlite3.connect(DB)
                    cur = db.execute('SELECT id FROM listings WHERE source=? AND external_id=?',
                                     ('yallamotor', external_id))
                    if cur.fetchone():
                        db.close()
                        continue

                    # Fetch detail page for price, mileage, city, spec
                    detail_resp = requests.get(link, headers=HEADERS, impersonate='chrome131', timeout=30)
                    if detail_resp.status_code != 200:
                        db.close()
                        continue

                    dsoup = BeautifulSoup(detail_resp.text, 'lxml')
                    detail_text = detail_resp.text.lower()

                    # Extract price
                    price_aed = 0
                    for sel in ['.price', '[class*="price"]', '.amount', '[class*="amount"]']:
                        price_el = dsoup.select_one(sel)
                        if price_el:
                            p = extract_number(price_el.get_text(strip=True))
                            if p and p > 1000:
                                price_aed = int(p * rate)
                                break

                    # Extract mileage
                    mileage = extract_mileage(detail_resp.text)

                    # Extract spec
                    spec = 'GCC'
                    if 'us spec' in detail_text or 'american spec' in detail_text: spec = 'US'
                    elif 'japan spec' in detail_text or 'japanese spec' in detail_text: spec = 'Japan'
                    elif 'european spec' in detail_text: spec = 'European'

                    # Extract city
                    city = dc
                    city_map = {
                        'dubai': 'Dubai', 'abu dhabi': 'Abu Dhabi', 'sharjah': 'Sharjah',
                        'ajman': 'Ajman', 'riyadh': 'Riyadh', 'jeddah': 'Jeddah',
                        'dammam': 'Dammam', 'doha': 'Doha', 'kuwait': 'Kuwait City',
                        'muscat': 'Muscat', 'manama': 'Manama',
                    }
                    for ck_text, city_name in city_map.items():
                        if ck_text in detail_text:
                            city = city_name
                            break

                    # Extract body type
                    body = None
                    if 'suv' in detail_text: body = 'SUV'
                    elif 'sedan' in detail_text: body = 'sedan'
                    elif 'hatchback' in detail_text: body = 'hatchback'
                    elif 'coupe' in detail_text: body = 'coupe'
                    elif 'pickup' in detail_text: body = 'pickup'

                    # Extract transmission
                    transmission = None
                    if 'automatic' in detail_text or 'auto' in detail_text: transmission = 'automatic'
                    elif 'manual' in detail_text: transmission = 'manual'

                    details = {
                        'source': 'yallamotor', 'external_id': external_id, 'url': link,
                        'make': make, 'model': model,
                        'year': url_year or extract_year(detail_resp.text),
                        'spec': spec, 'body_type': body, 'transmission': transmission,
                        'mileage_km': mileage, 'city': city, 'country': cc,
                        'original_price': price_aed, 'original_currency': 'AED',
                        'normalized_price_aed': price_aed, 'exchange_rate': 1.0,
                        'quality_score': 85, 'quality_flags': '',
                    }

                    db.execute('''INSERT INTO listings
                        (id, source, external_id, url, first_seen_at, last_seen_at, status,
                         make, model, year, spec, body_type, transmission, mileage_km,
                         city, country, original_price, original_currency, exchange_rate,
                         exchange_timestamp, normalized_price_aed, quality_score, quality_flags,
                         schema_version, parser_version, normalizer_version, pipeline_run_id)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (str(uuid.uuid4()), details['source'], details['external_id'],
                         details['url'], NOW, NOW, 'active',
                         details['make'], details['model'], details['year'],
                         details['spec'], details['body_type'], details['transmission'],
                         details['mileage_km'], details['city'], details['country'],
                         details['original_price'], details['original_currency'],
                         details['exchange_rate'], NOW, details['normalized_price_aed'],
                         details['quality_score'], details['quality_flags'],
                         1, 'prod_v2', 'prod_v2', str(uuid.uuid4())))
                    db.commit()
                    page_new += 1
                    db.close()

                except Exception as e:
                    try: db.close()
                    except: pass
                    continue

            print(f'  Page {page}: {len(links)} links -> {page_new} new', flush=True)
            new += page_new

        except Exception as e:
            print(f'  Error on page {page}: {str(e)[:80]}')
            break

    return new


if __name__ == '__main__':
    db = sqlite3.connect(DB)
    before = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    before_makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    before_models = db.execute('SELECT COUNT(DISTINCT make||\"||\"||model) FROM listings').fetchone()[0]
    db.close()

    print(f'Pre-scrape: {before:,} listings, {before_makes} makes, {before_models} models')
    print()

    total = 0
    for ck in ['uae', 'ksa', 'qatar', 'kuwait', 'bahrain', 'oman']:
        cc = COUNTRIES[ck][0]
        print(f'--- YallaMotor {ck.upper()} ({cc}) ---')
        n = scrape_yallamotor_country(ck, max_pages=3)
        total += n
        print(f'  Total new from {ck}: {n}')
        print()

    db = sqlite3.connect(DB)
    after = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    models = db.execute('SELECT COUNT(DISTINCT make||\"||\"||model) FROM listings').fetchone()[0]
    cur = db.execute('SELECT country, COUNT(*) FROM listings GROUP BY country ORDER BY COUNT(*) DESC')
    countries = cur.fetchall()
    # Sources
    cur = db.execute('SELECT source, COUNT(*) FROM listings GROUP BY source ORDER BY COUNT(*) DESC')
    sources = cur.fetchall()
    db.close()

    print()
    print(f'=== RESULTS ===')
    print(f'New this run: {total:,}')
    print(f'Total listings: {after:,} (was {before:,})')
    print(f'Total makes: {makes} (was {before_makes})')
    print(f'Total models: {models} (was {before_models})')
    print(f"Countries: {', '.join(f'{c}: {n}' for c,n in countries)}")
    print(f"Sources: {', '.join(f'{s}: {n}' for s,n in sources)}")
