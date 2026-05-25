"""
Self-Consistency (SC) Prompting Templates for CRMArena-Pro

Self-Consistency (Wang et al., n.d.) samples multiple independent Chain-of-Thought
reasoning paths and selects the most consistent (majority-vote) answer.

Implementation:
- The agent runs N=3 independent reasoning paths for the same task
- Each path uses the same ReAct-style prompt but with temperature > 0 for diversity
- After all paths complete, the most common final answer is selected
- The prompt itself is identical to ReAct — the difference is in the execution loop

This file reuses the ReAct prompts since SC's differentiation is in the multi-path
execution, not in the prompt structure.
"""

from crm_sandbox.agents.prompts import (
    SCHEMA_STRING,
    SYSTEM_METADATA,
    REACT_RULE_STRING,
    REACT_INTERNAL_PROMPT,
    REACT_EXTERNAL_PROMPT,
    REACT_PRIVACY_AWARE_EXTERNAL_PROMPT,
    REACT_INTERNAL_INTERACTIVE_PROMPT,
    REACT_EXTERNAL_INTERACTIVE_PROMPT,
    REACT_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT,
)

# SC uses the same prompts as ReAct — the difference is multi-path execution
SC_RULE_STRING = REACT_RULE_STRING
SC_INTERNAL_PROMPT = REACT_INTERNAL_PROMPT
SC_EXTERNAL_PROMPT = REACT_EXTERNAL_PROMPT
SC_PRIVACY_AWARE_EXTERNAL_PROMPT = REACT_PRIVACY_AWARE_EXTERNAL_PROMPT
SC_INTERNAL_INTERACTIVE_PROMPT = REACT_INTERNAL_INTERACTIVE_PROMPT
SC_EXTERNAL_INTERACTIVE_PROMPT = REACT_EXTERNAL_INTERACTIVE_PROMPT
SC_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT = REACT_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT

# Number of independent paths to sample
SC_NUM_PATHS = 3

# Temperature for diverse sampling (ReAct uses 0.0, SC needs diversity)
SC_TEMPERATURE = 0.7
