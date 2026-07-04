"""Knowledge base seed — top 50 GCC car models with specs, issues, and maintenance costs.

Run once: python -m src.knowledge.seed
Populates: car_specs, car_issues, maintenance_costs, depreciation_curves, model_ratings
"""
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.car_spec import CarSpec
from src.models.car_issue import CarIssue
from src.models.maintenance_cost import MaintenanceCost
from src.models.depreciation_curve import DepreciationCurve
from src.models.model_rating import ModelRating
from src.db.session import async_session_factory
import structlog

logger = structlog.get_logger()

# ============================================================
# TOP 50 GCC MODELS — curated knowledge
# Format: {make: {model: {generation: {year_start, year_end, specs, issues, maintenance, ratings}}}}
# ============================================================

MODELS = {
    "Toyota": {
        "Land Cruiser": {
            "J200 (2008-2021)": {
                "year_start": 2008, "year_end": 2021,
                "body_type": "SUV",
                "engine": [{"size": 5.7, "cylinders": 8, "fuel": "petrol", "hp": 362, "torque": 530}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "4WD",
                "fuel_economy": 14.5, "fuel_tank": 138, "seats": 8,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Timing chain tensioner wear", "severity": "moderate",
                     "mileage": 120000, "cost": 3500,
                     "desc": "Rattling noise on cold start. Replace tensioner before chain jumps."},
                    {"title": "Radiator cracking", "severity": "moderate",
                     "mileage": 150000, "cost": 2500,
                     "desc": "Plastic top tank cracks in GCC heat. Replace with all-aluminum radiator."},
                    {"title": "Air suspension pump failure", "severity": "major",
                     "mileage": 180000, "cost": 6000,
                     "desc": "VXR models only. Pump motor burns out. Convert to coil springs for reliability."},
                    {"title": "Water pump leak", "severity": "minor",
                     "mileage": 100000, "cost": 1500,
                     "desc": "Slow coolant leak from weep hole. Replace with timing belt service."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1200, "major_cost": 2800,
                    "insurance": 4500,
                },
                "ratings": {"reliability": 5, "comfort": 4, "performance": 4,
                            "fuel_economy": 2, "offroad": 5, "resale": 5, "overall": 4.5},
            },
            "J300 (2022-present)": {
                "year_start": 2022, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.5, "cylinders": 6, "fuel": "petrol", "hp": 409, "torque": 650}],
                "transmission": [{"type": "automatic", "gears": 10}],
                "drivetrain": "4WD",
                "fuel_economy": 12.0, "fuel_tank": 110, "seats": 7,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Turbo wastegate rattle", "severity": "minor",
                     "mileage": 30000, "cost": 0,
                     "desc": "Warranty fix. Metallic rattle under acceleration. TSB available."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1500, "major_cost": 3500,
                    "insurance": 6000,
                },
                "ratings": {"reliability": 4.5, "comfort": 5, "performance": 5,
                            "fuel_economy": 3, "offroad": 4.5, "resale": 5, "overall": 4.5},
            },
        },
        "Prado": {
            "J150 (2010-present)": {
                "year_start": 2010, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 4.0, "cylinders": 6, "fuel": "petrol", "hp": 271, "torque": 381},
                           {"size": 2.8, "cylinders": 4, "fuel": "diesel", "hp": 201, "torque": 500}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "4WD",
                "fuel_economy": 12.5, "fuel_tank": 150, "seats": 7,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Front brake rotor warping", "severity": "moderate",
                     "mileage": 60000, "cost": 2000,
                     "desc": "Steering wheel vibration under braking. Replace with aftermarket rotors."},
                    {"title": "KDSS suspension lean", "severity": "minor",
                     "mileage": 100000, "cost": 3000,
                     "desc": "Vehicle leans to one side. KDSS valve replacement needed."},
                    {"title": "Injector failure", "severity": "major",
                     "mileage": 150000, "cost": 8000,
                     "desc": "Diesel models only. Rough idle, white smoke. Replace all 4 injectors."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1000, "major_cost": 2500,
                    "insurance": 3500,
                },
                "ratings": {"reliability": 4.5, "comfort": 4, "performance": 3.5,
                            "fuel_economy": 2.5, "offroad": 4.5, "resale": 5, "overall": 4},
            },
        },
        "Camry": {
            "XV70 (2018-present)": {
                "year_start": 2018, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "petrol", "hp": 204, "torque": 243}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "FWD",
                "fuel_economy": 7.5, "fuel_tank": 60, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "CV axle boot tear", "severity": "minor",
                     "mileage": 80000, "cost": 800,
                     "desc": "Grease leaking from inner CV boot. Replace before joint damage."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 600, "major_cost": 1500,
                    "insurance": 2500,
                },
                "ratings": {"reliability": 5, "comfort": 4, "performance": 3,
                            "fuel_economy": 5, "offroad": 1, "resale": 4.5, "overall": 4.5},
            },
        },
        "Corolla": {
            "E210 (2019-present)": {
                "year_start": 2019, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 2.0, "cylinders": 4, "fuel": "petrol", "hp": 169, "torque": 200}],
                "transmission": [{"type": "automatic", "gears": 7}],
                "drivetrain": "FWD",
                "fuel_economy": 6.5, "fuel_tank": 50, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 500, "major_cost": 1200,
                    "insurance": 1800,
                },
                "ratings": {"reliability": 5, "comfort": 3, "performance": 2.5,
                            "fuel_economy": 5, "offroad": 1, "resale": 4, "overall": 4},
            },
        },
        "Hilux": {
            "AN120 (2016-present)": {
                "year_start": 2016, "year_end": None,
                "body_type": "pickup",
                "engine": [{"size": 2.8, "cylinders": 4, "fuel": "diesel", "hp": 201, "torque": 500}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "4WD",
                "fuel_economy": 9.0, "fuel_tank": 80, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Leaf spring sag", "severity": "moderate",
                     "mileage": 100000, "cost": 3000,
                     "desc": "Rear sags under load. Upgrade to heavy-duty leaf pack."},
                    {"title": "Turbo oil leak", "severity": "moderate",
                     "mileage": 120000, "cost": 2500,
                     "desc": "Oil weeping from turbo oil feed line."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 800, "major_cost": 2000,
                    "insurance": 2500,
                },
                "ratings": {"reliability": 4.5, "comfort": 2.5, "performance": 3.5,
                            "fuel_economy": 3.5, "offroad": 5, "resale": 4.5, "overall": 4},
            },
        },
        "Fortuner": {
            "AN160 (2016-present)": {
                "year_start": 2016, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 2.8, "cylinders": 4, "fuel": "diesel", "hp": 201, "torque": 500}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "4WD",
                "fuel_economy": 8.5, "fuel_tank": 80, "seats": 7,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Rear suspension harshness", "severity": "minor",
                     "mileage": 50000, "cost": 1500,
                     "desc": "Harsh ride over bumps. Aftermarket shocks improve comfort significantly."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 900, "major_cost": 2200,
                    "insurance": 3000,
                },
                "ratings": {"reliability": 4.5, "comfort": 3, "performance": 3.5,
                            "fuel_economy": 3.5, "offroad": 4.5, "resale": 4.5, "overall": 4},
            },
        },
        "RAV4": {
            "XA50 (2019-present)": {
                "year_start": 2019, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "hybrid", "hp": 219, "torque": 221}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "AWD",
                "fuel_economy": 5.5, "fuel_tank": 55, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Hybrid battery degradation", "severity": "moderate",
                     "mileage": 150000, "cost": 8000,
                     "desc": "Reduced EV range in GCC heat. Battery replacement at 8-10 years."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 700, "major_cost": 1800,
                    "insurance": 2800,
                },
                "ratings": {"reliability": 5, "comfort": 4, "performance": 3.5,
                            "fuel_economy": 5, "offroad": 2, "resale": 4, "overall": 4.5},
            },
        },
    },
    "Nissan": {
        "Patrol": {
            "Y62 (2010-present)": {
                "year_start": 2010, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 5.6, "cylinders": 8, "fuel": "petrol", "hp": 400, "torque": 560}],
                "transmission": [{"type": "automatic", "gears": 7}],
                "drivetrain": "4WD",
                "fuel_economy": 14.5, "fuel_tank": 140, "seats": 8,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Transmission shudder", "severity": "major",
                     "mileage": 120000, "cost": 12000,
                     "desc": "Torque converter shudder at 40-60 km/h. Full transmission rebuild often needed."},
                    {"title": "Catalytic converter failure", "severity": "major",
                     "mileage": 150000, "cost": 8000,
                     "desc": "Check engine light, power loss. GCC fuel quality contributes."},
                    {"title": "Suspension bushing wear", "severity": "moderate",
                     "mileage": 80000, "cost": 3000,
                     "desc": "Clunking over bumps. Replace front lower control arm bushings."},
                    {"title": "AC compressor failure", "severity": "moderate",
                     "mileage": 100000, "cost": 4000,
                     "desc": "Common in GCC heat. Compressor clutch burns out."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1300, "major_cost": 3000,
                    "insurance": 5000,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 4.5,
                            "fuel_economy": 1.5, "offroad": 4.5, "resale": 4.5, "overall": 4},
            },
        },
        "Sunny": {
            "B18 (2020-present)": {
                "year_start": 2020, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 1.6, "cylinders": 4, "fuel": "petrol", "hp": 118, "torque": 149}],
                "transmission": [{"type": "automatic", "gears": 5}],
                "drivetrain": "FWD",
                "fuel_economy": 6.0, "fuel_tank": 41, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "CVT transmission whine", "severity": "minor",
                     "mileage": 80000, "cost": 5000,
                     "desc": "Whining noise from CVT. Fluid change every 40K km critical in GCC."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 450, "major_cost": 1100,
                    "insurance": 1500,
                },
                "ratings": {"reliability": 4, "comfort": 3, "performance": 2,
                            "fuel_economy": 5, "offroad": 1, "resale": 3, "overall": 3.5},
            },
        },
        "Altima": {
            "L34 (2019-present)": {
                "year_start": 2019, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "petrol", "hp": 188, "torque": 244}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "FWD",
                "fuel_economy": 7.0, "fuel_tank": 62, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "CVT judder on takeoff", "severity": "moderate",
                     "mileage": 70000, "cost": 6000,
                     "desc": "CVT belt slip at low speeds. Regular fluid changes prevent."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 550, "major_cost": 1400,
                    "insurance": 2200,
                },
                "ratings": {"reliability": 3.5, "comfort": 4, "performance": 3,
                            "fuel_economy": 4.5, "offroad": 1, "resale": 3.5, "overall": 3.5},
            },
        },
    },
    "Honda": {
        "Accord": {
            "10th Gen (2018-present)": {
                "year_start": 2018, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 1.5, "cylinders": 4, "fuel": "petrol", "hp": 192, "torque": 260}],
                "transmission": [{"type": "automatic", "gears": 7}],
                "drivetrain": "FWD",
                "fuel_economy": 7.0, "fuel_tank": 56, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Oil dilution in cold starts", "severity": "minor",
                     "mileage": 20000, "cost": 0,
                     "desc": "Not common in GCC climate. Software update available."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 600, "major_cost": 1500,
                    "insurance": 2200,
                },
                "ratings": {"reliability": 4.5, "comfort": 4, "performance": 3.5,
                            "fuel_economy": 4.5, "offroad": 1, "resale": 3.5, "overall": 4},
            },
        },
        "Civic": {
            "11th Gen (2022-present)": {
                "year_start": 2022, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 2.0, "cylinders": 4, "fuel": "petrol", "hp": 158, "torque": 187}],
                "transmission": [{"type": "automatic", "gears": 7}],
                "drivetrain": "FWD",
                "fuel_economy": 6.5, "fuel_tank": 47, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 500, "major_cost": 1200,
                    "insurance": 1800,
                },
                "ratings": {"reliability": 5, "comfort": 3.5, "performance": 3,
                            "fuel_economy": 5, "offroad": 1, "resale": 4, "overall": 4},
            },
        },
        "CR-V": {
            "5th Gen (2017-2022)": {
                "year_start": 2017, "year_end": 2022,
                "body_type": "SUV",
                "engine": [{"size": 1.5, "cylinders": 4, "fuel": "petrol", "hp": 190, "torque": 243}],
                "transmission": [{"type": "automatic", "gears": 7}],
                "drivetrain": "AWD",
                "fuel_economy": 7.5, "fuel_tank": 57, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "AC compressor clutch failure", "severity": "moderate",
                     "mileage": 80000, "cost": 3500,
                     "desc": "AC stops blowing cold. Compressor clutch replacement required."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 650, "major_cost": 1600,
                    "insurance": 2600,
                },
                "ratings": {"reliability": 4.5, "comfort": 4, "performance": 3,
                            "fuel_economy": 4.5, "offroad": 2, "resale": 4, "overall": 4},
            },
        },
    },
    "Hyundai": {
        "Tucson": {
            "NX4 (2021-present)": {
                "year_start": 2021, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "petrol", "hp": 187, "torque": 241}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "AWD",
                "fuel_economy": 8.0, "fuel_tank": 54, "seats": 5,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [
                    {"title": "DCT hesitation", "severity": "minor",
                     "mileage": 30000, "cost": 0,
                     "desc": "Dual-clutch hesitation in stop-start traffic. Software update available."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 650, "major_cost": 1600,
                    "insurance": 2400,
                },
                "ratings": {"reliability": 4, "comfort": 4, "performance": 3,
                            "fuel_economy": 4, "offroad": 2, "resale": 3.5, "overall": 4},
            },
        },
        "Santa Fe": {
            "TM (2019-present)": {
                "year_start": 2019, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.5, "cylinders": 6, "fuel": "petrol", "hp": 277, "torque": 336}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "AWD",
                "fuel_economy": 10.0, "fuel_tank": 67, "seats": 7,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 750, "major_cost": 1800,
                    "insurance": 3000,
                },
                "ratings": {"reliability": 4.5, "comfort": 4.5, "performance": 3.5,
                            "fuel_economy": 3, "offroad": 2.5, "resale": 3.5, "overall": 4},
            },
        },
        "Elantra": {
            "CN7 (2021-present)": {
                "year_start": 2021, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 2.0, "cylinders": 4, "fuel": "petrol", "hp": 147, "torque": 179}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "FWD",
                "fuel_economy": 6.5, "fuel_tank": 47, "seats": 5,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 500, "major_cost": 1200,
                    "insurance": 1800,
                },
                "ratings": {"reliability": 4.5, "comfort": 3.5, "performance": 2.5,
                            "fuel_economy": 5, "offroad": 1, "resale": 3, "overall": 3.5},
            },
        },
    },
    "Kia": {
        "Sportage": {
            "NQ5 (2022-present)": {
                "year_start": 2022, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "petrol", "hp": 187, "torque": 241}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "AWD",
                "fuel_economy": 8.0, "fuel_tank": 54, "seats": 5,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 650, "major_cost": 1600,
                    "insurance": 2400,
                },
                "ratings": {"reliability": 4, "comfort": 4, "performance": 3,
                            "fuel_economy": 4, "offroad": 2, "resale": 3.5, "overall": 4},
            },
        },
        "Sorento": {
            "MQ4 (2021-present)": {
                "year_start": 2021, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.5, "cylinders": 6, "fuel": "petrol", "hp": 277, "torque": 336}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "AWD",
                "fuel_economy": 10.5, "fuel_tank": 67, "seats": 7,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 750, "major_cost": 1800,
                    "insurance": 3200,
                },
                "ratings": {"reliability": 4.5, "comfort": 4.5, "performance": 3.5,
                            "fuel_economy": 3, "offroad": 2, "resale": 3.5, "overall": 4},
            },
        },
    },
    "Mitsubishi": {
        "Pajero": {
            "V97 (2006-2021)": {
                "year_start": 2006, "year_end": 2021,
                "body_type": "SUV",
                "engine": [{"size": 3.8, "cylinders": 6, "fuel": "petrol", "hp": 247, "torque": 329}],
                "transmission": [{"type": "automatic", "gears": 5}],
                "drivetrain": "4WD",
                "fuel_economy": 13.5, "fuel_tank": 88, "seats": 7,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [
                    {"title": "Timing belt replacement", "severity": "major",
                     "mileage": 100000, "cost": 3000,
                     "desc": "Critical maintenance. Belt failure = engine damage. Replace every 100K km."},
                    {"title": "Intake manifold gasket leak", "severity": "moderate",
                     "mileage": 120000, "cost": 1500,
                     "desc": "Rough idle, vacuum leak. Plastic manifold warps in GCC heat."},
                    {"title": "Transfer case chain stretch", "severity": "moderate",
                     "mileage": 180000, "cost": 5000,
                     "desc": "Clunking when shifting from 2H to 4H."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 900, "major_cost": 2200,
                    "insurance": 3000,
                },
                "ratings": {"reliability": 4, "comfort": 3, "performance": 3,
                            "fuel_economy": 2, "offroad": 4.5, "resale": 3.5, "overall": 3.5},
            },
        },
        "Lancer": {
            "CY (2007-2017)": {
                "year_start": 2007, "year_end": 2017,
                "body_type": "sedan",
                "engine": [{"size": 2.0, "cylinders": 4, "fuel": "petrol", "hp": 150, "torque": 197}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "FWD",
                "fuel_economy": 7.5, "fuel_tank": 59, "seats": 5,
                "warranty_years": 5, "warranty_km": 100000,
                "issues": [
                    {"title": "CVT transmission failure", "severity": "major",
                     "mileage": 120000, "cost": 8000,
                     "desc": "Complete CVT failure. Fluid changes every 40K km are critical."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 500, "major_cost": 1300,
                    "insurance": 1800,
                },
                "ratings": {"reliability": 3.5, "comfort": 3, "performance": 2.5,
                            "fuel_economy": 4, "offroad": 1, "resale": 2.5, "overall": 3},
            },
        },
    },
    "Mazda": {
        "CX-5": {
            "KF (2017-present)": {
                "year_start": 2017, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "petrol", "hp": 187, "torque": 252}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "AWD",
                "fuel_economy": 7.5, "fuel_tank": 58, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Infotainment screen delamination", "severity": "minor",
                     "mileage": 50000, "cost": 2000,
                     "desc": "Screen bubbles in GCC heat. Replace screen digitizer."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 700, "major_cost": 1700,
                    "insurance": 2400,
                },
                "ratings": {"reliability": 4.5, "comfort": 4, "performance": 3.5,
                            "fuel_economy": 4, "offroad": 2, "resale": 3.5, "overall": 4},
            },
        },
        "CX-9": {
            "TC (2016-present)": {
                "year_start": 2016, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 2.5, "cylinders": 4, "fuel": "petrol", "hp": 250, "torque": 420}],
                "transmission": [{"type": "automatic", "gears": 6}],
                "drivetrain": "AWD",
                "fuel_economy": 9.5, "fuel_tank": 74, "seats": 7,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Turbo oil consumption", "severity": "moderate",
                     "mileage": 80000, "cost": 2000,
                     "desc": "Excessive oil consumption. Check oil level every 1000 km."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 800, "major_cost": 2000,
                    "insurance": 3000,
                },
                "ratings": {"reliability": 4, "comfort": 4.5, "performance": 4,
                            "fuel_economy": 3.5, "offroad": 2, "resale": 3.5, "overall": 4},
            },
        },
    },
    "Ford": {
        "Explorer": {
            "U625 (2020-present)": {
                "year_start": 2020, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.0, "cylinders": 6, "fuel": "petrol", "hp": 365, "torque": 515}],
                "transmission": [{"type": "automatic", "gears": 10}],
                "drivetrain": "AWD",
                "fuel_economy": 11.0, "fuel_tank": 73, "seats": 7,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Transmission harsh shifting", "severity": "moderate",
                     "mileage": 40000, "cost": 0,
                     "desc": "10-speed harsh 1-2-3 shift. Software TSB fixes most cases."},
                    {"title": "Water pump failure", "severity": "major",
                     "mileage": 100000, "cost": 6000,
                     "desc": "Internal water pump leaks into oil. Catastrophic if not caught early."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 800, "major_cost": 2000,
                    "insurance": 3800,
                },
                "ratings": {"reliability": 3.5, "comfort": 4.5, "performance": 4.5,
                            "fuel_economy": 2.5, "offroad": 3, "resale": 3, "overall": 3.5},
            },
        },
        "Expedition": {
            "U553 (2018-present)": {
                "year_start": 2018, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.5, "cylinders": 6, "fuel": "petrol", "hp": 375, "torque": 637}],
                "transmission": [{"type": "automatic", "gears": 10}],
                "drivetrain": "4WD",
                "fuel_economy": 12.5, "fuel_tank": 106, "seats": 8,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Cam phaser rattle", "severity": "moderate",
                     "mileage": 60000, "cost": 4000,
                     "desc": "Cold start rattle from 3.5L EcoBoost. Phaser replacement required."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 900, "major_cost": 2200,
                    "insurance": 4500,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 4.5,
                            "fuel_economy": 2, "offroad": 3.5, "resale": 3, "overall": 3.5},
            },
        },
    },
    "Chevrolet": {
        "Tahoe": {
            "GMT1YC (2021-present)": {
                "year_start": 2021, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 5.3, "cylinders": 8, "fuel": "petrol", "hp": 355, "torque": 519}],
                "transmission": [{"type": "automatic", "gears": 10}],
                "drivetrain": "4WD",
                "fuel_economy": 13.0, "fuel_tank": 106, "seats": 8,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "AFM lifter failure", "severity": "major",
                     "mileage": 80000, "cost": 9000,
                     "desc": "Active Fuel Management lifters collapse. Delete AFM for reliability in GCC."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 950, "major_cost": 2400,
                    "insurance": 5000,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 4,
                            "fuel_economy": 2, "offroad": 3, "resale": 3.5, "overall": 3.5},
            },
        },
    },
    "BMW": {
        "5 Series": {
            "G30 (2017-2023)": {
                "year_start": 2017, "year_end": 2023,
                "body_type": "sedan",
                "engine": [{"size": 2.0, "cylinders": 4, "fuel": "petrol", "hp": 252, "torque": 350}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "RWD",
                "fuel_economy": 6.5, "fuel_tank": 68, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Valve cover gasket leak", "severity": "moderate",
                     "mileage": 80000, "cost": 2500,
                     "desc": "Oil leaking onto exhaust manifold. Replace gasket + cover."},
                    {"title": "Coolant expansion tank crack", "severity": "moderate",
                     "mileage": 60000, "cost": 1200,
                     "desc": "Plastic tank cracks in GCC heat. Replace with updated part."},
                ],
                "maintenance": {
                    "interval_km": 12000,
                    "minor_cost": 1500, "major_cost": 3500,
                    "insurance": 5000,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 4,
                            "fuel_economy": 4.5, "offroad": 1, "resale": 2.5, "overall": 4},
            },
        },
        "X5": {
            "G05 (2019-present)": {
                "year_start": 2019, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.0, "cylinders": 6, "fuel": "petrol", "hp": 335, "torque": 450}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "AWD",
                "fuel_economy": 9.0, "fuel_tank": 83, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Air suspension failure", "severity": "major",
                     "mileage": 80000, "cost": 8000,
                     "desc": "Rear air springs leak. Replace both air springs + compressor."},
                    {"title": "Oil filter housing gasket", "severity": "moderate",
                     "mileage": 70000, "cost": 2500,
                     "desc": "Oil leak from filter housing. B58 engine common issue."},
                ],
                "maintenance": {
                    "interval_km": 12000,
                    "minor_cost": 1800, "major_cost": 4000,
                    "insurance": 6000,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 4.5,
                            "fuel_economy": 3.5, "offroad": 3, "resale": 2.5, "overall": 4},
            },
        },
    },
    "Mercedes-Benz": {
        "E-Class": {
            "W213 (2016-2023)": {
                "year_start": 2016, "year_end": 2023,
                "body_type": "sedan",
                "engine": [{"size": 2.0, "cylinders": 4, "fuel": "petrol", "hp": 255, "torque": 370}],
                "transmission": [{"type": "automatic", "gears": 9}],
                "drivetrain": "RWD",
                "fuel_economy": 7.0, "fuel_tank": 66, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Electric steering rack failure", "severity": "major",
                     "mileage": 100000, "cost": 10000,
                     "desc": "Power steering failure. Complete rack replacement."},
                    {"title": "Engine mount collapse", "severity": "moderate",
                     "mileage": 60000, "cost": 3000,
                     "desc": "Excessive vibration at idle. Replace engine + transmission mounts."},
                ],
                "maintenance": {
                    "interval_km": 15000,
                    "minor_cost": 1800, "major_cost": 4000,
                    "insurance": 5500,
                },
                "ratings": {"reliability": 3, "comfort": 5, "performance": 4,
                            "fuel_economy": 4, "offroad": 1, "resale": 2.5, "overall": 3.5},
            },
        },
        "S-Class": {
            "W223 (2021-present)": {
                "year_start": 2021, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 3.0, "cylinders": 6, "fuel": "petrol", "hp": 429, "torque": 520}],
                "transmission": [{"type": "automatic", "gears": 9}],
                "drivetrain": "AWD",
                "fuel_economy": 9.0, "fuel_tank": 76, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "MBUX system glitches", "severity": "minor",
                     "mileage": 0, "cost": 0,
                     "desc": "Screen freezes, reboots. Software updates resolve most issues."},
                ],
                "maintenance": {
                    "interval_km": 15000,
                    "minor_cost": 2500, "major_cost": 6000,
                    "insurance": 10000,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 5,
                            "fuel_economy": 3, "offroad": 1, "resale": 2, "overall": 4},
            },
        },
    },
    "Lexus": {
        "LX": {
            "J310 (2022-present)": {
                "year_start": 2022, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.5, "cylinders": 6, "fuel": "petrol", "hp": 409, "torque": 650}],
                "transmission": [{"type": "automatic", "gears": 10}],
                "drivetrain": "4WD",
                "fuel_economy": 12.0, "fuel_tank": 110, "seats": 7,
                "warranty_years": 4, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1800, "major_cost": 4000,
                    "insurance": 8000,
                },
                "ratings": {"reliability": 5, "comfort": 5, "performance": 4.5,
                            "fuel_economy": 2.5, "offroad": 4.5, "resale": 5, "overall": 4.5},
            },
        },
        "ES": {
            "XZ10 (2019-present)": {
                "year_start": 2019, "year_end": None,
                "body_type": "sedan",
                "engine": [{"size": 3.5, "cylinders": 6, "fuel": "petrol", "hp": 302, "torque": 362}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "FWD",
                "fuel_economy": 8.5, "fuel_tank": 60, "seats": 5,
                "warranty_years": 4, "warranty_km": 100000,
                "issues": [],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1000, "major_cost": 2500,
                    "insurance": 4000,
                },
                "ratings": {"reliability": 5, "comfort": 5, "performance": 4,
                            "fuel_economy": 4, "offroad": 1, "resale": 4, "overall": 4.5},
            },
        },
    },
    "GMC": {
        "Yukon": {
            "GMT1YC (2021-present)": {
                "year_start": 2021, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 5.3, "cylinders": 8, "fuel": "petrol", "hp": 355, "torque": 519}],
                "transmission": [{"type": "automatic", "gears": 10}],
                "drivetrain": "4WD",
                "fuel_economy": 13.0, "fuel_tank": 106, "seats": 8,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "AFM lifter failure", "severity": "major",
                     "mileage": 80000, "cost": 9000,
                     "desc": "Same GM 5.3L AFM issue as Tahoe/Suburban. Delete AFM for reliability."},
                ],
                "maintenance": {
                    "interval_km": 10000,
                    "minor_cost": 1000, "major_cost": 2500,
                    "insurance": 5000,
                },
                "ratings": {"reliability": 3.5, "comfort": 5, "performance": 4,
                            "fuel_economy": 2, "offroad": 3, "resale": 3.5, "overall": 3.5},
            },
        },
    },
    "Land Rover": {
        "Range Rover": {
            "L460 (2022-present)": {
                "year_start": 2022, "year_end": None,
                "body_type": "SUV",
                "engine": [{"size": 3.0, "cylinders": 6, "fuel": "petrol", "hp": 395, "torque": 550}],
                "transmission": [{"type": "automatic", "gears": 8}],
                "drivetrain": "4WD",
                "fuel_economy": 11.0, "fuel_tank": 90, "seats": 5,
                "warranty_years": 3, "warranty_km": 100000,
                "issues": [
                    {"title": "Air suspension fault", "severity": "major",
                     "mileage": 60000, "cost": 10000,
                     "desc": "Suspension drops to bump stops. Compressor or strut failure."},
                    {"title": "Infotainment black screen", "severity": "minor",
                     "mileage": 20000, "cost": 0,
                     "desc": "Pivi Pro screen goes black. Hold power button 30 seconds to reset."},
                    {"title": "Coolant pipe failure", "severity": "major",
                     "mileage": 50000, "cost": 5000,
                     "desc": "Plastic coolant pipes crack. Replace with updated metal pipes."},
                ],
                "maintenance": {
                    "interval_km": 15000,
                    "minor_cost": 2500, "major_cost": 6000,
                    "insurance": 9000,
                },
                "ratings": {"reliability": 2.5, "comfort": 5, "performance": 5,
                            "fuel_economy": 2.5, "offroad": 5, "resale": 2.5, "overall": 3.5},
            },
        },
    },
}

# Depreciation curves (residual % after N years, from MSRP)
DEPRECIATION = {
    ("Toyota", "Land Cruiser"): {1: 0.90, 2: 0.85, 3: 0.78, 5: 0.65, 7: 0.52, 10: 0.35},
    ("Toyota", "Prado"):       {1: 0.88, 2: 0.83, 3: 0.75, 5: 0.62, 7: 0.50, 10: 0.33},
    ("Toyota", "Camry"):        {1: 0.85, 2: 0.78, 3: 0.70, 5: 0.55, 7: 0.42, 10: 0.28},
    ("Toyota", "Corolla"):      {1: 0.84, 2: 0.77, 3: 0.68, 5: 0.53, 7: 0.40, 10: 0.26},
    ("Toyota", "Hilux"):        {1: 0.87, 2: 0.80, 3: 0.73, 5: 0.60, 7: 0.48, 10: 0.32},
    ("Toyota", "Fortuner"):     {1: 0.86, 2: 0.79, 3: 0.72, 5: 0.58, 7: 0.46, 10: 0.30},
    ("Toyota", "RAV4"):         {1: 0.85, 2: 0.78, 3: 0.70, 5: 0.55, 7: 0.42, 10: 0.28},
    ("Nissan", "Patrol"):       {1: 0.88, 2: 0.82, 3: 0.75, 5: 0.60, 7: 0.48, 10: 0.32},
    ("Nissan", "Sunny"):        {1: 0.80, 2: 0.72, 3: 0.63, 5: 0.48, 7: 0.35, 10: 0.22},
    ("Nissan", "Altima"):       {1: 0.78, 2: 0.70, 3: 0.60, 5: 0.45, 7: 0.32, 10: 0.20},
    ("Honda", "Accord"):        {1: 0.82, 2: 0.75, 3: 0.67, 5: 0.52, 7: 0.40, 10: 0.25},
    ("Honda", "Civic"):         {1: 0.83, 2: 0.76, 3: 0.68, 5: 0.53, 7: 0.41, 10: 0.26},
    ("Honda", "CR-V"):          {1: 0.84, 2: 0.77, 3: 0.69, 5: 0.54, 7: 0.42, 10: 0.27},
    ("Hyundai", "Tucson"):      {1: 0.78, 2: 0.70, 3: 0.60, 5: 0.45, 7: 0.33, 10: 0.20},
    ("Hyundai", "Santa Fe"):    {1: 0.76, 2: 0.68, 3: 0.58, 5: 0.43, 7: 0.31, 10: 0.19},
    ("Hyundai", "Elantra"):     {1: 0.77, 2: 0.69, 3: 0.59, 5: 0.44, 7: 0.32, 10: 0.19},
    ("Kia", "Sportage"):        {1: 0.78, 2: 0.70, 3: 0.60, 5: 0.45, 7: 0.33, 10: 0.20},
    ("Kia", "Sorento"):         {1: 0.76, 2: 0.68, 3: 0.58, 5: 0.43, 7: 0.31, 10: 0.19},
    ("Mitsubishi", "Pajero"):   {1: 0.82, 2: 0.74, 3: 0.65, 5: 0.50, 7: 0.38, 10: 0.25},
    ("Mitsubishi", "Lancer"):   {1: 0.75, 2: 0.66, 3: 0.55, 5: 0.40, 7: 0.28, 10: 0.16},
    ("Mazda", "CX-5"):          {1: 0.82, 2: 0.75, 3: 0.67, 5: 0.52, 7: 0.40, 10: 0.25},
    ("Mazda", "CX-9"):          {1: 0.80, 2: 0.73, 3: 0.65, 5: 0.50, 7: 0.38, 10: 0.23},
    ("Ford", "Explorer"):       {1: 0.75, 2: 0.66, 3: 0.55, 5: 0.40, 7: 0.28, 10: 0.16},
    ("Ford", "Expedition"):     {1: 0.76, 2: 0.67, 3: 0.56, 5: 0.41, 7: 0.29, 10: 0.17},
    ("Chevrolet", "Tahoe"):     {1: 0.78, 2: 0.70, 3: 0.60, 5: 0.45, 7: 0.33, 10: 0.20},
    ("BMW", "5 Series"):        {1: 0.70, 2: 0.60, 3: 0.50, 5: 0.35, 7: 0.23, 10: 0.12},
    ("BMW", "X5"):              {1: 0.72, 2: 0.62, 3: 0.52, 5: 0.37, 7: 0.25, 10: 0.14},
    ("Mercedes-Benz", "E-Class"):{1: 0.70, 2: 0.60, 3: 0.50, 5: 0.35, 7: 0.23, 10: 0.12},
    ("Mercedes-Benz", "S-Class"):{1: 0.65, 2: 0.55, 3: 0.45, 5: 0.30, 7: 0.18, 10: 0.08},
    ("Lexus", "LX"):            {1: 0.90, 2: 0.85, 3: 0.78, 5: 0.65, 7: 0.52, 10: 0.35},
    ("Lexus", "ES"):            {1: 0.84, 2: 0.77, 3: 0.68, 5: 0.53, 7: 0.41, 10: 0.26},
    ("GMC", "Yukon"):           {1: 0.78, 2: 0.70, 3: 0.60, 5: 0.45, 7: 0.33, 10: 0.20},
    ("Land Rover", "Range Rover"):{1: 0.72, 2: 0.62, 3: 0.52, 5: 0.37, 7: 0.25, 10: 0.14},
}


async def seed_knowledge_base(session: AsyncSession) -> dict:
    """Seed the knowledge base with top GCC car models. Returns counts per table."""
    counts = {"specs": 0, "issues": 0, "maintenance": 0, "depreciation": 0, "ratings": 0}

    for make, models in MODELS.items():
        for model_name, generations in models.items():
            for gen_name, gen_data in generations.items():
                # CarSpecs
                spec = CarSpec(
                    make=make, model=model_name,
                    generation=gen_name,
                    year_start=gen_data["year_start"],
                    year_end=gen_data.get("year_end"),
                    body_type=gen_data.get("body_type"),
                    engine_options=gen_data.get("engine", []),
                    transmission_options=gen_data.get("transmission", []),
                    drivetrain=gen_data.get("drivetrain"),
                    fuel_economy_combined=gen_data.get("fuel_economy"),
                    fuel_tank_capacity=gen_data.get("fuel_tank"),
                    seating_capacity=gen_data.get("seats"),
                    warranty_years=gen_data.get("warranty_years"),
                    warranty_km=gen_data.get("warranty_km"),
                    source="curated",
                )
                session.add(spec)
                counts["specs"] += 1

                # CarIssues
                for issue in gen_data.get("issues", []):
                    car_issue = CarIssue(
                        make=make, model=model_name,
                        generation=gen_name,
                        year_start=gen_data["year_start"],
                        year_end=gen_data.get("year_end"),
                        issue_title=issue["title"],
                        issue_description=issue.get("desc", ""),
                        severity=issue["severity"],
                        typical_mileage_km=issue.get("mileage"),
                        repair_cost_estimate=issue.get("cost"),
                        source="curated",
                        confirmed=True,
                        confirmed_by_count=1,
                    )
                    session.add(car_issue)
                    counts["issues"] += 1

                # MaintenanceCost
                m = gen_data.get("maintenance", {})
                if m:
                    mc = MaintenanceCost(
                        make=make, model=model_name,
                        generation=gen_name,
                        service_interval_km=m.get("interval_km"),
                        minor_service_cost=m.get("minor_cost"),
                        major_service_cost=m.get("major_cost"),
                        annual_insurance_estimate=m.get("insurance"),
                        source="curated",
                    )
                    session.add(mc)
                    counts["maintenance"] += 1

                # DepreciationCurve
                key = (make, model_name)
                if key in DEPRECIATION:
                    dc = DepreciationCurve(
                        make=make, model=model_name,
                        generation=gen_name,
                        residual_pct_year=DEPRECIATION[key],
                        computed_from_rows=0,
                    )
                    session.add(dc)
                    counts["depreciation"] += 1

                # ModelRating
                r = gen_data.get("ratings", {})
                if r:
                    mr = ModelRating(
                        make=make, model=model_name,
                        generation=gen_name,
                        reliability=r.get("reliability"),
                        comfort=r.get("comfort"),
                        performance=r.get("performance"),
                        fuel_economy=r.get("fuel_economy"),
                        offroad_capability=r.get("offroad", 1),
                        resale_value=r.get("resale"),
                        overall=r.get("overall"),
                        rating_count=1,
                        source="curated",
                    )
                    session.add(mr)
                    counts["ratings"] += 1

    await session.commit()
    logger.info("knowledge_base_seeded", **counts)
    return counts


async def main():
    """Seed the knowledge base. Connects to configured database."""
    async with async_session_factory() as session:
        counts = await seed_knowledge_base(session)
        print(f"Knowledge base seeded: {counts}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
