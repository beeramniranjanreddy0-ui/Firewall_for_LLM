from app.firewall.scoring import RiskScorer


def test_risk_level_mapping_uses_good_thresholds() -> None:
    assert RiskScorer.level(0) == "SAFE"
    assert RiskScorer.level(1) == "GOOD"
    assert RiskScorer.level(10) == "GOOD"
    assert RiskScorer.level(25) == "GOOD"
    assert RiskScorer.level(26) == "MEDIUM"
    assert RiskScorer.level(30) == "MEDIUM"
    assert RiskScorer.level(60) == "MEDIUM"
    assert RiskScorer.level(61) == "HIGH"
    assert RiskScorer.level(85) == "HIGH"
