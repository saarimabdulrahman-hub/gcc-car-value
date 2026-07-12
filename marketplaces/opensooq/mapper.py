"""OpenSooq mapper — country-aware mapping to CanonicalListing."""

from schema.listing import CanonicalListing
from schema.vehicle import Vehicle
from schema.pricing import Pricing
from schema.location import Location
from schema.seller import Seller
from schema.images import Images
from marketplaces.opensooq.config import OpenSooqConfig


class OpenSooqMapper:
    def __init__(self, config: OpenSooqConfig): self.config = config

    def map_to_canonical(self, data: dict, url: str = "", listing_id: str = "") -> CanonicalListing:
        country = self.config.country
        currency = data.get("currency", self.config.currency)
        return CanonicalListing(
            marketplace=f"opensooq_{country.lower()}",
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
            pricing=Pricing(amount=data.get("price", 0.0), currency=currency),
            location=Location(country=country, city=data.get("location", data.get("city", ""))),
            seller=Seller(seller_name=data.get("seller_name", ""), seller_type=data.get("seller_type", "private")),
            images=Images(cover_image=data.get("image", ""), gallery=data.get("images", []),
                         image_count=len(data.get("images", []))),
            metadata={"source": f"opensooq_{country.lower()}", "country": country,
                     "extracted_title": data.get("title", ""), "extracted_description": data.get("description", "")},
        )
