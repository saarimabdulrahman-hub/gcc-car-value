"""Seed the database with sample car listings using raw SQL (matches existing schema)."""
import asyncio, asyncpg, uuid, os
from datetime import datetime, timezone

DSN = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@localhost:5432/gcc_car_value")

brands = {
    'Toyota': ['Land Cruiser','Prado','Camry','Corolla','Hilux','Fortuner','RAV4','Yaris'],
    'Nissan': ['Patrol','Sunny','Altima','X-Trail','Kicks','Navara','Sentra','Maxima'],
    'Honda': ['Accord','Civic','CR-V','Pilot','HR-V','City','Odyssey'],
    'Hyundai': ['Tucson','Santa Fe','Elantra','Accent','Creta','Palisade','Kona','Sonata'],
    'Kia': ['Sportage','Sorento','Optima','Picanto','Telluride','Carnival','Seltos','K5'],
    'Mitsubishi': ['Pajero','Lancer','Outlander','ASX','Eclipse Cross','Attrage'],
    'Mazda': ['CX-5','CX-9','CX-30','Mazda6','Mazda3','CX-3'],
    'Ford': ['Explorer','Expedition','Edge','F-150','Mustang','Bronco','Ranger'],
    'Chevrolet': ['Tahoe','Suburban','Silverado','Captiva','Traverse','Malibu','Camaro'],
    'GMC': ['Yukon','Sierra','Acadia','Terrain'],
    'Lexus': ['LX','ES','RX','IS','GX','LS','NX','LC'],
    'BMW': ['5 Series','X5','3 Series','X3','7 Series','X6','X1','X4'],
    'Mercedes-Benz': ['E-Class','S-Class','G-Class','C-Class','GLE','GLS','A-Class','GLC'],
    'Audi': ['A4','A6','Q5','Q7','Q3','A5','A8','Q8'],
    'Porsche': ['Cayenne','Macan','911','Panamera','Taycan'],
    'Land Rover': ['Range Rover','Range Rover Sport','Defender','Discovery','Evoque','Velar'],
    'Dodge': ['Charger','Challenger','Durango'],
    'Jeep': ['Wrangler','Grand Cherokee','Cherokee'],
    'Volvo': ['XC90','XC60','XC40','S60'],
    'Volkswagen': ['Tiguan','Teramont','Passat','Golf'],
    'BYD': ['Atto 3','Seal','Dolphin','Han'],
    'MG': ['ZS','HS','RX5','MG5'],
}

async def seed():
    conn = await asyncpg.connect(DSN)
    now = datetime.now(timezone.utc)
    count = 0

    for make, models in brands.items():
        for model in models:
            for year in [2020, 2021, 2022, 2023, 2024]:
                if count >= 500:
                    break
                mileage = (2025 - year) * 15000 + abs(hash(model)) % 10000
                price = float(30000 + abs(hash(make + model + str(year))) % 250000 + 50000)

                await conn.execute(
                    """INSERT INTO listings (id, make, model, year, mileage_km, spec, city, country,
                                            price_aed, quality_score, found_on, captured_at, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)""",
                    uuid.uuid4(), make, model, year, mileage, 'GCC',
                    'Dubai', 'AE', price, 85, 'seed',
                    now, now
                )
                count += 1

    await conn.close()
    print(f'Seeded {count} listings across {len(brands)} brands')

asyncio.run(seed())
