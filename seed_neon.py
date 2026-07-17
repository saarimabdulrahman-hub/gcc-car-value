import asyncio, random
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    e = create_async_engine(
        "postgresql+asyncpg://neondb_owner:npg_jJO7yB9VEUtl@ep-frosty-feather-at0if82x.c-9.us-east-1.aws.neon.tech/neondb"
    )
    async with e.connect() as c:
        r = await c.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='listings')"))
        exists = r.scalar()
        if not exists:
            await c.execute(text("""
                CREATE TABLE IF NOT EXISTS listings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    make VARCHAR(100), model VARCHAR(200), year INTEGER,
                    mileage_km INTEGER, spec VARCHAR(50) DEFAULT 'GCC',
                    city VARCHAR(100), country VARCHAR(2),
                    price_aed NUMERIC, quality_score INTEGER DEFAULT 0,
                    found_on VARCHAR(100), captured_at TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """))
            await c.commit()
            print("Table created")

        mk_models = {
            "Toyota": ["Land Cruiser","Camry","Corolla","Hilux","Fortuner","RAV4"],
            "Nissan": ["Patrol","Sunny","Altima","X-Trail","Kicks"],
            "Honda": ["Accord","Civic","CR-V","Pilot","City"],
            "BMW": ["X5","3 Series","5 Series","X3","7 Series"],
            "Mercedes": ["G-Class","C-Class","E-Class","S-Class","GLE"],
            "Hyundai": ["Tucson","Santa Fe","Elantra","Accent","Creta"],
            "Kia": ["Sportage","Seltos","Telluride","K5","Rio"],
            "Lexus": ["LX","ES","RX","GX","IS"],
            "Audi": ["Q7","A4","A6","Q5","A3"],
            "Ford": ["Bronco","Explorer","Edge","F-150","Mustang"],
            "Chevrolet": ["Tahoe","Camaro","Malibu","Traverse","Silverado"],
            "Mitsubishi": ["Pajero","Lancer","Outlander","ASX","Eclipse Cross"],
        }
        cities = {
            "AE": ["Dubai","Abu Dhabi","Sharjah"],
            "SA": ["Riyadh","Jeddah","Dammam"],
            "KW": ["Kuwait City","Hawalli"],
            "QA": ["Doha","Al Wakrah"],
            "BH": ["Manama","Riffa"],
            "OM": ["Muscat","Salalah"],
        }
        makes = list(mk_models.keys())
        countries = ["AE","SA","KW","QA","BH","OM"]
        for _ in range(200):
            mk = random.choice(makes)
            md = random.choice(mk_models[mk])
            yr = random.randint(2015, 2025)
            mi = random.randint(10000, 200000)
            co = random.choice(countries)
            ci = random.choice(cities[co])
            pr = random.randint(30000, 500000)
            qs = random.randint(60, 100)
            src = random.choice(["Dubizzle","YallaMotor","Haraj","OpenSooq","CarSwitch"])
            await c.execute(text(
                "INSERT INTO listings(id,make,model,year,mileage_km,spec,city,country,price_aed,quality_score,found_on) "
                "VALUES(gen_random_uuid(),:mk,:md,:yr,:mi,:s,:ci,:co,:pr,:qs,:src)"
            ), {"mk":mk,"md":md,"yr":yr,"mi":mi,"s":"GCC","ci":ci,"co":co,"pr":pr,"qs":qs,"src":src})
        await c.commit()
        print("Seeded 200 listings")
    await e.dispose()

asyncio.run(main())
