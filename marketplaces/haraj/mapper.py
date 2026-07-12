"""Haraj mapper — converts extracted fields to CanonicalListing."""

from schema.listing import CanonicalListing
from schema.vehicle import Vehicle
from schema.pricing import Pricing
from schema.location import Location
from schema.seller import Seller
from schema.images import Images
from marketplaces.haraj.constants import MARKETPLACE_NAME, MARKETPLACE_COUNTRY, MARKETPLACE_CURRENCY


class HarajMapper:
    def map_to_canonical(self, data: dict, url: str = "", listing_id: str = "") -> CanonicalListing:
        return CanonicalListing(
            marketplace=MARKETPLACE_NAME,
            marketplace_listing_id=data.get("listing_id", listing_id),
            listing_url=url or data.get("url", ""),
            status="active",
            vehicle=Vehicle(
                make=data.get("make", ""), model=data.get("model", ""),
                year=data.get("year", 0), mileage_km=data.get("mileage_km", 0),
                body_type=data.get("body_type", ""), fuel_type=data.get("fuel_type", ""),
                transmission=data.get("transmission", ""), specification=data.get("spec", ""),
                color=data.get("color", ""),
            ),
            pricing=Pricing(amount=data.get("price", 0.0), currency= data.get("currency", MARKETPLACE_CURRENCY)),
            location=Location(country=data.get("country", MARKETPLACE_COUNTRY),
                            city=data.get("location", data.get("city", ""))),
            seller=Seller(seller_name=data.get("seller_name", ""), seller_type=data.get("seller_type", "private")),
            images=Images(cover_image=data.get("image", ""), gallery=data.get("images", []),
                         image_count=len(data.get("images", []))),
            metadata={"source": MARKETPLACE_NAME, "extracted_title": data.get("title", ""),
                     "extracted_description": data.get("description", "")},
        )
