"""DubiCars API scraper — open REST API, 28,856 listings with full structured data.
Run: python scripts/dubicars_scraper.py
"""
import json, sqlite3, uuid, re, time
from datetime import datetime, timezone
from curl_cffi import requests

DB = r'C:\projects\p1\gcc_car_value.db'
NOW = datetime.now(timezone.utc).isoformat()
HEADERS = {'User-Agent': 'Mozilla/5.0','Accept': 'application/json','Accept-Language': 'en-US'}

def extract_number(text):
    text = re.sub(r'[^\d.]', '', str(text).replace(',', ''))
    try: return float(text) if '.' in text else int(text)
    except: return None

def scrape_dubicars(max_pages=500):
    """Scrape DubiCars open API. 20 listings/page. 28,856 total."""
    db = sqlite3.connect(DB)
    new = 0

    for page in range(1, max_pages + 1):
        try:
            url = f'https://www.dubicars.com/api/search?page={page}'
            r = requests.get(url, headers=HEADERS, impersonate='chrome131', timeout=30)
            if r.status_code != 200:
                print(f'  Page {page}: HTTP {r.status_code}')
                if r.status_code in (403, 429): break
                continue

            data = r.json()
            listings = data.get('data', [])
            if not listings:
                print(f'  Page {page}: 0 listings — end reached')
                break

            page_new = 0
            for item in listings:
                try:
                    moe = item.get('moengage-detail', {})
                    details = item.get('details', {})
                    prices = item.get('prices', {})

                    make = moe.get('car_make', '')
                    model = moe.get('car_model', '')
                    if not make or not model:
                        continue

                    ext_id = str(item.get('id', ''))
                    if not ext_id:
                        continue

                    # Check duplicate
                    cur = db.execute('SELECT id FROM listings WHERE source=? AND external_id=?',
                                     ('dubicars', ext_id))
                    if cur.fetchone():
                        continue

                    year = moe.get('car_year') or details.get('year')
                    if year:
                        try: year = int(year)
                        except: pass

                    mileage = moe.get('mileage') or details.get('kilometers')
                    if mileage:
                        try: mileage = int(mileage)
                        except: mileage = None

                    # Price from moengage (clean) or prices string
                    price_aed = moe.get('price') or extract_number(prices.get('original', '')) or 0

                    spec = moe.get('regional_specs', 'GCC')
                    if spec and 'europe' in str(spec).lower(): spec = 'European'
                    elif spec and 'us' in str(spec).lower(): spec = 'US'
                    elif spec and 'japan' in str(spec).lower(): spec = 'Japan'
                    elif spec == 'GCC': pass

                    city = moe.get('location', 'Dubai')
                    body = moe.get('body_type', '')
                    transmission = moe.get('gearbox', '')
                    if transmission: transmission = transmission.lower()
                    fuel = moe.get('fuel_type', '')
                    if fuel: fuel = fuel.lower()

                    link = item.get('link', '')
                    title = item.get('title', '')
                    trim = moe.get('car_trim', '')

                    db.execute('''INSERT INTO listings
                        (id, source, external_id, url, first_seen_at, last_seen_at, status,
                         make, model, trim, year, spec, body_type, transmission, fuel_type,
                         mileage_km, city, country, original_price, original_currency,
                         exchange_rate, exchange_timestamp, normalized_price_aed,
                         quality_score, quality_flags, schema_version, parser_version,
                         normalizer_version, pipeline_run_id)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (str(uuid.uuid4()), 'dubicars', ext_id, link, NOW, NOW, 'active',
                         make, model, trim, year, spec, body, transmission, fuel,
                         mileage, city, 'AE', price_aed, 'AED', 1.0, NOW, price_aed,
                         90, '', 1, 'dubicars_api_v1', 'dubicars_api_v1', str(uuid.uuid4())))
                    page_new += 1
                except Exception:
                    continue

            db.commit()
            print(f'  Page {page}: {page_new} new (total new: {new + page_new})', flush=True)
            new += page_new

            if page % 2 == 0:
                time.sleep(0.5)

        except Exception as e:
            print(f'  Page {page}: ERROR {str(e)[:80]}')
            break

    db.close()
    return new


if __name__ == '__main__':
    db = sqlite3.connect(DB)
    before = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    before_makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    before_models = db.execute('SELECT COUNT(DISTINCT make||\"||\"||model) FROM listings').fetchone()[0]
    db.close()

    print(f'Pre-scrape: {before:,} listings, {before_makes} makes, {before_models} models')
    print(f'DubiCars API has 28,856 total listings. Scraping up to 10,000...')
    print()

    new = scrape_dubicars(max_pages=500)

    db = sqlite3.connect(DB)
    after = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    models = db.execute('SELECT COUNT(DISTINCT make||\"||\"||model) FROM listings').fetchone()[0]
    cur = db.execute('SELECT country, COUNT(*) FROM listings GROUP BY country ORDER BY COUNT(*) DESC')
    countries = cur.fetchall()
    cur = db.execute('SELECT source, COUNT(*) FROM listings GROUP BY source ORDER BY COUNT(*) DESC')
    sources = cur.fetchall()
    db.close()

    print()
    print(f'=== RESULTS ===')
    print(f'New: {new:,} | Total: {after:,} (was {before:,})')
    print(f'Makes: {makes} (was {before_makes}) | Models: {models} (was {before_models})')
    print(f'Countries: {\" \".join(f\"{c}: {n}\" for c,n in countries)}')
    print(f'Sources: {\" \".join(f\"{s}: {n}\" for s,n in sources)}')
