#!/bin/bash
# Run knowledge_qa task with all 3 strategies sequentially
# Ensure llama-server is running with -c 32768 before executing this script

MODEL="Qwen2.5-Coder-32B-Instruct-Q4_K_M.gguf"
ORG_TYPE="b2c"
TASK="knowledge_qa"

echo "=========================================="
echo "Running knowledge_qa comparison"
echo "Model: $MODEL"
echo "=========================================="

echo ""
echo "[1/3] Running ReAct..."
python run_tasks.py --org_type $ORG_TYPE --agent_strategy react --llm_provider local --model "$MODEL" --task_category $TASK --reuse_results

echo ""
echo "[2/3] Running Plan-and-Solve..."
python run_tasks.py --org_type $ORG_TYPE --agent_strategy plan_and_solve --llm_provider local --model "$MODEL" --task_category $TASK --reuse_results

echo ""
echo "[3/3] Running Reflexion..."
python run_tasks.py --org_type $ORG_TYPE --agent_strategy reflexion --llm_provider local --model "$MODEL" --task_category $TASK --reuse_results

echo ""
echo "=========================================="
echo "All 3 strategies complete for knowledge_qa"
echo "Run: python check_status.py to see results"
echo "=========================================="
