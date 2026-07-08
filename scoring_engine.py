"""
MSME Financial Health Card — Scoring Engine
IDBI Innovate 2026 — Track 03: Financial Inclusion, Digital Lending & Credit Decisioning

Computes a 5-pillar Financial Health Score (0-100) plus a 90-day forward
trajectory, from alternate data sources (GST, UPI/AA, EPFO).

This mirrors the logic used in the interactive dashboard (index.html) so the
same scoring behaviour can be exposed as an API (FastAPI-ready) or run in
batch over a real/synthetic MSME dataset.
"""

from dataclasses import dataclass, field
from typing import List, Literal
import statistics


PILLAR_WEIGHTS = {
    "revenue_stability": 0.25,
    "cash_flow_health": 0.25,
    "compliance_discipline": 0.20,
    "digital_footprint": 0.15,
    "debt_behavior": 0.15,
}

Band = Literal["Green", "Amber", "Red"]


@dataclass
class MSMEProfile:
    business_id: str
    name: str
    sector: str
    # last 6 months, e.g. normalized GST turnover index
    revenue_series: List[float]
    # last 6 months, UPI/AA inflow-to-outflow ratio
    cashflow_ratio_series: List[float]
    gst_filing_rate: float       # 0-100, % of on-time filings
    epfo_consistency: float      # 0-100, % of consistent contributions
    digital_depth: float         # 0-100, digital payment adoption score
    debt_utilization: float      # 0-100, higher = more utilized/riskier


@dataclass
class HealthCardResult:
    business_id: str
    name: str
    overall_score: float
    band: Band
    pillar_scores: dict
    trajectory_label: str
    projected_score_90d: float
    projected_delta: float
    flags: List[str] = field(default_factory=list)
    loan_recommendation: dict = field(default_factory=dict)


def _slope(series: List[float]) -> float:
    """Simple linear regression slope over an evenly spaced series."""
    n = len(series)
    x_mean = (n - 1) / 2
    y_mean = sum(series) / n
    num = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(series))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def score_revenue_stability(revenue_series: List[float]) -> float:
    mean = statistics.mean(revenue_series)
    stdev = statistics.pstdev(revenue_series)
    return _clamp(mean - stdev * 1.2)


def score_cash_flow_health(cashflow_series: List[float]) -> float:
    mean_ratio = statistics.mean(cashflow_series)
    return _clamp((mean_ratio - 0.5) / 1.3 * 100)


def score_compliance(gst_filing_rate: float, epfo_consistency: float) -> float:
    return _clamp(gst_filing_rate * 0.6 + epfo_consistency * 0.4)


def score_digital_footprint(digital_depth: float) -> float:
    return _clamp(digital_depth)


def score_debt_behavior(debt_utilization: float) -> float:
    return _clamp(100 - debt_utilization)


def compute_trajectory(revenue_series: List[float], cashflow_series: List[float],
                        overall_score: float) -> tuple:
    rev_slope = _slope(revenue_series)
    cf_slope = _slope(cashflow_series) * 40  # scale cashflow ratio slope to score-points
    composite_slope = rev_slope * 0.55 + cf_slope * 0.45
    projected_delta = composite_slope * 3  # ~90 days out, 3 monthly steps
    projected_score = _clamp(overall_score + projected_delta)

    if composite_slope > 0.8:
        label = "Improving"
    elif composite_slope < -0.8:
        label = "Declining"
    else:
        label = "Stable"

    return label, projected_score, projected_delta


def generate_flags(pillars: dict, debt_utilization: float, gst_filing_rate: float,
                    digital_depth: float) -> List[str]:
    flags = []
    if pillars["revenue_stability"] >= 65:
        flags.append("Consistent turnover growth")
    if pillars["revenue_stability"] < 45:
        flags.append("Revenue volatility detected")
    if pillars["cash_flow_health"] >= 65:
        flags.append("Healthy cash flow buffer")
    if pillars["cash_flow_health"] < 40:
        flags.append("Cash flow strain")
    if gst_filing_rate >= 80:
        flags.append("Strong GST filing discipline")
    if gst_filing_rate < 55:
        flags.append("Irregular GST filings")
    if debt_utilization >= 55:
        flags.append("High debt utilization")
    if digital_depth >= 75:
        flags.append("Strong digital footprint")
    return flags


def recommend_lending(band: Band) -> dict:
    if band == "Green":
        return {"status": "Eligible — fast-track", "amount_range": "₹8L – ₹35L", "rate_band": "10.5% – 12.5%"}
    if band == "Amber":
        return {"status": "Eligible — standard review", "amount_range": "₹3L – ₹12L", "rate_band": "13% – 16%"}
    return {"status": "Refer — secured / co-lending only", "amount_range": "₹1L – ₹4L", "rate_band": "17% – 20%"}


def band_for_score(score: float) -> Band:
    if score >= 70:
        return "Green"
    if score >= 40:
        return "Amber"
    return "Red"


def compute_health_card(profile: MSMEProfile) -> HealthCardResult:
    pillars = {
        "revenue_stability": score_revenue_stability(profile.revenue_series),
        "cash_flow_health": score_cash_flow_health(profile.cashflow_ratio_series),
        "compliance_discipline": score_compliance(profile.gst_filing_rate, profile.epfo_consistency),
        "digital_footprint": score_digital_footprint(profile.digital_depth),
        "debt_behavior": score_debt_behavior(profile.debt_utilization),
    }

    overall = sum(pillars[k] * PILLAR_WEIGHTS[k] for k in PILLAR_WEIGHTS)
    band = band_for_score(overall)

    trajectory_label, projected_score, projected_delta = compute_trajectory(
        profile.revenue_series, profile.cashflow_ratio_series, overall
    )

    flags = generate_flags(pillars, profile.debt_utilization, profile.gst_filing_rate, profile.digital_depth)
    lending = recommend_lending(band)

    return HealthCardResult(
        business_id=profile.business_id,
        name=profile.name,
        overall_score=round(overall, 1),
        band=band,
        pillar_scores={k: round(v, 1) for k, v in pillars.items()},
        trajectory_label=trajectory_label,
        projected_score_90d=round(projected_score, 1),
        projected_delta=round(projected_delta, 1),
        flags=flags,
        loan_recommendation=lending,
    )


if __name__ == "__main__":
    sample = MSMEProfile(
        business_id="MSME-2201",
        name="Anand Kirana Store",
        sector="Retail · Grocery",
        revenue_series=[62, 65.5, 69, 72.5, 76, 79.5],
        cashflow_ratio_series=[1.05, 1.07, 1.09, 1.11, 1.13, 1.15],
        gst_filing_rate=88,
        epfo_consistency=70,
        digital_depth=60,
        debt_utilization=35,
    )
    result = compute_health_card(sample)
    print(f"{result.name} ({result.business_id})")
    print(f"Overall score: {result.overall_score} — {result.band}")
    print(f"Pillars: {result.pillar_scores}")
    print(f"Trajectory: {result.trajectory_label} -> {result.projected_score_90d} (Δ {result.projected_delta})")
    print(f"Flags: {result.flags}")
    print(f"Lending: {result.loan_recommendation}")
