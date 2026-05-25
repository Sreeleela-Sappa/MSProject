#!/bin/bash

# ============================================================
# Run all 5 strategies against CRMArena-Pro tasks
# Using local GGUF model via llama.cpp
# ============================================================

MODEL="Qwen2.5-Coder-32B-Instruct-Q4_K_M.gguf"
LLM_PROVIDER="local"
ORG_TYPE="b2c"
EVAL_MODE="aided"
PRIVACY_AWARE_PROMPT="false"

STRATEGIES=(
    "react"
    "plan_and_solve"
    "reflexion"
    "self_consistency"
    "tree_of_thought"
)

TASKS=(
    "case_routing"
    "transfer_count"
    "handle_time"
    "lead_routing"
    "conversion_rate_comprehension"
    "quote_approval"
    "invalid_config"
    "private_customer_information"
)

RESULT_DIR="logs"

echo "=========================================="
echo "CRMArena-Pro: All Strategies Comparison"
echo "Model: $MODEL"
echo "Org: $ORG_TYPE"
echo "Provider: $LLM_PROVIDER"
echo "=========================================="

for STRATEGY in "${STRATEGIES[@]}"; do
    for TASK in "${TASKS[@]}"; do
        echo ""
        echo "[Running] Strategy: $STRATEGY | Task: $TASK"

        python -u run_tasks.py \
            --model "$MODEL" \
            --task_category "$TASK" \
            --agent_eval_mode "$EVAL_MODE" \
            --log_dir "$RESULT_DIR" \
            --agent_strategy "$STRATEGY" \
            --llm_provider "$LLM_PROVIDER" \
            --reuse_results \
            --privacy_aware_prompt "$PRIVACY_AWARE_PROMPT" \
            --org_type "$ORG_TYPE"

        echo "[Done] Strategy: $STRATEGY | Task: $TASK"
    done
done

echo ""
echo "=========================================="
echo "All runs complete. Check results:"
echo "  python check_status.py"
echo "=========================================="
