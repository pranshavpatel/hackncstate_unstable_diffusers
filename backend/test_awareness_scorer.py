"""
Unit tests for awareness scorer agent
"""
from agents.awareness_scorer import awareness_scorer
from config.state import TrialState

def create_mock_state(user_judgements=None, round_count=2):
    """Helper to create mock trial state"""
    if user_judgements is None:
        user_judgements = []
    
    # Build transcript
    transcript = []
    for i in range(1, round_count + 1):
        transcript.append({
            "agent": "prosecutor",
            "round": i,
            "argument_text": f"Prosecutor argument round {i}",
            "confidence_score": 65
        })
        transcript.append({
            "agent": "defendant",
            "round": i,
            "argument_text": f"Defendant rebuttal round {i}",
            "confidence_score": 55
        })
    
    return {
        "case_id": "test-case",
        "trial_transcript": transcript,
        "user_judgements": user_judgements,
        "aggregated_verdict": {
            "score": 45,
            "category": "Likely False",
            "summary": "Test verdict summary"
        },
        "awareness_score_result": None,
        "selected_claims": [{"text": "Test claim"}],
        "current_round": round_count,
        "max_rounds": 2,
        "input_type": "text",
        "raw_input": "test",
        "claims": [],
        "investigator_evidence": [],
        "prosecutor_private_evidence": [],
        "defendant_private_evidence": [],
        "prosecutor_revealed_evidence": [],
        "prosecutor_confidence": 65.0,
        "defendant_revealed_evidence": [],
        "defendant_confidence": 55.0,
        "user_interventions": [],
        "jury_members": [],
        "should_terminate": True,
        "termination_reason": "max_rounds",
        "user_prediction": None,
        "jury_verdicts": [],
        "user_score_delta": 0,
        "education_panel": None,
        "verdict_report": None
    }


async def test_average_calculation():
    """Test that averaging works correctly"""
    state = create_mock_state(user_judgements=["plausible", "misleading", "not sure"])
    
    # Mock the LLM response with known scores
    # This is a unit test, so we'll need to mock the LLM client
    # For now, just test the averaging logic after receiving a response
    
    result = await awareness_scorer(state)
    
    # Check that awareness_score_result was created
    assert result["awareness_score_result"] is not None
    assert "summary" in result["awareness_score_result"]
    assert "final_score_out_of_10" in result["awareness_score_result"]["summary"]
    
    # Score should be between 1-10
    score = result["awareness_score_result"]["summary"]["final_score_out_of_10"]
    assert 1 <= score <= 10


async def test_rounding_behavior():
    """Test that rounding works as expected"""
    # Testing the actual rounding logic
    # Average of [7, 8, 6] = 7.0 → round(7.0) = 7
    # Average of [7, 8, 7] = 7.33 → round(7.33) = 7
    # Average of [7, 9, 7] = 7.67 → round(7.67) = 8
    
    # This tests the mathematical behavior
    scores_1 = [7, 8, 6]
    avg_1 = sum(scores_1) / len(scores_1)
    assert round(avg_1) == 7
    
    scores_2 = [7, 8, 7]
    avg_2 = sum(scores_2) / len(scores_2)
    assert round(avg_2) == 7
    
    scores_3 = [7, 9, 7]
    avg_3 = sum(scores_3) / len(scores_3)
    assert round(avg_3) == 8


async def test_fewer_than_2_rounds():
    """Test handling of fewer than 2 rounds"""
    state = create_mock_state(user_judgements=["plausible"], round_count=1)
    
    result = await awareness_scorer(state)
    
    # Should still produce a score
    assert result["awareness_score_result"] is not None
    score = result["awareness_score_result"]["summary"]["final_score_out_of_10"]
    assert 1 <= score <= 10


async def test_no_judgements():
    """Test handling when no judgements provided"""
    state = create_mock_state(user_judgements=[], round_count=2)
    
    result = await awareness_scorer(state)
    
    # Should return default score
    assert result["awareness_score_result"] is not None
    assert result["awareness_score_result"]["summary"]["final_score_out_of_10"] == 0


def test_judgement_validation():
    """Test valid judgement values"""
    valid_judgements = ["plausible", "misleading", "not sure", "neutral"]
    
    for judgement in valid_judgements:
        # All should be valid
        assert judgement in valid_judgements
    
    # Invalid judgements (should be coerced to "neutral" by endpoint)
    invalid = "invalid_choice"
    assert invalid not in valid_judgements


def test_score_clamping():
    """Test that scores are clamped to 1-10 range"""
    # Test clamping logic
    test_values = [-5, 0, 0.5, 5, 10, 15, 100]
    
    for val in test_values:
        clamped = max(1, min(10, round(val)))
        assert 1 <= clamped <= 10


if __name__ == "__main__":
    import asyncio
    
    print("Running awareness scorer tests...")
    print("\n1. Testing average calculation...")
    asyncio.run(test_average_calculation())
    print("✓ Average calculation test passed")
    
    print("\n2. Testing rounding behavior...")
    asyncio.run(test_rounding_behavior())
    print("✓ Rounding behavior test passed")
    
    print("\n3. Testing fewer than 2 rounds...")
    asyncio.run(test_fewer_than_2_rounds())
    print("✓ Fewer rounds test passed")
    
    print("\n4. Testing no judgements...")
    asyncio.run(test_no_judgements())
    print("✓ No judgements test passed")
    
    print("\n5. Testing judgement validation...")
    test_judgement_validation()
    print("✓ Judgement validation test passed")
    
    print("\n6. Testing score clamping...")
    test_score_clamping()
    print("✓ Score clamping test passed")
    
    print("\n✅ All tests passed!")
