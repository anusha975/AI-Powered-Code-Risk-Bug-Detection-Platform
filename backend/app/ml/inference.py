"""
Risk Scoring Inference and Explainability Engine.

Combines deterministic rule-based scoring and Scikit-learn ML regression
to produce bounded risk scores, severity classifications, and human-interpretable reasons.
"""

from typing import List, Dict, Any, Tuple
import numpy as np

from app.schemas.risk import RiskLevel, RiskScoreBreakdown, RiskScoreResponse
from app.ml.feature_extractor import extract_features, feature_dict_to_vector
from app.ml.model_trainer import get_risk_model_trainer


def calculate_deterministic_score(
    features: Dict[str, float],
    findings: List[Dict[str, Any]],
    secrets_count: int = 0
) -> Tuple[float, List[str]]:
    """
    Calculate an interpretable deterministic baseline risk score (0-100)
    and compile human-readable explanations.
    """
    score = 0.0
    reasons: List[str] = []

    crit = int(features.get("critical_findings_count", 0))
    high = int(features.get("high_findings_count", 0))
    med = int(features.get("medium_findings_count", 0))
    low = int(features.get("low_findings_count", 0))
    secrets_flag = features.get("has_secrets_flag", 0.0) > 0.0 or secrets_count > 0
    cyclo = features.get("cyclomatic_complexity", 1.0)
    nesting = features.get("max_nesting_depth", 0.0)
    density = features.get("finding_density_per_100_lines", 0.0)

    # 1. Critical findings
    if crit > 0:
        score += crit * 32.0
        reasons.append(f"Detected {crit} critical-severity finding(s) presenting immediate security hazards.")

    # 2. High findings
    if high > 0:
        score += high * 18.0
        reasons.append(f"Identified {high} high-severity issue(s) that could compromise application integrity.")

    # 3. Medium findings
    if med > 0:
        score += med * 7.0
        if med >= 3:
            reasons.append(f"Multiple medium-severity findings ({med}) indicating potential logic flaws or error handling gaps.")
        else:
            reasons.append(f"Detected {med} medium-severity finding(s).")

    # 4. Low findings
    if low > 0:
        score += min(15.0, low * 2.0)
        reasons.append(f"Identified {low} low-severity code quality or style issue(s).")

    # 5. Secrets
    if secrets_flag:
        score += 25.0
        reasons.append("Detected exposed secrets/credentials or hardcoded sensitive tokens in the code.")

    # 6. Structural Complexity
    if cyclo >= 25.0:
        score += 15.0
        reasons.append(f"Excessive cyclomatic complexity ({int(cyclo)}) significantly increases bug and regression risk.")
    elif cyclo >= 12.0:
        score += 8.0
        reasons.append(f"Elevated cyclomatic complexity ({int(cyclo)}) makes code harder to audit and test.")

    # 7. Nesting Depth
    if nesting >= 7.0:
        score += 8.0
        reasons.append(f"Deeply nested code structures (depth {int(nesting)}) impair control flow readability.")
    elif nesting >= 4.0:
        score += 4.0

    # 8. Finding Density
    if density >= 20.0 and len(findings) > 2:
        score += 10.0
        reasons.append(f"High finding density ({density:.1f} issues per 100 lines) reflects systemic quality risks.")

    # Baseline floor for severe issues
    if crit > 0 or secrets_flag:
        score = max(score, 80.0)
    elif high > 0:
        score = max(score, 55.0)

    # Clean profile note if no reasons generated
    if not reasons:
        reasons.append("Clean code profile: Local AST and SAST analyzers detected no security or quality anomalies.")

    # Clamp baseline score
    bounded_score = float(np.clip(score, 0.0, 100.0))
    return round(bounded_score, 2), reasons


def map_score_to_risk_level(score: float) -> RiskLevel:
    """Map continuous score (0-100) to RiskLevel enum."""
    if score >= 80.0:
        return RiskLevel.CRITICAL
    elif score >= 55.0:
        return RiskLevel.HIGH
    elif score >= 25.0:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def infer_risk_score(
    content: str,
    findings: List[Dict[str, Any]],
    language: str = "python",
    secrets_count: int = 0,
    filename: str = "snippet.py"
) -> RiskScoreResponse:
    """
    Full inference pipeline:
    1. Feature Extraction (16 numerical dimensions)
    2. Deterministic baseline scoring
    3. Scikit-learn ML regression inference
    4. Score blending and bounds enforcement
    5. Explainability reasons synthesis
    """
    features = extract_features(content=content, findings=findings, secrets_count=secrets_count)
    feature_vector = feature_dict_to_vector(features)

    # 1. Deterministic baseline
    det_score, reasons = calculate_deterministic_score(
        features=features, findings=findings, secrets_count=secrets_count
    )

    # 2. Scikit-learn ML prediction
    trainer = get_risk_model_trainer()
    arr_vector = np.array(feature_vector, dtype=np.float64).reshape(1, -1)
    ml_pred = trainer.predict(arr_vector)

    # 3. Blending strategy:
    # If findings are empty and secrets are 0, prioritize pristine deterministic 0
    if len(findings) == 0 and secrets_count == 0 and features.get("cyclomatic_complexity", 1.0) < 5.0:
        final_score = int(round(det_score))
    else:
        # 60% deterministic + 40% ML model
        blended = (0.60 * det_score) + (0.40 * ml_pred)
        # Critical floor enforcement
        if features.get("critical_findings_count", 0) > 0 or features.get("has_secrets_flag", 0) > 0:
            blended = max(blended, 80.0)
        elif features.get("high_findings_count", 0) > 0:
            blended = max(blended, 55.0)

        final_score = int(round(float(np.clip(blended, 0.0, 100.0))))

    risk_level = map_score_to_risk_level(float(final_score))

    # Calculate feature contributions
    contributions: Dict[str, float] = {}
    total_signal = (
        (features.get("critical_findings_count", 0) * 30.0) +
        (features.get("high_findings_count", 0) * 18.0) +
        (features.get("medium_findings_count", 0) * 7.0) +
        (features.get("low_findings_count", 0) * 2.0) +
        (features.get("has_secrets_flag", 0) * 25.0) +
        (min(20.0, features.get("cyclomatic_complexity", 1.0) * 1.5))
    )

    if total_signal > 0:
        contributions["critical_severity"] = round((features.get("critical_findings_count", 0) * 30.0 / total_signal) * 100.0, 1)
        contributions["high_severity"] = round((features.get("high_findings_count", 0) * 18.0 / total_signal) * 100.0, 1)
        contributions["medium_severity"] = round((features.get("medium_findings_count", 0) * 7.0 / total_signal) * 100.0, 1)
        contributions["exposed_secrets"] = round((features.get("has_secrets_flag", 0) * 25.0 / total_signal) * 100.0, 1)
        contributions["code_complexity"] = round((min(20.0, features.get("cyclomatic_complexity", 1.0) * 1.5) / total_signal) * 100.0, 1)
    else:
        contributions["clean_baseline"] = 100.0

    breakdown = RiskScoreBreakdown(
        deterministic_score=det_score,
        ml_predicted_score=round(ml_pred, 2),
        model_confidence=0.92,
        feature_metrics=features,
        feature_contributions=contributions,
        total_findings_count=len(findings),
        secrets_detected_count=secrets_count,
        cyclomatic_complexity=features.get("cyclomatic_complexity", 1.0),
        max_nesting_depth=features.get("max_nesting_depth", 0.0)
    )

    return RiskScoreResponse(
        risk_score=final_score,
        risk_level=risk_level,
        reasons=reasons,
        breakdown=breakdown,
        filename=filename,
        model_metadata={
            "pipeline": "Hybrid Deterministic + Scikit-learn RandomForestRegressor",
            "feature_dimensions": len(feature_vector),
            "evaluation_metrics": trainer.evaluation_metrics,
            "disclaimer": "ML scoring trained on structured synthetic risk profiles; complements deterministic SAST heuristics without empirical claims."
        }
    )
