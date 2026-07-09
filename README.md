# MSME Financial Health Card

**IDBI Innovate 2026 — Track 03: Financial Inclusion, Digital Lending & Credit Decisioning**
**Team Pulse Capital Labs**

Explainable, forward-looking credit scoring built from GST, UPI, EPFO and Account Aggregator data — for New-to-Credit and New-to-Bank MSMEs.

🔗 **Live demo:** [idbimsmehealthcard.netlify.app](https://idbimsmehealthcard.netlify.app/)

---

## The problem

Bank's MSME credit evaluation relies on traditional financial documents, which many New-to-Credit (NTC) and New-to-Bank (NTB) enterprises lack or maintain inadequately. Rich alternate data exists (GST, UPI, Account Aggregator, EPFO) but sits fragmented across systems, with no unified assessment framework — leading to high rejection rates and missed viable borrowers.

## The idea

A CIBIL-style score alternative for the credit-invisible: the MSME Financial Health Card aggregates alternate data into a single, explainable **0–100 Financial Health Score** — and goes a step further by predicting a **90-day forward trajectory** (Improving / Stable / Declining), so underwriters see direction, not just a snapshot.

Every score ships with a concrete lending recommendation: eligibility band, suggested loan amount range, and indicative rate.

## What's in this repo

| File | Description |
|---|---|
| `msme_health_card_dashboard.html` | Self-contained interactive dashboard — browse 14 sample MSME profiles across sectors, see live score breakdowns, trajectories, and lending recommendations. Open directly in any browser, no build step. |
| `scoring_engine.py` | Standalone Python implementation of the same scoring logic, framework-agnostic and ready to wrap as a FastAPI endpoint. |

## Try it yourself

1. Open the [live demo](https://idbimsmehealthcard.netlify.app/)
2. Select any MSME from the portfolio list on the left
3. See the live Financial Health Score, 5-pillar breakdown, 90-day trajectory, risk/positive signal flags, and lending recommendation update instantly

## How the scoring works

A weighted, explainable 5-pillar framework — not a black box:

| Pillar | Weight | Signal |
|---|---|---|
| Revenue stability | 25% | GST turnover trend & volatility |
| Cash flow health | 25% | UPI/AA inflow-to-outflow ratio |
| Compliance discipline | 20% | GST filing regularity & EPFO consistency |
| Digital footprint | 15% | Digital payment adoption depth |
| Debt behavior | 15% | Credit utilization pattern |

The trajectory model applies linear trend analysis to each pillar's underlying time series, projecting momentum 90 days forward — catching stress or recovery before it shows up in a static snapshot.

See `scoring_engine.py` for the full implementation, including a runnable example.

## Validation

Internal validation run across 14 synthetic MSME profiles spanning 10 sectors:

- Band distribution: **2 Green · 9 Amber · 3 Red** (realistic long-tail spread, not artificially balanced)
- Trajectory split: **9 Improving · 1 Stable · 4 Declining**
- Every score ships with a pillar-level breakdown — no black-box output

## Roadmap

- Sandbox integration — connect live GST, UPI/AA and EPFO sandbox APIs in place of synthetic data
- Model calibration — tune the trajectory model against real repayment/default outcomes
- API hardening — wrap the scoring engine as a documented REST endpoint
- Pilot ULI/OCEN connectivity for underwriting workflow integration
- Extend the same explainable framework to Personal, Home, and Auto loans

## Tech stack

HTML / CSS / JavaScript (interactive dashboard) · Python (portable scoring engine) · AWS + Applied Cloud Computing (planned sandbox hosting)

---

Built for IDBI Innovate 2026 by **Pulse Capital Labs**.
