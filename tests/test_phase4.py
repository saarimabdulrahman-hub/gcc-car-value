"""Phase 4 tests — LLM explainer, VIN decoder, user accounts, recommendations."""
import pytest
from src.engine.llm_explainer import explain_valuation, ValuationContext
from src.engine.vin_decoder import validate_vin, decode_vin_basic
from src.models.user_account import UserAccount


# --- LLM Explainer ---

def test_template_explanation_generated():
    ctx = ValuationContext(
        make="Toyota", model="Land Cruiser", year=2018,
        mileage_km=80000, spec="GCC", city="Dubai",
        estimate=127350, price_low=123000, price_high=132000,
        confidence="medium", comp_count=16,
        adjustments=[
            {"reason": "mileage", "amount": -2125,
             "detail": "Fewer km than segment avg. Adjustment: -2125 AED"},
            {"reason": "city", "amount": 1725,
             "detail": "Dubai market adjustment: +1725 AED"},
        ],
        knowledge={
            "known_issues": ["Timing chain tensioner at 120K km"],
            "annual_maintenance_estimate": "4,500-6,500 AED",
            "market_liquidity": "18 days",
        },
    )
    explanation = explain_valuation(ctx)
    assert "127,350" in explanation
    assert "Toyota" in explanation
    assert "Land Cruiser" in explanation
    assert "16 comparable" in explanation


def test_explanation_with_knowledge():
    ctx = ValuationContext(
        make="Nissan", model="Patrol", year=2020,
        mileage_km=50000, spec="GCC", city="Dubai",
        estimate=180000, price_low=170000, price_high=190000,
        confidence="high", comp_count=35,
        adjustments=[], knowledge=None,
    )
    explanation = explain_valuation(ctx)
    assert "180,000" in explanation
    assert "35 comparable" in explanation
    assert "high confidence" in explanation


# --- VIN Decoder ---

def test_valid_vin():
    assert validate_vin("JTEHT05JX02401234")
    assert not validate_vin("TOO_SHORT")
    assert not validate_vin("JTEHT05JX0240I234")  # I is invalid
    assert not validate_vin("JTEHT05JX0240O234")  # O is invalid


def test_decode_vin_toyota():
    result = decode_vin_basic("JTEHT05JX02401234")
    assert result is not None
    assert result["valid"]
    assert "Toyota" in result["manufacturer"]
    assert "JTE" in result["wmi"]


def test_decode_vin_mercedes():
    result = decode_vin_basic("WDD2050421F123456")
    assert result is not None
    assert "Mercedes-Benz" in result["manufacturer"]


def test_decode_vin_invalid():
    assert decode_vin_basic("BAD_VIN") is None


# --- User Accounts ---

def test_hash_password():
    h, salt = UserAccount.hash_password("mypassword123")
    assert len(h) == 64  # SHA-256 hex = 64 chars
    assert len(salt) == 32  # 16 bytes hex = 32 chars


def test_verify_password():
    user = UserAccount()
    user.password_hash, user.password_salt = UserAccount.hash_password("secure_pass")
    assert user.verify_password("secure_pass")
    assert not user.verify_password("wrong_pass")


def test_password_different_salts():
    h1, s1 = UserAccount.hash_password("same_password")
    h2, s2 = UserAccount.hash_password("same_password")
    assert h1 != h2  # Different salts → different hashes
    assert s1 != s2


# --- Recommendation engine ---
# (requires DB — tested in integration)
