#!/usr/bin/env python3
"""
Quick status checker for CRMArena benchmark runs.
Usage: 
  python check_status.py                          # show all
  python check_status.py react                    # filter by strategy
  python check_status.py react case_routing       # filter by strategy + task
  python check_status.py "" knowledge_qa          # filter by task only
"""
import json, os, glob, sys

LOG_DIR = "logs"
TOTAL = 100

# Parse optional filters
strategy_filter = sys.argv[1] if len(sys.argv) > 1 else ""
task_filter = sys.argv[2] if len(sys.argv) > 2 else ""

files = sorted(glob.glob(f"{LOG_DIR}/results_*.json"))
if not files:
    print("No result files found in logs/ directory.")
    exit()

# Apply filters
if strategy_filter:
    files = [f for f in files if f"_{strategy_filter}_" in f]
if task_filter:
    files = [f for f in files if f"_{task_filter}" in f]

if not files:
    print(f"No results matching strategy='{strategy_filter}' task='{task_filter}'")
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
        # Shorten model name prefix for readability
        name = name.replace("Qwen2.5-Coder-32B-Instruct-Q4_K_M.gguf_", "Coder32B_")
        name = name.replace("Qwen2.5-32B-Instruct-Q4_K_M.gguf_", "Qwen32B_")
        name = name.replace("Meta-Llama-3.1-70B-Instruct-Q4_K_S.gguf_", "Llama70B_")
        print(f"{name:<45} {done:>5}/{TOTAL} {passed:>5} {acc:>25}")
    except Exception as e:
        print(f"{os.path.basename(f)}: ERROR - {e}")

print("=" * 80)
