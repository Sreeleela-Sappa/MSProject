#!/usr/bin/env python3
"""
Quick status checker for CRMArena benchmark runs.
Usage: python check_status.py
"""
import json, os, glob

LOG_DIR = "logs"
TOTAL = 100

files = sorted(glob.glob(f"{LOG_DIR}/results_*.json"))
if not files:
    print("No result files found in logs/ directory.")
    exit()

print("=" * 65)
print(f"{'FILE':<45} {'DONE':>6} {'PASS':>6} {'ACC':>6}")
print("=" * 65)

for f in files:
    try:
        with open(f) as fp:
            d = json.load(fp)
        done = len(d)

        def is_pass(reward):
            if isinstance(reward, dict):
                # Soft metrics: use F1 >= 0.5 as pass threshold
                return reward.get("f1", 0) >= 0.5
            return reward == 1

        passed = sum(1 for t in d if is_pass(t["reward"]))
        # Also show avg F1 for soft-metric tasks
        rewards = [t["reward"] for t in d]
        if rewards and isinstance(rewards[0], dict):
            avg_f1 = sum(r.get("f1", 0) for r in rewards) / done
            acc = f"{100*passed/done:.1f}% (avgF1:{avg_f1:.2f})"
        else:
            acc = f"{100*passed/done:.1f}%" if done > 0 else "N/A"
        name = os.path.basename(f).replace("results_", "").replace(".json", "")
        if len(name) > 44:
            name = name[:41] + "..."
        print(f"{name:<45} {done:>5}/{TOTAL} {passed:>5} {acc:>25}")
    except Exception as e:
        print(f"{os.path.basename(f)}: ERROR - {e}")

print("=" * 80)
