from scripts.eq12_ai_guardrails import score_negative_marking


def test_negative_marking_scoring() -> None:
    truth = "september 10"
    y_right = {
        "answer": "September 10",
        "abstain": False,
        "confidence": 0.8,
        "citations": [],
    }
    y_wrong = {
        "answer": "Sept 11",
        "abstain": False,
        "confidence": 0.9,
        "citations": [],
    }
    y_abst = {"answer": "", "abstain": True, "confidence": 0.2, "citations": []}

    assert score_negative_marking(truth, y_right) == 1.0
    assert score_negative_marking(truth, y_wrong) == -1.0
    assert score_negative_marking(truth, y_abst) == 0.3
