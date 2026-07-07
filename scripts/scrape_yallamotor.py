"""Targeted YallaMotor scraper — all 6 GCC countries."""
import requests, time, re, sqlite3, uuid
from bs4 import BeautifulSoup
from datetime import datetime, timezone

DB = r'C:\projects\p1\gcc_car_value.db'
NOW = datetime.now(timezone.utc).isoformat()
UA = 'GCCCarValue/1.0 (market research bot)'
RATE = 1.5

VALID_MAKES = {'Toyota','Nissan','Honda','Hyundai','Kia','Mitsubishi','Mazda','Suzuki','Subaru','Isuzu',
    'Ford','Chevrolet','GMC','Cadillac','Dodge','Jeep','Chrysler','RAM','Lincoln','Tesla',
    'BMW','Mercedes-Benz','Mercedes','Audi','Volkswagen','Porsche','Volvo','Land Rover','Jaguar','Mini',
    'Lexus','Infiniti','Acura','Genesis','MG','Jetour','Geely','Changan','BYD','GAC','Chery','Haval',
    'Renault','Peugeot','Citroen','Fiat','Bentley','Rolls-Royce','Ferrari','Lamborghini','Maserati'}

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

COUNTRIES = {
    'uae': ('AE','Dubai','AED','https://uae.yallamotor.com'),
    'ksa': ('SA','Riyadh','SAR','https://ksa.yallamotor.com'),
    'qatar': ('QA','Doha','QAR','https://qatar.yallamotor.com'),
    'kuwait': ('KW','Kuwait City','KWD','https://kuwait.yallamotor.com'),
    'bahrain': ('BH','Manama','BHD','https://bahrain.yallamotor.com'),
    'oman': ('OM','Muscat','OMR','https://oman.yallamotor.com'),
}
RATES = {'AED':1.0,'SAR':1.0,'QAR':1.0,'KWD':12.7,'BHD':9.8,'OMR':9.5}

def scrape():
    total_new = 0
    s = requests.Session()
    s.headers.update({'User-Agent': UA})

    for ck, (cc, dc, cur, base_url) in COUNTRIES.items():
        rate = RATES.get(cur, 1.0)
        new = 0
        for page in range(1, 6):
            try:
                url = f'{base_url}/used-cars?page={page}'
                r = s.get(url, timeout=30)
                if r.status_code != 200:
                    print(f'YallaMotor {ck} p{page}: HTTP {r.status_code}')
                    break
                soup = BeautifulSoup(r.text, 'lxml')
                links = set()
                for a in soup.select('a[href*="/used-cars/"]'):
                    href = a.get('href','')
                    if '/used-cars/' in href and href.count('/') > 3:
                        links.add(href if href.startswith('http') else base_url + href)
                if not links:
                    print(f'YallaMotor {ck} p{page}: 0 links')
                    break
                print(f'YallaMotor {ck} p{page}: {len(links)} links', end='', flush=True)
                page_new = 0
                for link in links:
                    time.sleep(RATE)
                    try:
                        lr = s.get(link, timeout=30)
                        if lr.status_code != 200: continue
                        lsoup = BeautifulSoup(lr.text, 'lxml')
                        title_el = lsoup.select_one('h1, .car-title, [class*="title"]')
                        title = title_el.get_text(strip=True) if title_el else ''
                        if not title: continue
                        title_clean = title.strip()
                        tokens = title_clean.split()
                        make = tokens[0] if tokens else ''
                        if make not in VALID_MAKES: continue
                        remainder = title_clean[len(make):].strip()
                        model_words = []
                        for w in remainder.split():
                            if re.match(r'^(20\d{2}|AED|SAR|\d+)$', w): break
                            if w.lower() in ('gcc','us','japan','automatic','manual'): break
                            model_words.append(w)
                        model = ' '.join(model_words[:3]) if model_words else ''
                        if not model: continue

                        year = extract_year(title)
                        mileage = extract_mileage(lsoup.text)
                        spec_text = (title + ' ' + lsoup.text).lower()
                        spec = 'GCC'
                        if 'american' in spec_text or 'us spec' in spec_text: spec = 'US'
                        elif 'japan' in spec_text: spec = 'Japan'
                        elif 'european' in spec_text: spec = 'European'

                        price_el = lsoup.select_one('[class*="price"], .price-value, .car-price')
                        price_aed = 0
                        if price_el:
                            p = extract_number(price_el.get_text(strip=True)) or 0
                            price_aed = int(p * rate)

                        eid = re.search(r'/(\d+)[/$]', link)
                        external_id = eid.group(1) if eid else f'ym_{ck}_{hash(link) & 0xFFFFFFF:07x}'

                        db = sqlite3.connect(DB)
                        cur = db.execute('SELECT id FROM listings WHERE source=? AND external_id=?',
                                         ('yallamotor', external_id))
                        if not cur.fetchone():
                            db.execute('''INSERT INTO listings
                                (source, external_id, url, first_seen_at, last_seen_at, status,
                                 make, model, year, spec, mileage_km, city, country,
                                 original_price, original_currency, normalized_price_aed,
                                 quality_score, quality_flags, schema_version, parser_version,
                                 normalizer_version, pipeline_run_id)
                                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                                ('yallamotor', external_id, link, NOW, NOW, 'active',
                                 make, model, year, spec, mileage_km, dc, cc,
                                 price_aed, 'AED', price_aed,
                                 85, '', 1, 'bulk_v1', 'bulk_v1', str(uuid.uuid4())))
                            db.commit()
                            page_new += 1
                        db.close()
                    except: pass
                print(f' -> {page_new} new', flush=True)
                new += page_new
            except Exception as e:
                print(f'YallaMotor {ck}: error: {e}')
                break
        print(f'  YallaMotor {ck}: {new} new listings total')
        total_new += new
    return total_new

if __name__ == '__main__':
    db = sqlite3.connect(DB)
    before = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    db.close()
    print(f'Pre-scrape: {before:,} listings')
    print()

    total_new = scrape()

    db = sqlite3.connect(DB)
    after = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    models = db.execute('SELECT COUNT(DISTINCT make||"||"||model) FROM listings').fetchone()[0]
    cur = db.execute('SELECT country, COUNT(*) FROM listings GROUP BY country ORDER BY COUNT(*) DESC')
    countries = cur.fetchall()
    db.close()

    print(f'\n=== RESULTS ===')
    print(f'New: {total_new:,} | Total: {after:,} | Makes: {makes} | Models: {models}')
    print(f'Countries: {", ".join(f"{c}: {n}" for c,n in countries)}')
