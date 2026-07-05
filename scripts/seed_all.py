import asyncio, uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.models.listing import Listing

async def seed():
    engine = create_async_engine('sqlite+aiosqlite:///gcc_car_value.db')
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    now = datetime.now(timezone.utc)

    brands = {
        'Toyota': ['Land Cruiser','Prado','Camry','Corolla','Hilux','Fortuner','RAV4','Yaris','Avalon','C-HR','Rush','Supra'],
        'Nissan': ['Patrol','Sunny','Altima','X-Trail','Kicks','Navara','Sentra','Maxima','Pathfinder','Armada','Z','GT-R'],
        'Honda': ['Accord','Civic','CR-V','Pilot','HR-V','City','Odyssey','Jazz'],
        'Hyundai': ['Tucson','Santa Fe','Elantra','Accent','Creta','Palisade','Kona','Sonata','Azera','Staria','Ioniq'],
        'Kia': ['Sportage','Sorento','Optima','Picanto','Telluride','K5','K8','Carnival','Seltos','Sonet','Rio','Stinger'],
        'Mitsubishi': ['Pajero','Lancer','Outlander','ASX','Eclipse Cross','Attrage','Montero Sport'],
        'Mazda': ['CX-5','CX-9','CX-30','Mazda6','Mazda3','CX-3','MX-5'],
        'Ford': ['Explorer','Expedition','Edge','F-150','Mustang','Bronco','Ranger','Escape','Territory'],
        'Chevrolet': ['Tahoe','Suburban','Silverado','Captiva','Traverse','Malibu','Camaro','Corvette','Blazer'],
        'GMC': ['Yukon','Sierra','Acadia','Terrain','Canyon'],
        'Lexus': ['LX','ES','RX','IS','GX','LS','NX','RC','LC','UX'],
        'BMW': ['5 Series','X5','3 Series','X3','7 Series','X6','X1','X4','M3','M5','X7','iX'],
        'Mercedes-Benz': ['E-Class','S-Class','G-Class','C-Class','GLE','GLS','A-Class','GLC','AMG GT','EQS'],
        'Audi': ['A4','A6','Q5','Q7','Q3','A5','A8','Q8','e-tron','RS6','RSQ8'],
        'Porsche': ['Cayenne','Macan','911','Panamera','Taycan','718'],
        'Land Rover': ['Range Rover','Range Rover Sport','Defender','Discovery','Evoque','Velar'],
        'Jaguar': ['F-Pace','XE','XF','E-Pace','F-Type','I-Pace'],
        'Cadillac': ['Escalade','XT5','XT6','CT5','CT4','Lyriq'],
        'Infiniti': ['QX80','QX60','QX55','QX50','Q50'],
        'Volvo': ['XC90','XC60','XC40','S90','S60'],
        'Genesis': ['GV80','GV70','G80','G70','GV60'],
        'Subaru': ['Outback','Forester','XV','WRX','BRZ'],
        'Suzuki': ['Vitara','Jimny','Swift','Baleno','Dzire','Fronx'],
        'Dodge': ['Charger','Challenger','Durango'],
        'Jeep': ['Wrangler','Grand Cherokee','Cherokee','Gladiator','Renegade'],
        'Chrysler': ['300','Pacifica'],
        'BYD': ['Han','Tang','Atto 3','Qin','Song','Seal','Dolphin'],
        'Geely': ['Coolray','Azkarra','Monjaro','Emgrand','Tugella'],
        'Changan': ['CS35','CS75','CS85','UNI-K','UNI-T','Eado'],
        'MG': ['ZS','HS','RX5','MG5','MG6','RX8','One'],
        'Volkswagen': ['Tiguan','Teramont','Passat','Golf','Arteon','ID.4','Touareg'],
        'Peugeot': ['3008','5008','2008','508','Landtrek'],
        'Renault': ['Duster','Koleos','Megane','Captur','Arkana'],
        'RAM': ['1500','2500','3500','TRX'],
        'Lincoln': ['Navigator','Aviator','Nautilus','Corsair'],
        'Jetour': ['X70','X90','Dashing','T2'],
        'Haval': ['H6','Jolion','Big Dog','H9'],
        'Tank': ['300','500'],
        'GAC': ['GS8','GS4','GA4','GS3'],
        'Chery': ['Tiggo 7','Tiggo 8','Arrizo 5','Tiggo 4'],
        'Alfa Romeo': ['Stelvio','Giulia'],
        'Maserati': ['Levante','Ghibli','Quattroporte','Grecale'],
        'Bentley': ['Bentayga','Continental','Flying Spur'],
        'Aston Martin': ['DBX','Vantage','DB11'],
        'Ferrari': ['SF90','Roma','F8','812','Purosangue'],
        'Lamborghini': ['Urus','Huracan','Revuelto'],
        'Rolls-Royce': ['Cullinan','Phantom','Ghost'],
        'McLaren': ['720S','GT','Artura'],
    }

    count = 0
    async with factory() as session:
        for make, models in brands.items():
            for model in models[:5]:
                for year in [2022, 2023, 2024]:
                    if count >= 300:
                        break
                    mileage = (2025 - year) * 15000
                    price = 50000 + (hash(make + model + str(year)) % 250000) + 30000
                    listing = Listing(
                        id=str(uuid.uuid4()),
                        source='dubizzle_uae',
                        external_id=('seed_'+make+'_'+model+'_'+str(year)).replace(' ','_').replace('-','')[:30],
                        first_seen_at=now, last_seen_at=now, status='active',
                        make=make, model=model, year=year,
                        mileage_km=mileage, spec='GCC', city='Dubai', country='AE',
                        original_price=price, original_currency='AED',
                        exchange_rate=1.0, exchange_timestamp=now,
                        normalized_price_aed=price, quality_score=85,
                        seller_type='dealer',
                        schema_version=1, parser_version='seed', normalizer_version='seed',
                        pipeline_run_id=uuid.uuid4(),
                    )
                    session.add(listing)
                    count += 1
        await session.commit()

    print(f'Seeded {count} listings across {len(brands)} brands')
    await engine.dispose()

asyncio.run(seed())
