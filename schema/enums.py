"""Canonical enums for the vehicle listing schema."""

from enum import StrEnum


class Marketplace(StrEnum):
    DUBIZZLE_UAE = "dubizzle_uae"
    DUBIZZLE_KSA = "dubizzle_ksa"
    YALLAMOTOR = "yallamotor"
    HARAJ = "haraj"
    CARSWITCH = "carswitch"
    EMIRATES_AUCTION = "emirates_auction"
    OPENSOOQ = "opensooq"
    SYARAH = "syarah"
    MAZADAK = "mazadak"
    DUBICARS = "dubicars"


class FuelType(StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"
    PLUGIN_HYBRID = "plugin_hybrid"
    LPG = "lpg"
    OTHER = "other"


class Transmission(StrEnum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    CVT = "cvt"
    DCT = "dct"  # dual-clutch
    OTHER = "other"


class SellerType(StrEnum):
    PRIVATE = "private"
    DEALER = "dealer"
    AUCTION = "auction"
    CERTIFIED = "certified"


class BodyType(StrEnum):
    SUV = "suv"
    SEDAN = "sedan"
    HATCHBACK = "hatchback"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    WAGON = "wagon"
    PICKUP = "pickup"
    MINIVAN = "minivan"
    VAN = "van"
    TRUCK = "truck"
    OTHER = "other"


class DriveTrain(StrEnum):
    FWD = "fwd"
    RWD = "rwd"
    AWD = "awd"
    FOUR_WD = "4wd"


class Currency(StrEnum):
    AED = "AED"
    SAR = "SAR"
    KWD = "KWD"
    QAR = "QAR"
    BHD = "BHD"
    OMR = "OMR"
    USD = "USD"


class Country(StrEnum):
    AE = "AE"
    SA = "SA"
    KW = "KW"
    QA = "QA"
    BH = "BH"
    OM = "OM"


class Specification(StrEnum):
    GCC = "GCC"
    US = "US"
    JAPAN = "Japan"
    EUROPEAN = "European"
    OTHER = "Other"


class ListingStatus(StrEnum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    DELISTED = "delisted"
    PENDING = "pending"
