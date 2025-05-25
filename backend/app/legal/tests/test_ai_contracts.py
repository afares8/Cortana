"""
Unit tests for the AI contract analysis functions.
"""
import pytest
from app.legal.contracts.ai_contracts import (
    extract_clauses, calculate_risk_score, detect_anomalies,
    suggest_rewrite_clauses, simulate_legal_impact
)

SAMPLE_CONTRACT = """
CONFIDENTIALITY AGREEMENT

This Confidentiality Agreement (the "Agreement") is entered into as of January 1, 2023 (the "Effective Date") by and between Company A, a corporation organized under the laws of Delaware ("Discloser"), and Company B, a corporation organized under the laws of California ("Recipient").

1. CONFIDENTIAL INFORMATION
"Confidential Information" means any information disclosed by Discloser to Recipient, either directly or indirectly, in writing, orally or by inspection of tangible objects, which is designated as "Confidential," "Proprietary" or some similar designation.

2. NON-DISCLOSURE
Recipient shall not disclose any Confidential Information to third parties and shall use the Confidential Information only for purposes of evaluating and pursuing a business relationship with Discloser.

3. TERM
This Agreement shall terminate five (5) years from the Effective Date.

4. GOVERNING LAW
This Agreement shall be governed by the laws of the State of New York.
"""

SAMPLE_CLAUSE = """
5. LIMITATION OF LIABILITY
IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES, HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SERVICE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

@pytest.mark.asyncio
async def test_extract_clauses():
    """Test extraction of clauses from contract text."""
    clauses = await extract_clauses(SAMPLE_CONTRACT)
    assert isinstance(clauses, list)
    assert len(clauses) > 0
    found_confidentiality = False
    found_non_disclosure = False
    found_term = False
    found_governing_law = False
    
    for clause in clauses:
        if "confidential" in clause.lower():
            found_confidentiality = True
        if "non-disclosure" in clause.lower() or "disclosure" in clause.lower():
            found_non_disclosure = True
        if "term" in clause.lower():
            found_term = True
        if "governing law" in clause.lower():
            found_governing_law = True
    
    assert found_confidentiality or found_non_disclosure or found_term or found_governing_law

@pytest.mark.asyncio
async def test_calculate_risk_score():
    """Test calculation of risk score for contract text."""
    risk_score = await calculate_risk_score(SAMPLE_CONTRACT)
    assert isinstance(risk_score, float)
    assert 0.0 <= risk_score <= 1.0

@pytest.mark.asyncio
async def test_detect_anomalies():
    """Test detection of anomalies in contract text."""
    anomalies = await detect_anomalies(SAMPLE_CONTRACT)
    assert isinstance(anomalies, list)
    
    problematic_contract = SAMPLE_CONTRACT + "\n\n" + SAMPLE_CLAUSE
    anomalies_with_problem = await detect_anomalies(problematic_contract)
    assert isinstance(anomalies_with_problem, list)

@pytest.mark.asyncio
async def test_suggest_rewrite_clauses():
    """Test suggestion of rewrites for problematic clauses."""
    rewrites = await suggest_rewrite_clauses(SAMPLE_CONTRACT + "\n\n" + SAMPLE_CLAUSE)
    assert isinstance(rewrites, dict)

@pytest.mark.asyncio
async def test_simulate_legal_impact():
    """Test simulation of legal impact for a specific clause."""
    impact = await simulate_legal_impact(SAMPLE_CLAUSE)
    assert isinstance(impact, str)
    assert len(impact) > 0
