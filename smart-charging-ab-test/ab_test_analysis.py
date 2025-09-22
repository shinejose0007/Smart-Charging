#!/usr/bin/env python3
"""
ab_test_analysis.py
Loads data/ab_test_data.csv and runs:
 - proportion test for charged_in_low
 - t-test for energy_kwh
 - bootstrap CI for differences
Outputs results to stdout and saves simple figures.
"""
import argparse
import os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt

def load_data(path):
    df = pd.read_csv(path, parse_dates=["session_ts"])
    return df

def summarize_kpis(df):
    grouped = df.groupby("group").agg(
        sessions=("user_id","count"),
        low_share=("charged_in_low","mean"),
        avg_kwh=("energy_kwh","mean"),
        std_kwh=("energy_kwh","std")
    ).reset_index()
    return grouped

def z_test_proportions(df, metric_col="charged_in_low"):
    cont = df[df["group"]=="control"][metric_col].astype(int)
    treat = df[df["group"]=="treatment"][metric_col].astype(int)
    count = np.array([treat.sum(), cont.sum()])
    nobs = np.array([len(treat), len(cont)])
    stat, pval = sm.stats.proportions_ztest(count, nobs, alternative='two-sided')
    diff = treat.mean() - cont.mean()
    return {"stat": stat, "pvalue": pval, "diff": diff, "treat_mean": treat.mean(), "control_mean": cont.mean()}

def t_test_continuous(df, metric_col="energy_kwh"):
    cont = df[df["group"]=="control"][metric_col]
    treat = df[df["group"]=="treatment"][metric_col]
    stat, pval = stats.ttest_ind(treat, cont, equal_var=False)
    return {"stat": stat, "pvalue": pval, "diff": treat.mean() - cont.mean(), "treat_mean": treat.mean(), "control_mean": cont.mean()}

def bootstrap_diff(df, metric_col, n_boot=2000, seed=1):
    rng = np.random.default_rng(seed)
    treat = df[df["group"]=="treatment"][metric_col].values
    cont = df[df["group"]=="control"][metric_col].values
    diffs = []
    for _ in range(n_boot):
        s1 = rng.choice(treat, size=len(treat), replace=True)
        s0 = rng.choice(cont, size=len(cont), replace=True)
        diffs.append(s1.mean() - s0.mean())
    diffs = np.array(diffs)
    lower = np.percentile(diffs, 2.5)
    upper = np.percentile(diffs, 97.5)
    return lower, upper, diffs.mean(), diffs

def plot_hist_boot(diffs, outpath):
    plt.figure(figsize=(6,4))
    plt.hist(diffs, bins=50)
    plt.title("Bootstrap distribution: difference (treatment - control)")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def main(args):
    os.makedirs(args.output, exist_ok=True)
    df = load_data(args.input)
    print("Loaded data:", df.shape)
    print("\nKPI summary by group:")
    print(summarize_kpis(df).to_string(index=False))
    print("\nProportion test (charged_in_low):")
    prop = z_test_proportions(df)
    print(prop)
    print("\nT-test (energy_kwh):")
    ttest = t_test_continuous(df)
    print(ttest)
    print("\nBootstrap CI for difference in energy_kwh:")
    lower, upper, mean_diff, diffs = bootstrap_diff(df, "energy_kwh", n_boot=args.n_boot)
    print(f"mean_diff={mean_diff:.4f}, 95% CI=({lower:.4f}, {upper:.4f})")
    plot_hist_boot(diffs, os.path.join(args.output, "bootstrap_energy_diff.png"))
    print(f"Plots saved to {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/ab_test_data.csv")
    parser.add_argument("--output", default="results")
    parser.add_argument("--n_boot", type=int, default=2000)
    args = parser.parse_args()
    main(args)
