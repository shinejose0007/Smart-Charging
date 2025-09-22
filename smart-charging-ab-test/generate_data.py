#!/usr/bin/env python3
"""
generate_data.py
Generates synthetic session-level data for an A/B test of a smart-charging signal.
Outputs CSV suitable for analysis.
"""
import argparse
import numpy as np
import pandas as pd

def generate_users(n_users, seed=42):
    rng = np.random.default_rng(seed)
    user_ids = np.arange(1, n_users+1)
    propensity = rng.beta(2,5, size=n_users)
    return pd.DataFrame({"user_id": user_ids, "propensity": propensity})

def generate_sessions(users_df, sessions_per_user_mean=3, seed=42):
    rng = np.random.default_rng(seed+1)
    rows = []
    for _, row in users_df.iterrows():
        n_sessions = max(1, int(rng.poisson(sessions_per_user_mean)))
        for s in range(n_sessions):
            ts = pd.Timestamp("2024-06-01") + pd.to_timedelta(rng.integers(0, 30*24*60), unit='m')
            rows.append({
                "user_id": int(row["user_id"]),
                "session_ts": ts,
                "propensity": float(row["propensity"])
            })
    df = pd.DataFrame(rows)
    return df

def assign_treatment(sessions_df, seed=42):
    rng = np.random.default_rng(seed+2)
    sessions_df = sessions_df.copy()
    sessions_df["group"] = rng.choice(["control","treatment"], size=len(sessions_df), p=[0.5,0.5])
    return sessions_df

def simulate_pricing_and_charging(sessions_df, seed=42):
    rng = np.random.default_rng(seed+3)
    df = sessions_df.copy()
    df["hour"] = df["session_ts"].dt.hour
    def base_low_prob(hour, propensity):
        if 2 <= hour <= 5:
            return 0.6 + 0.3*propensity
        else:
            return 0.1 + 0.4*propensity
    df["base_low_prob"] = df.apply(lambda r: base_low_prob(r["hour"], r["propensity"]), axis=1)
    df["treatment_effect"] = df["propensity"] * 0.15
    df["p_shift_to_low"] = df["base_low_prob"] + (df["treatment_effect"] * (df["group"]=="treatment"))
    df["p_shift_to_low"] = df["p_shift_to_low"].clip(0,1)
    df["charged_in_low"] = rng.random(len(df)) < df["p_shift_to_low"]
    base_kwh = rng.normal(7, 2, size=len(df))
    df["energy_kwh"] = (base_kwh + np.where(df["charged_in_low"], rng.normal(1.5,0.5,len(df)), rng.normal(0,0.5,len(df)))).clip(0.1)
    out = df[["user_id","session_ts","group","propensity","charged_in_low","energy_kwh"]].copy()
    return out

def main(args):
    users = generate_users(args.n_users, seed=args.seed)
    sessions = generate_sessions(users, sessions_per_user_mean=args.sessions_mean, seed=args.seed)
    sessions = assign_treatment(sessions, seed=args.seed)
    data = simulate_pricing_and_charging(sessions, seed=args.seed)
    data.to_csv(args.output, index=False)
    print(f"Generated {len(data)} sessions for {args.n_users} users -> {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_users", type=int, default=5000)
    parser.add_argument("--sessions_mean", type=float, default=3.0)
    parser.add_argument("--output", type=str, default="data/ab_test_data.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args)
