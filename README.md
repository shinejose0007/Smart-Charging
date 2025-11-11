Smart-Charging A/B Test
Short description.
Dieses Projekt simuliert ein produktorientiertes A/B-Experiment für eine Smart-Charging-Funktion: eine Behandlung (neues Lade-Timing-Signal) vs. Kontrolle (Status quo). Ziel ist, die Wirkung auf Nutzerverhalten (z. B. Anteil der Ladevorgänge in Niedrigpreis-Zeiten und geladene kWh) zu messen, statistisch zu bewerten und Handlungsempfehlungen zu geben.

Why this is relevant to hiring managers at energy / product-data teams

Demonstrates product analytics: hypothesis → KPI → experiment design → statistical conclusion → business recommendation.
Shows ETL + reproducible data generation and analysis in Python, plus testing/CI.
Contains time-series-like user session data and energy consumption metrics that map to smart-charging use cases.
Includes production-minded touches: modular code, requirements, Dockerfile, and CI workflow.
What’s included
generate_data.py — reproducible synthetic dataset generator (users, sessions, treatment assignment, prices, energy_kWh, indicator whether charge happened during low-price window).
ab_test_analysis.py — analysis pipeline: data loading, KPI calculation, two-sample tests (continuous & proportions), bootstrap CIs, simple visualization outputs (matplotlib).
notebook/Smart_Charging_AB_Test.ipynb — Jupyter notebook skeleton with step-by-step analysis and explanations.
queries.sql — example SQL snippets showing how to aggregate cohort metrics (useful for BigQuery / analytics stacks).
requirements.txt — Python dependencies.
Dockerfile and .github/workflows/ci.yml — minimal steps to show production/CI awareness.
Quick start
Create virtualenv:
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
Generate synthetic data:
python generate_data.py --output data/ab_test_data.csv --n_users 20000 --seed 42
Run the analysis:
python ab_test_analysis.py --input data/ab_test_data.csv --output results
The script will print KPI tables, test results and save simple PNGs to the results/ folder.
