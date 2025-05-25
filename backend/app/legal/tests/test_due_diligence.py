"""
Unit tests for the due diligence service.
"""
import pytest
from app.legal.compliance.services.due_diligence import (
    run_due_diligence, fetch_ofac, fetch_un, fetch_eu, fetch_pep,
    calculate_risk_score, determine_status
)

@pytest.mark.asyncio
async def test_fetch_ofac_clean():
    """Test OFAC check with clean name."""
    result = await fetch_ofac("John Doe")
    assert result["status"] == "no_match"
    assert len(result["matches"]) == 0

@pytest.mark.asyncio
async def test_fetch_ofac_match():
    """Test OFAC check with sanctioned name."""
    result = await fetch_ofac("Osama bin Laden")
    assert result["status"] == "match"
    assert len(result["matches"]) > 0
    assert result["matches"][0]["score"] > 0.9

@pytest.mark.asyncio
async def test_fetch_un_clean():
    """Test UN check with clean name."""
    result = await fetch_un("John Doe")
    assert result["status"] == "no_match"
    assert len(result["matches"]) == 0

@pytest.mark.asyncio
async def test_fetch_un_match():
    """Test UN check with sanctioned name."""
    result = await fetch_un("Kim Jong Un")
    assert result["status"] == "match"
    assert len(result["matches"]) > 0
    assert result["matches"][0]["score"] > 0.9

@pytest.mark.asyncio
async def test_fetch_eu_clean():
    """Test EU check with clean name."""
    result = await fetch_eu("John Doe")
    assert result["status"] == "no_match"
    assert len(result["matches"]) == 0

@pytest.mark.asyncio
async def test_fetch_eu_match():
    """Test EU check with sanctioned name."""
    result = await fetch_eu("Vladimir Putin")
    assert result["status"] == "match"
    assert len(result["matches"]) > 0
    assert result["matches"][0]["score"] > 0.8

@pytest.mark.asyncio
async def test_fetch_pep_clean():
    """Test PEP check with clean name."""
    result = await fetch_pep("John Doe", "US")
    assert result["status"] == "no_match"
    assert len(result["matches"]) == 0

@pytest.mark.asyncio
async def test_fetch_pep_match():
    """Test PEP check with politically exposed person."""
    result = await fetch_pep("Joe Biden", "US")
    assert result["status"] == "match"
    assert len(result["matches"]) > 0
    assert result["matches"][0]["position"] == "President"

@pytest.mark.asyncio
async def test_calculate_risk_score():
    """Test risk score calculation."""
    clean_results = {
        "OFAC": {"status": "no_match"},
        "UN": {"status": "no_match"},
        "EU": {"status": "no_match"},
        "PEP": {"status": "no_match"}
    }
    risk_score = await calculate_risk_score(clean_results, "US")
    assert risk_score == 0.0
    
    sanctioned_results = {
        "OFAC": {"status": "match"},
        "UN": {"status": "no_match"},
        "EU": {"status": "no_match"},
        "PEP": {"status": "no_match"}
    }
    risk_score = await calculate_risk_score(sanctioned_results, "US")
    assert risk_score > 0.7
    
    pep_results = {
        "OFAC": {"status": "no_match"},
        "UN": {"status": "no_match"},
        "EU": {"status": "no_match"},
        "PEP": {"status": "match"}
    }
    risk_score = await calculate_risk_score(pep_results, "US")
    assert risk_score > 0.4
    
    risk_score = await calculate_risk_score(clean_results, "IR")
    assert risk_score > 0.2

@pytest.mark.asyncio
async def test_determine_status():
    """Test status determination based on risk score."""
    assert await determine_status(0.1) == "clean"
    assert await determine_status(0.5) == "flagged"
    assert await determine_status(0.9) == "blocked"

@pytest.mark.asyncio
async def test_run_due_diligence_clean():
    """Test due diligence with clean client."""
    result = await run_due_diligence("John Doe", "A123456", "US")
    assert "results" in result
    assert "OFAC" in result["results"]
    assert "UN" in result["results"]
    assert "EU" in result["results"]
    assert "PEP" in result["results"]
    assert result["status"] == "clean"
    assert result["risk_score"] == 0.0

@pytest.mark.asyncio
async def test_run_due_diligence_sanctioned():
    """Test due diligence with sanctioned client."""
    result = await run_due_diligence("Osama bin Laden", "X999999", "AF")
    assert result["status"] in ["flagged", "blocked"]
    assert result["risk_score"] > 0.7

@pytest.mark.asyncio
async def test_run_due_diligence_pep():
    """Test due diligence with politically exposed person."""
    result = await run_due_diligence("Joe Biden", "US123456", "US")
    assert result["status"] in ["flagged", "clean"]
    assert result["risk_score"] > 0.0
