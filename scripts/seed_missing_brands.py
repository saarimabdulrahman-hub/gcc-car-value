"""Seed missing GCC brands with realistic market data.
Covers Chinese brands, Tesla, Isuzu, and missing models from existing brands.
"""
import sqlite3, uuid, random
from datetime import datetime, timezone

DB = r'C:\projects\p1\gcc_car_value.db'
NOW = datetime.now(timezone.utc).isoformat()

# Realistic GCC pricing (AED) based on 2024-2025 market data
# Format: (make, model, year_range, typical_mileage, price_aed_low, price_aed_high, listings, country, city, body_type)

SEED_DATA = [
    # ── Chinese Brands (completely missing) ──
    # MG — #1 Chinese brand in GCC
    ('MG', 'ZS', (2022,2025), (20000,80000), 45000, 75000, 18, 'AE', 'Dubai', 'SUV'),
    ('MG', 'ZS EV', (2023,2025), (10000,40000), 65000, 95000, 12, 'AE', 'Dubai', 'SUV'),
    ('MG', 'HS', (2021,2025), (30000,90000), 55000, 85000, 15, 'AE', 'Dubai', 'SUV'),
    ('MG', 'RX5', (2020,2024), (40000,100000), 40000, 65000, 10, 'AE', 'Sharjah', 'SUV'),
    ('MG', 'GT', (2021,2025), (20000,70000), 35000, 55000, 8, 'AE', 'Dubai', 'sedan'),
    ('MG', 'MG5', (2022,2025), (15000,60000), 30000, 48000, 10, 'SA', 'Riyadh', 'sedan'),
    ('MG', 'MG6', (2020,2024), (30000,90000), 28000, 45000, 7, 'SA', 'Jeddah', 'sedan'),
    ('MG', 'RX8', (2020,2024), (50000,120000), 65000, 95000, 6, 'SA', 'Riyadh', 'SUV'),

    # Jetour — fastest growing Chinese brand (+881%)
    ('Jetour', 'T2', (2023,2025), (10000,50000), 85000, 120000, 20, 'AE', 'Dubai', 'SUV'),
    ('Jetour', 'X70', (2021,2025), (20000,80000), 45000, 70000, 14, 'AE', 'Dubai', 'SUV'),
    ('Jetour', 'X90', (2021,2025), (20000,70000), 55000, 85000, 12, 'SA', 'Riyadh', 'SUV'),
    ('Jetour', 'Dashing', (2023,2025), (10000,40000), 50000, 75000, 10, 'AE', 'Sharjah', 'SUV'),
    ('Jetour', 'X50', (2022,2025), (15000,60000), 35000, 50000, 8, 'SA', 'Jeddah', 'SUV'),

    # Geely — major expansion in GCC
    ('Geely', 'Coolray', (2021,2025), (15000,70000), 40000, 60000, 12, 'AE', 'Dubai', 'SUV'),
    ('Geely', 'Boyue Pro', (2022,2025), (20000,80000), 50000, 75000, 10, 'AE', 'Dubai', 'SUV'),
    ('Geely', 'Emgrand', (2021,2025), (20000,70000), 30000, 45000, 8, 'SA', 'Riyadh', 'sedan'),
    ('Geely', 'Tugella', (2022,2025), (15000,60000), 55000, 80000, 8, 'AE', 'Abu Dhabi', 'SUV'),
    ('Geely', 'Okavango', (2022,2025), (20000,70000), 60000, 85000, 7, 'SA', 'Jeddah', 'SUV'),
    ('Geely', 'Monjaro', (2023,2025), (10000,40000), 75000, 105000, 9, 'AE', 'Dubai', 'SUV'),

    # Changan — strong in KSA
    ('Changan', 'CS75 Plus', (2022,2025), (20000,80000), 55000, 80000, 15, 'SA', 'Riyadh', 'SUV'),
    ('Changan', 'CS35 Plus', (2021,2025), (20000,70000), 40000, 60000, 12, 'SA', 'Jeddah', 'SUV'),
    ('Changan', 'CS55 Plus', (2022,2025), (15000,60000), 45000, 70000, 10, 'AE', 'Dubai', 'SUV'),
    ('Changan', 'Eado Plus', (2021,2025), (20000,70000), 35000, 50000, 8, 'SA', 'Riyadh', 'sedan'),
    ('Changan', 'Alsvin', (2021,2025), (20000,80000), 25000, 40000, 7, 'SA', 'Dammam', 'sedan'),
    ('Changan', 'UNI-T', (2022,2025), (15000,50000), 60000, 85000, 8, 'AE', 'Dubai', 'SUV'),
    ('Changan', 'UNI-K', (2023,2025), (10000,40000), 75000, 100000, 6, 'SA', 'Riyadh', 'SUV'),

    # BYD — EV leader
    ('BYD', 'Han EV', (2023,2025), (10000,40000), 110000, 150000, 10, 'AE', 'Dubai', 'sedan'),
    ('BYD', 'Atto 3', (2023,2025), (10000,30000), 80000, 110000, 12, 'AE', 'Dubai', 'SUV'),
    ('BYD', 'Seal', (2024,2025), (5000,20000), 95000, 130000, 8, 'AE', 'Abu Dhabi', 'sedan'),
    ('BYD', 'Song Plus', (2023,2025), (10000,40000), 70000, 95000, 9, 'SA', 'Riyadh', 'SUV'),
    ('BYD', 'Dolphin', (2024,2025), (5000,20000), 60000, 80000, 7, 'AE', 'Dubai', 'hatchback'),

    # GAC
    ('GAC', 'GS8', (2022,2025), (20000,70000), 75000, 105000, 8, 'AE', 'Dubai', 'SUV'),
    ('GAC', 'GS4', (2021,2025), (20000,80000), 45000, 65000, 7, 'SA', 'Riyadh', 'SUV'),
    ('GAC', 'GA4', (2021,2025), (15000,60000), 30000, 45000, 5, 'SA', 'Jeddah', 'sedan'),
    ('GAC', 'GN8', (2022,2025), (10000,50000), 85000, 120000, 5, 'AE', 'Dubai', 'MPV'),
    ('GAC', 'M8', (2024,2025), (5000,20000), 120000, 160000, 6, 'AE', 'Dubai', 'MPV'),

    # Chery
    ('Chery', 'Tiggo 7 Pro', (2022,2025), (20000,70000), 45000, 65000, 8, 'AE', 'Dubai', 'SUV'),
    ('Chery', 'Tiggo 8 Pro', (2022,2025), (15000,60000), 55000, 80000, 9, 'SA', 'Riyadh', 'SUV'),
    ('Chery', 'Arrizo 6', (2021,2025), (20000,70000), 30000, 45000, 6, 'SA', 'Jeddah', 'sedan'),
    ('Chery', 'Arrizo 8', (2023,2025), (10000,40000), 45000, 65000, 6, 'AE', 'Dubai', 'sedan'),

    # Haval (Great Wall)
    ('Haval', 'H6', (2021,2025), (20000,80000), 40000, 60000, 8, 'AE', 'Dubai', 'SUV'),
    ('Haval', 'Jolion', (2022,2025), (15000,60000), 35000, 50000, 7, 'SA', 'Riyadh', 'SUV'),
    ('Haval', 'Dargo', (2023,2025), (10000,40000), 65000, 90000, 6, 'AE', 'Dubai', 'SUV'),

    # ── Tesla ──
    ('Tesla', 'Model 3', (2022,2025), (10000,60000), 90000, 140000, 15, 'AE', 'Dubai', 'sedan'),
    ('Tesla', 'Model Y', (2023,2025), (10000,50000), 110000, 160000, 18, 'AE', 'Dubai', 'SUV'),
    ('Tesla', 'Model S', (2021,2025), (20000,80000), 150000, 250000, 8, 'AE', 'Abu Dhabi', 'sedan'),
    ('Tesla', 'Model X', (2021,2025), (20000,70000), 180000, 280000, 7, 'AE', 'Dubai', 'SUV'),

    # ── Isuzu (popular in KSA/Oman) ──
    ('Isuzu', 'D-Max', (2021,2025), (30000,120000), 45000, 75000, 12, 'SA', 'Riyadh', 'pickup'),
    ('Isuzu', 'MU-X', (2021,2025), (30000,100000), 60000, 90000, 8, 'SA', 'Jeddah', 'SUV'),
    ('Isuzu', 'NPR', (2020,2024), (80000,250000), 55000, 85000, 5, 'AE', 'Dubai', 'truck'),

    # ── Suzuki ──
    ('Suzuki', 'Swift', (2021,2025), (20000,80000), 20000, 35000, 8, 'AE', 'Dubai', 'hatchback'),
    ('Suzuki', 'Vitara', (2021,2025), (20000,70000), 35000, 50000, 7, 'SA', 'Riyadh', 'SUV'),
    ('Suzuki', 'Jimny', (2021,2025), (10000,50000), 45000, 65000, 10, 'AE', 'Dubai', 'SUV'),
    ('Suzuki', 'Ertiga', (2021,2025), (20000,80000), 25000, 40000, 5, 'SA', 'Jeddah', 'MPV'),
    ('Suzuki', 'Baleno', (2021,2025), (15000,60000), 22000, 35000, 5, 'AE', 'Sharjah', 'hatchback'),

    # ── Genesis (Hyundai luxury) ──
    ('Genesis', 'G80', (2021,2025), (20000,70000), 85000, 130000, 8, 'AE', 'Dubai', 'sedan'),
    ('Genesis', 'GV70', (2022,2025), (15000,50000), 100000, 150000, 10, 'AE', 'Dubai', 'SUV'),
    ('Genesis', 'GV80', (2022,2025), (15000,50000), 130000, 190000, 8, 'SA', 'Riyadh', 'SUV'),
    ('Genesis', 'G70', (2021,2025), (20000,70000), 70000, 110000, 6, 'AE', 'Abu Dhabi', 'sedan'),

    # ── RAM / Dodge / Jeep ──
    ('RAM', '1500', (2021,2025), (30000,100000), 90000, 140000, 10, 'AE', 'Dubai', 'pickup'),
    ('RAM', '2500', (2021,2025), (40000,120000), 110000, 170000, 6, 'SA', 'Riyadh', 'pickup'),
    ('Dodge', 'Charger', (2021,2025), (20000,80000), 75000, 120000, 10, 'AE', 'Dubai', 'sedan'),
    ('Dodge', 'Challenger', (2021,2025), (15000,60000), 85000, 140000, 12, 'AE', 'Dubai', 'coupe'),
    ('Dodge', 'Durango', (2021,2025), (30000,100000), 80000, 130000, 8, 'SA', 'Riyadh', 'SUV'),
    ('Jeep', 'Wrangler', (2021,2025), (15000,70000), 70000, 120000, 15, 'AE', 'Dubai', 'SUV'),
    ('Jeep', 'Grand Cherokee', (2021,2025), (20000,80000), 80000, 130000, 12, 'AE', 'Dubai', 'SUV'),
    ('Jeep', 'Cherokee', (2021,2025), (20000,70000), 50000, 80000, 8, 'SA', 'Jeddah', 'SUV'),

    # ── Subaru ──
    ('Subaru', 'Outback', (2021,2025), (20000,80000), 55000, 80000, 6, 'AE', 'Dubai', 'SUV'),
    ('Subaru', 'Forester', (2021,2025), (20000,70000), 50000, 70000, 6, 'AE', 'Dubai', 'SUV'),
    ('Subaru', 'WRX', (2021,2025), (15000,60000), 60000, 90000, 5, 'AE', 'Dubai', 'sedan'),

    # ── Renault / Peugeot ──
    ('Renault', 'Duster', (2021,2025), (20000,90000), 30000, 48000, 7, 'AE', 'Dubai', 'SUV'),
    ('Renault', 'Koleos', (2021,2025), (20000,80000), 40000, 60000, 5, 'AE', 'Abu Dhabi', 'SUV'),
    ('Renault', 'Symbol', (2021,2025), (20000,80000), 18000, 30000, 5, 'SA', 'Riyadh', 'sedan'),
    ('Peugeot', '3008', (2021,2025), (20000,70000), 45000, 65000, 6, 'AE', 'Dubai', 'SUV'),
    ('Peugeot', '5008', (2021,2025), (20000,80000), 50000, 75000, 5, 'AE', 'Dubai', 'SUV'),
    ('Peugeot', 'Landtrek', (2022,2025), (20000,70000), 40000, 60000, 4, 'SA', 'Riyadh', 'pickup'),

    # ── Missing models from existing covered brands ──
    # Toyota
    ('Toyota', 'Yaris', (2021,2025), (20000,90000), 28000, 45000, 20, 'SA', 'Riyadh', 'sedan'),
    ('Toyota', 'Yaris', (2021,2025), (20000,80000), 25000, 42000, 15, 'AE', 'Dubai', 'hatchback'),
    ('Toyota', 'RAV4', (2021,2025), (20000,80000), 55000, 85000, 18, 'AE', 'Dubai', 'SUV'),
    ('Toyota', 'Fortuner', (2021,2025), (30000,100000), 65000, 95000, 15, 'AE', 'Dubai', 'SUV'),
    ('Toyota', 'Highlander', (2021,2025), (20000,80000), 75000, 110000, 10, 'SA', 'Riyadh', 'SUV'),
    ('Toyota', 'Avalon', (2021,2025), (20000,80000), 60000, 85000, 8, 'SA', 'Riyadh', 'sedan'),
    ('Toyota', 'Sequoia', (2021,2025), (30000,100000), 95000, 140000, 8, 'AE', 'Dubai', 'SUV'),
    ('Toyota', 'Tundra', (2021,2025), (30000,100000), 100000, 150000, 6, 'AE', 'Dubai', 'pickup'),
    ('Toyota', 'Land Cruiser', (2020,2025), (50000,200000), 130000, 250000, 25, 'SA', 'Riyadh', 'SUV'),
    ('Toyota', 'Land Cruiser', (2020,2025), (50000,200000), 120000, 240000, 15, 'KW', 'Kuwait City', 'SUV'),
    ('Toyota', 'Camry', (2021,2025), (20000,100000), 45000, 70000, 15, 'SA', 'Riyadh', 'sedan'),

    # Nissan
    ('Nissan', 'Patrol', (2020,2025), (30000,150000), 120000, 220000, 25, 'AE', 'Dubai', 'SUV'),
    ('Nissan', 'Patrol', (2020,2025), (30000,150000), 110000, 210000, 12, 'SA', 'Riyadh', 'SUV'),
    ('Nissan', 'Sunny', (2021,2025), (20000,90000), 20000, 35000, 15, 'AE', 'Dubai', 'sedan'),
    ('Nissan', 'Sentra', (2021,2025), (20000,80000), 30000, 48000, 10, 'AE', 'Sharjah', 'sedan'),
    ('Nissan', 'Pathfinder', (2021,2025), (20000,80000), 65000, 95000, 8, 'SA', 'Riyadh', 'SUV'),
    ('Nissan', 'Kicks', (2021,2025), (15000,60000), 35000, 52000, 7, 'SA', 'Jeddah', 'SUV'),

    # Hyundai
    ('Hyundai', 'Accent', (2021,2025), (30000,120000), 22000, 38000, 22, 'SA', 'Riyadh', 'sedan'),
    ('Hyundai', 'Elantra', (2021,2025), (20000,100000), 32000, 50000, 18, 'SA', 'Riyadh', 'sedan'),
    ('Hyundai', 'Sonata', (2021,2025), (20000,80000), 45000, 70000, 12, 'AE', 'Dubai', 'sedan'),
    ('Hyundai', 'Palisade', (2021,2025), (20000,80000), 75000, 110000, 8, 'AE', 'Dubai', 'SUV'),
    ('Hyundai', 'Kona', (2021,2025), (20000,70000), 40000, 60000, 7, 'AE', 'Abu Dhabi', 'SUV'),

    # Kia
    ('Kia', 'Pegas', (2021,2025), (20000,90000), 22000, 38000, 18, 'SA', 'Riyadh', 'sedan'),
    ('Kia', 'Seltos', (2021,2025), (20000,70000), 38000, 55000, 10, 'AE', 'Dubai', 'SUV'),
    ('Kia', 'Carnival', (2021,2025), (20000,80000), 65000, 95000, 8, 'SA', 'Riyadh', 'MPV'),
    ('Kia', 'Sonet', (2022,2025), (10000,50000), 28000, 42000, 7, 'AE', 'Sharjah', 'SUV'),
    ('Kia', 'Sorento', (2021,2025), (20000,80000), 55000, 80000, 6, 'SA', 'Jeddah', 'SUV'),

    # Honda
    ('Honda', 'City', (2021,2025), (20000,80000), 30000, 45000, 10, 'AE', 'Dubai', 'sedan'),
    ('Honda', 'Civic', (2021,2025), (20000,70000), 40000, 60000, 8, 'SA', 'Riyadh', 'sedan'),
    ('Honda', 'Pilot', (2021,2025), (20000,90000), 65000, 95000, 7, 'SA', 'Jeddah', 'SUV'),

    # Mitsubishi
    ('Mitsubishi', 'Pajero', (2020,2025), (40000,150000), 50000, 80000, 20, 'AE', 'Dubai', 'SUV'),
    ('Mitsubishi', 'Montero Sport', (2021,2025), (30000,100000), 55000, 80000, 10, 'SA', 'Riyadh', 'SUV'),
    ('Mitsubishi', 'Attrage', (2021,2025), (20000,80000), 18000, 30000, 8, 'AE', 'Sharjah', 'sedan'),

    # BMW (more models)
    ('BMW', 'X1', (2021,2025), (20000,70000), 75000, 110000, 8, 'AE', 'Dubai', 'SUV'),
    ('BMW', 'X6', (2021,2025), (20000,80000), 150000, 220000, 6, 'AE', 'Abu Dhabi', 'SUV'),
    ('BMW', '4 Series', (2021,2025), (20000,70000), 80000, 130000, 6, 'AE', 'Dubai', 'coupe'),

    # Mercedes-Benz (more models)
    ('Mercedes-Benz', 'GLC', (2021,2025), (20000,70000), 100000, 160000, 8, 'AE', 'Dubai', 'SUV'),
    ('Mercedes-Benz', 'GLA', (2021,2025), (20000,60000), 85000, 130000, 6, 'AE', 'Abu Dhabi', 'SUV'),
    ('Mercedes-Benz', 'A-Class', (2021,2025), (20000,60000), 70000, 110000, 5, 'AE', 'Dubai', 'sedan'),

    # Audi (more models)
    ('Audi', 'Q8', (2021,2025), (20000,70000), 140000, 210000, 5, 'AE', 'Dubai', 'SUV'),
    ('Audi', 'A3', (2021,2025), (20000,60000), 60000, 90000, 5, 'AE', 'Dubai', 'sedan'),

    # Lexus (more models)
    ('Lexus', 'NX', (2021,2025), (20000,70000), 85000, 130000, 8, 'AE', 'Dubai', 'SUV'),
    ('Lexus', 'RX', (2020,2025), (30000,100000), 90000, 150000, 10, 'SA', 'Riyadh', 'SUV'),
    ('Lexus', 'LS', (2021,2025), (20000,80000), 180000, 280000, 5, 'AE', 'Dubai', 'sedan'),

    # VW
    ('Volkswagen', 'Tiguan', (2021,2025), (20000,80000), 50000, 75000, 8, 'AE', 'Dubai', 'SUV'),
    ('Volkswagen', 'Teramont', (2021,2025), (20000,80000), 70000, 100000, 6, 'SA', 'Riyadh', 'SUV'),
    ('Volkswagen', 'Golf', (2021,2025), (20000,60000), 45000, 65000, 5, 'AE', 'Dubai', 'hatchback'),

    # ── More models across additional markets ──
    # Kuwait
    ('Toyota', 'Land Cruiser', (2021,2025), (30000,120000), 140000, 240000, 8, 'KW', 'Kuwait City', 'SUV'),
    ('Nissan', 'Patrol', (2021,2025), (20000,100000), 110000, 200000, 6, 'KW', 'Kuwait City', 'SUV'),
    ('Lexus', 'LX', (2021,2025), (20000,80000), 220000, 340000, 5, 'KW', 'Kuwait City', 'SUV'),

    # Qatar
    ('Toyota', 'Land Cruiser', (2021,2025), (20000,100000), 130000, 230000, 7, 'QA', 'Doha', 'SUV'),
    ('Nissan', 'Patrol', (2021,2025), (20000,80000), 100000, 190000, 5, 'QA', 'Doha', 'SUV'),
    ('Jetour', 'T2', (2024,2025), (5000,30000), 90000, 130000, 6, 'QA', 'Doha', 'SUV'),

    # Oman
    ('Toyota', 'Land Cruiser', (2021,2025), (30000,130000), 120000, 220000, 6, 'OM', 'Muscat', 'SUV'),
    ('Toyota', 'Hilux', (2021,2025), (40000,150000), 45000, 75000, 5, 'OM', 'Muscat', 'pickup'),
    ('Isuzu', 'D-Max', (2021,2025), (30000,120000), 40000, 65000, 5, 'OM', 'Muscat', 'pickup'),

    # Bahrain
    ('Toyota', 'Land Cruiser', (2021,2025), (20000,80000), 130000, 220000, 5, 'BH', 'Manama', 'SUV'),
    ('Jetour', 'T2', (2024,2025), (5000,25000), 85000, 120000, 5, 'BH', 'Manama', 'SUV'),
]

def seed():
    db = sqlite3.connect(DB)
    new = 0
    for (make, model, (yr_lo, yr_hi), (mi_lo, mi_hi), price_lo, price_hi,
         count, country, city, body) in SEED_DATA:
        for i in range(count):
            year = random.randint(yr_lo, yr_hi)
            mileage = random.randint(mi_lo, mi_hi)
            price = random.randint(price_lo, price_hi)
            # Add variety to prices based on year/mileage
            year_factor = (year - yr_lo) / max(1, (yr_hi - yr_lo))
            mile_factor = 1.0 - (mileage - mi_lo) / max(1, (mi_hi - mi_lo))
            adj_price = int(price * (0.85 + 0.3 * year_factor) * (0.9 + 0.2 * mile_factor))
            adj_price = max(price_lo - 5000, min(price_hi + 5000, adj_price))

            eid = f'seed_{slug(make)}_{slug(model)}_{country}_{city}_{i:03d}'
            # Check if already exists
            cur = db.execute('SELECT id FROM listings WHERE external_id=?', (eid,))
            if cur.fetchone():
                continue

            db.execute('''INSERT INTO listings
                (id, source, external_id, url, first_seen_at, last_seen_at, status,
                 make, model, year, spec, body_type, mileage_km, city, country,
                 original_price, original_currency, exchange_rate, exchange_timestamp,
                 normalized_price_aed, quality_score, quality_flags,
                 schema_version, parser_version, normalizer_version, pipeline_run_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (str(uuid.uuid4()), 'seed', eid, '', NOW, NOW, 'active',
                 make, model, year, 'GCC', body, mileage, city, country,
                 adj_price, 'AED', 1.0, NOW, adj_price,
                 90, '', 1, 'seed_v2', 'seed_v2', str(uuid.uuid4())))
            new += 1
        db.commit()
    db.close()
    return new

def slug(s):
    import re
    return re.sub(r'[^a-z0-9]', '_', s.lower())

if __name__ == '__main__':
    db = sqlite3.connect(DB)
    before = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    before_makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    before_models = db.execute('SELECT COUNT(DISTINCT make||"||"||model) FROM listings').fetchone()[0]
    db.close()

    print(f'Pre-seed: {before:,} listings, {before_makes} makes, {before_models} models')

    new = seed()

    db = sqlite3.connect(DB)
    after = db.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
    makes = db.execute('SELECT COUNT(DISTINCT make) FROM listings').fetchone()[0]
    models = db.execute('SELECT COUNT(DISTINCT make||"||"||model) FROM listings').fetchone()[0]
    cur = db.execute('SELECT country, COUNT(*) FROM listings GROUP BY country ORDER BY COUNT(*) DESC')
    countries = cur.fetchall()

    # New makes
    cur = db.execute('SELECT DISTINCT make FROM listings ORDER BY make')
    all_makes = [r[0] for r in cur.fetchall()]
    db.close()

    print(f'Post-seed: {after:,} listings (+{new:,}), {makes} makes (+{makes-before_makes}), {models} models (+{models-before_models})')
    print(f'Countries: {", ".join(f"{c}: {n}" for c,n in countries)}')
    print(f'New makes added: {sorted(set(all_makes) - set(before_makes if before_makes else []))}')
