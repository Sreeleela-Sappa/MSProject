import os
from litellm import completion
import litellm
litellm.set_verbose = False
from typing import Dict, List
import time, traceback
from crm_sandbox.agents.prompts import SCHEMA_STRING, REACT_RULE_STRING, ACT_RULE_STRING, SYSTEM_METADATA, REACT_EXTERNAL_INTERACTIVE_PROMPT, REACT_INTERNAL_INTERACTIVE_PROMPT, REACT_INTERNAL_PROMPT, REACT_EXTERNAL_PROMPT, REACT_PRIVACY_AWARE_EXTERNAL_PROMPT, REACT_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT, ACT_PROMPT
from crm_sandbox.agents.plan_and_solve_prompts import (
    PAS_RULE_STRING,
    PAS_INTERNAL_PROMPT,
    PAS_EXTERNAL_PROMPT,
    PAS_PRIVACY_AWARE_EXTERNAL_PROMPT,
    PAS_INTERNAL_INTERACTIVE_PROMPT,
    PAS_EXTERNAL_INTERACTIVE_PROMPT,
    PAS_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT,
)
from crm_sandbox.agents.reflexion_prompts import (
    REFLEXION_RULE_STRING,
    REFLEXION_INTERNAL_PROMPT,
    REFLEXION_EXTERNAL_PROMPT,
    REFLEXION_PRIVACY_AWARE_EXTERNAL_PROMPT,
    REFLEXION_INTERNAL_INTERACTIVE_PROMPT,
    REFLEXION_EXTERNAL_INTERACTIVE_PROMPT,
    REFLEXION_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT,
)
from crm_sandbox.agents.self_consistency_prompts import (
    SC_RULE_STRING,
    SC_INTERNAL_PROMPT,
    SC_EXTERNAL_PROMPT,
    SC_PRIVACY_AWARE_EXTERNAL_PROMPT,
    SC_INTERNAL_INTERACTIVE_PROMPT,
    SC_EXTERNAL_INTERACTIVE_PROMPT,
    SC_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT,
    SC_NUM_PATHS,
    SC_TEMPERATURE,
)
from crm_sandbox.agents.tree_of_thought_prompts import (
    TOT_RULE_STRING,
    TOT_INTERNAL_PROMPT,
    TOT_EXTERNAL_PROMPT,
    TOT_PRIVACY_AWARE_EXTERNAL_PROMPT,
    TOT_INTERNAL_INTERACTIVE_PROMPT,
    TOT_EXTERNAL_INTERACTIVE_PROMPT,
    TOT_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT,
    TOT_GENERATOR_SUFFIX,
    TOT_EVALUATOR_PROMPT,
    TOT_NUM_CANDIDATES,
)
from crm_sandbox.agents.step_back_prompts import (
    STEP_BACK_RULE_STRING,
    STEP_BACK_INTERNAL_PROMPT,
    STEP_BACK_EXTERNAL_PROMPT,
    STEP_BACK_PRIVACY_AWARE_EXTERNAL_PROMPT,
    STEP_BACK_INTERNAL_INTERACTIVE_PROMPT,
    STEP_BACK_EXTERNAL_INTERACTIVE_PROMPT,
    STEP_BACK_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT,
)
from crm_sandbox.agents.soql_reference import SOQL_REFERENCE
from crm_sandbox.agents.utils import parse_wrapped_response, BEDROCK_MODELS_MAP, TOGETHER_MODELS_MAP, VERTEX_MODELS_MAP
import together




class ChatAgent:
    def __init__(
        self, schema_obj, model: str = "gpt-4o", max_turns: int = 20, eval_mode="default", strategy="react", provider="bedrock", interactive=False, agent_type="internal", privacy_aware_prompt=False
    ):
        schema = self._build_schema(schema_obj)
        assert strategy in ["react", "act", "plan_and_solve", "reflexion", "self_consistency", "tree_of_thought", "step_back"], "Only react, act, plan_and_solve, reflexion, self_consistency, tree_of_thought, and step_back strategies supported"
        assert agent_type in ["internal", "external"], "Invalid agent type"
        
        if strategy == "react":
            # react strategy
            if not interactive:
                if agent_type == "internal":
                    self.sys_prompt = REACT_INTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = REACT_PRIVACY_AWARE_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = REACT_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
            else:
                if agent_type == "internal":
                    self.sys_prompt = REACT_INTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = REACT_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = REACT_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
        elif strategy == "plan_and_solve":
            # Plan-and-Solve strategy
            if not interactive:
                if agent_type == "internal":
                    self.sys_prompt = PAS_INTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = PAS_PRIVACY_AWARE_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = PAS_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
            else:
                if agent_type == "internal":
                    self.sys_prompt = PAS_INTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = PAS_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = PAS_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
        elif strategy == "reflexion":
            # Reflexion strategy
            if not interactive:
                if agent_type == "internal":
                    self.sys_prompt = REFLEXION_INTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = REFLEXION_PRIVACY_AWARE_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = REFLEXION_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
            else:
                if agent_type == "internal":
                    self.sys_prompt = REFLEXION_INTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = REFLEXION_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = REFLEXION_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
        elif strategy == "self_consistency":
            # Self-Consistency uses same prompts as ReAct (difference is in multi-path execution)
            if not interactive:
                if agent_type == "internal":
                    self.sys_prompt = SC_INTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = SC_PRIVACY_AWARE_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = SC_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
            else:
                if agent_type == "internal":
                    self.sys_prompt = SC_INTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = SC_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = SC_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
        elif strategy == "tree_of_thought":
            # Tree-of-Thought strategy
            if not interactive:
                if agent_type == "internal":
                    self.sys_prompt = TOT_INTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = TOT_PRIVACY_AWARE_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = TOT_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
            else:
                if agent_type == "internal":
                    self.sys_prompt = TOT_INTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = TOT_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = TOT_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
        elif strategy == "step_back":
            # Step-Back strategy
            if not interactive:
                if agent_type == "internal":
                    self.sys_prompt = STEP_BACK_INTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = STEP_BACK_PRIVACY_AWARE_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = STEP_BACK_EXTERNAL_PROMPT.format(system_description=schema, system="Salesforce instance")
            else:
                if agent_type == "internal":
                    self.sys_prompt = STEP_BACK_INTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                else:
                    if privacy_aware_prompt:
                        self.sys_prompt = STEP_BACK_PRIVACY_AWARE_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
                    else:
                        self.sys_prompt = STEP_BACK_EXTERNAL_INTERACTIVE_PROMPT.format(system_description=schema, system="Salesforce instance")
        else:
            # act strategy
            self.sys_prompt = ACT_PROMPT.format(system_description=schema, system="Salesforce instance")
        
        self.agent_type = agent_type
        self.original_model_name = model
        self.model = model
        self.eval_mode = eval_mode
        self.max_turns = max_turns
        self.strategy = strategy
        self.info = {}
        self.usage = {"cost": [], "completion_tokens": [], "prompt_tokens": [], "total_tokens": []}
        self.provider = provider
       
        if provider == "bedrock" and self.model in BEDROCK_MODELS_MAP:
            os.environ["AWS_REGION_NAME"] = BEDROCK_MODELS_MAP[self.model]["region"]
            self.model = BEDROCK_MODELS_MAP[self.model]["name"]
        elif provider == "together_ai" and self.model in TOGETHER_MODELS_MAP:
            self.model = TOGETHER_MODELS_MAP[self.model]["name"]
        elif "vertex" in provider and self.model in VERTEX_MODELS_MAP:
            self.model = VERTEX_MODELS_MAP[self.model]["name"]
        elif provider == "local":
            self.model = f"openai/{self.model}"
        else:
            pass
        if self.model in ["o1-mini", "o1-preview", "o1-2024-12-17", "o3-mini-2025-01-31"]:
            import litellm
            
            litellm.drop_params=True
            print("dropping parameters")
            
            # assert self.model in ["o1-mini", "o1-preview", "gpt-4o-2024-08-06", "gpt-3.5-turbo-0125"], "Invalid model name"
    
    def _build_schema(self, schema_obj):
        object_description = dict()
        for item in schema_obj:
            object_description[item["object"]] = "\n".join([f"  - {k}: {v}" for k,v in item["fields"].items()])
            
        template = SCHEMA_STRING.format(
            object_names=", ".join(object_description.keys()),
            object_fields="\n".join(
                [f"{obj}\n{fields}" for obj, fields in object_description.items()]
            )
        )
        # Append shared SOQL reference guide (same for all strategies)
        template += "\n" + SOQL_REFERENCE
        return template
    
    def reset(self, args):
        if args["metadata"]["required"]:
            self.sys_prompt += SYSTEM_METADATA.format(system_metadata=args["metadata"]["required"], system="Salesforce instance")
        if self.eval_mode == "aided" and "optional" in args["metadata"]:
            self.sys_prompt += "\n" + args["metadata"]["optional"]
        if self.original_model_name not in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31", "gemini-2.5-flash-preview-04-17"]:
            self.messages = [{"role": "system", "content": self.sys_prompt.strip()}]
            self.messages.append({"role": "user", "content": args["query"].strip()})
        
        else:
            # No system role for o1-mini and o1-preview
            self.messages = [{"role": "user", "content": self.sys_prompt + "\n\n" + args["query"]}]
        self.usage = {"cost": [], "completion_tokens": [], "prompt_tokens": [], "total_tokens": []}
        
    def act(self, env, index=None, temperature=0.0):
        # Route to specialized methods for multi-call strategies
        if self.strategy == "self_consistency":
            return self.act_self_consistency(env, index)
        elif self.strategy == "tree_of_thought":
            return self.act_tree_of_thought(env, index)
        return self.act_single_path(env, index, temperature)

    def act_single_path(self, env, index=None, temperature=0.0):
        query, metadata = env.reset(task_index=index)
        self.reset({"query": query, "metadata": metadata})
        # print("----")
        # print(self.sys_prompt)
        # print("----")
        total_cost = 0.0
        self.info["observation_sizes"] = []
        done = False
        reward = 0
        
        current_agent_turn = 0
        # for turn_id in range(self.max_turns):
        while current_agent_turn < self.max_turns:
            # sleep for non-openai models
            if self.provider != "openai":
                time.sleep(5)
            info = {}
            current_agent_turn += 1
            # turn off thinking for gemini 2.5 flash
            if self.original_model_name == "gemini-2.5-flash-preview-04-17":
                thinking = {"type": "disabled", "budget_tokens": 0}
            elif self.original_model_name == "gemini-2.5-flash-preview-04-17-thinking-4096":
                thinking = {"type": "enabled", "budget_tokens": 4096}
            else:
                thinking = None
            
            res = completion(
                messages=self.messages,
                model=self.model,
                temperature=0.0,
                max_tokens=2000 if self.original_model_name not in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-preview-04-17-thinking-4096", "gemini-2.5-pro-preview-03-25"] else 50000,
                top_p=1.0 if self.model not in ["o3-mini-2025-01-31"] else None,
                thinking= thinking,  
                # custom_llm_provider=self.provider,
                additional_drop_params=["temperature"] if self.original_model_name in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31"] else []
            )

            
            
            message = res.choices[0].message.model_dump()
            
            
            usage = res.usage

            for key in self.usage.keys():
                if key != "cost":
                    self.usage[key].append(usage.get(key, 0))

            self.usage["cost"].append(res._hidden_params["response_cost"])
            action = self.message_action_parser(message, self.model)
            print("User Turn:", env.current_user_turn, "Agent Turn:", current_agent_turn, "Agent:", message["content"].strip())
            self.messages.append({"role": "assistant", "content": message["content"].strip()})
            if action is None:
                self.info["end_reason"] = {
                    "source": "agent",
                    "message": "Invalid action",
                    "content":  message["content"].strip()
                }
                info["end_reason"] = self.info["end_reason"]
                if self.strategy == "react":
                    self.messages.append({"role": "user", "content": REACT_RULE_STRING})
                elif self.strategy == "plan_and_solve":
                    self.messages.append({"role": "user", "content": PAS_RULE_STRING})
                elif self.strategy == "reflexion":
                    self.messages.append({"role": "user", "content": REFLEXION_RULE_STRING})
                elif self.strategy == "self_consistency":
                    self.messages.append({"role": "user", "content": SC_RULE_STRING})
                elif self.strategy == "tree_of_thought":
                    self.messages.append({"role": "user", "content": TOT_RULE_STRING})
                elif self.strategy == "step_back":
                    self.messages.append({"role": "user", "content": STEP_BACK_RULE_STRING})
                elif self.strategy == "act":
                    self.messages.append({"role": "user", "content": ACT_RULE_STRING})
                continue
            obs, reward, done, info = env.step(action)
            
            if "observation_size" in info:
                self.info["observation_sizes"].append(info["observation_size"])
            if "end_reason" in info: # implies error in query
                self.info["end_reason"] = info["end_reason"]
            # reset counter if previous action is respond
            if action["name"] == "respond":
                current_agent_turn = 0
            if done:
                break
            elif action["name"] == "execute": # execution results from
                self.messages.append({"role": "user", "content": f"Salesforce instance output: {obs}"})
            elif action["name"] == "respond": # respond to simulated user
                self.messages.append({"role": "user", "content": obs})
        
        # Here when either max_turns is reached or submitted
        if not done: 
            if "end_reason" not in info: # no error in last query
                self.info["end_reason"] = {
                    "source": "agent",
                    "message": "Max turns reached",
                    "content":  message["content"].strip()
                }
        self.info["usage"] = self.usage
        self.info["total_cost"] = sum(cost for cost in self.usage["cost"] if cost is not None)
        self.info["num_turns"] = (env.current_user_turn, current_agent_turn + 1)
        return reward

    def act_self_consistency(self, env, index=None):
        """
        Self-Consistency: Run N independent reasoning paths, majority-vote the answer.
        Each path is a full act_single_path() run with temperature > 0 for diversity.
        """
        import copy
        from collections import Counter

        answers = []
        all_paths = []

        for path_idx in range(SC_NUM_PATHS):
            print(f"\n--- SC Path {path_idx + 1}/{SC_NUM_PATHS} ---")
            # Create a fresh copy of the agent state for each path
            original_sys_prompt = copy.deepcopy(self.sys_prompt)
            
            # Run a full single-path execution with temperature for diversity
            reward = self.act_single_path(env, index, temperature=SC_TEMPERATURE)
            
            # Extract the final answer from this path
            final_answer = None
            for msg in reversed(self.messages):
                if msg["role"] == "assistant":
                    resp = parse_wrapped_response(r'<respond>(.*?)</respond>', msg["content"]).strip()
                    if resp:
                        final_answer = resp
                        break
            
            if final_answer:
                answers.append(final_answer)
            all_paths.append({"messages": copy.deepcopy(self.messages), "answer": final_answer, "reward": reward})
            
            # Reset for next path
            self.sys_prompt = original_sys_prompt

        # Majority vote
        if answers:
            vote_counts = Counter(answers)
            best_answer = vote_counts.most_common(1)[0][0]
            print(f"\n--- SC Majority Vote: {best_answer} (from {len(answers)} paths) ---")
            print(f"    Votes: {dict(vote_counts)}")
            
            # Use the path that produced the winning answer
            for path in all_paths:
                if path["answer"] == best_answer:
                    self.messages = path["messages"]
                    break
            
            # Re-evaluate with the majority answer
            # The reward from the winning path is our final reward
            return path["reward"]
        else:
            # No paths produced an answer
            self.info["end_reason"] = {"source": "agent", "message": "SC: No paths produced an answer"}
            return 0

    def act_tree_of_thought(self, env, index=None):
        """
        Tree-of-Thought: At each turn, generate multiple candidate queries,
        evaluate them, and execute the best one. Backtrack on failures.
        """
        query, metadata = env.reset(task_index=index)
        self.reset({"query": query, "metadata": metadata})

        self.info["observation_sizes"] = []
        done = False
        reward = 0
        current_agent_turn = 0
        failed_queries = []  # Track failed queries for backtracking

        while current_agent_turn < self.max_turns:
            if self.provider != "openai":
                time.sleep(5)
            info = {}
            current_agent_turn += 1

            # Step 1: Generate candidates by asking for multiple approaches
            gen_messages = list(self.messages)
            if failed_queries:
                backtrack_note = f"\nPrevious failed queries (DO NOT repeat these): {failed_queries}"
                gen_messages.append({"role": "user", "content": backtrack_note})
            gen_messages.append({"role": "user", "content": TOT_GENERATOR_SUFFIX.format(n_candidates=TOT_NUM_CANDIDATES)})

            if self.original_model_name == "gemini-2.5-flash-preview-04-17":
                thinking = {"type": "disabled", "budget_tokens": 0}
            elif self.original_model_name == "gemini-2.5-flash-preview-04-17-thinking-4096":
                thinking = {"type": "enabled", "budget_tokens": 4096}
            else:
                thinking = None

            res = completion(
                messages=gen_messages,
                model=self.model,
                temperature=0.3,  # Slight diversity for candidates
                max_tokens=2000 if self.original_model_name not in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-preview-04-17-thinking-4096", "gemini-2.5-pro-preview-03-25"] else 50000,
                top_p=1.0 if self.model not in ["o3-mini-2025-01-31"] else None,
                thinking=thinking,
                additional_drop_params=["temperature"] if self.original_model_name in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31"] else []
            )

            gen_content = res.choices[0].message.content.strip()
            usage = res.usage
            for key in self.usage.keys():
                if key != "cost":
                    self.usage[key].append(usage.get(key, 0))
            self.usage["cost"].append(res._hidden_params["response_cost"])

            # Try to parse candidates
            candidates = []
            for i in range(1, TOT_NUM_CANDIDATES + 1):
                c = parse_wrapped_response(rf'<candidate_{i}>(.*?)</candidate_{i}>', gen_content).strip()
                if c:
                    candidates.append(c)

            # If no candidates found, fall back to standard single-action parsing
            if not candidates:
                # Model didn't follow candidate format — treat as normal turn
                action = self.message_action_parser(res.choices[0].message.model_dump(), self.model)
                print(f"User Turn: {env.current_user_turn} Agent Turn: {current_agent_turn} Agent [ToT-fallback]: {gen_content[:200]}")
                self.messages.append({"role": "assistant", "content": gen_content})

                if action is None:
                    self.messages.append({"role": "user", "content": TOT_RULE_STRING})
                    continue

                obs, reward, done, info = env.step(action)
                if "observation_size" in info:
                    self.info["observation_sizes"].append(info["observation_size"])
                if "end_reason" in info:
                    self.info["end_reason"] = info["end_reason"]
                if action["name"] == "respond":
                    current_agent_turn = 0
                if done:
                    break
                elif action["name"] == "execute":
                    self.messages.append({"role": "user", "content": f"Salesforce instance output: {obs}"})
                elif action["name"] == "respond":
                    self.messages.append({"role": "user", "content": obs})
                continue

            # Step 2: Evaluate candidates — pick the best one
            # Use a simple heuristic: pick the first candidate not in failed_queries
            best_candidate = None
            for c in candidates:
                if c not in failed_queries:
                    best_candidate = c
                    break
            if not best_candidate:
                best_candidate = candidates[0]  # All failed before, try first anyway

            print(f"User Turn: {env.current_user_turn} Agent Turn: {current_agent_turn} Agent [ToT]: Candidates={len(candidates)}, Selected: {best_candidate[:80]}")

            # Step 3: Execute the best candidate
            action = {"name": "execute", "content": best_candidate}
            self.messages.append({"role": "assistant", "content": f"<thought> Evaluated {len(candidates)} candidates. Best approach: </thought>\n<execute> {best_candidate} </execute>"})

            obs, reward, done, info = env.step(action)

            if "observation_size" in info:
                self.info["observation_sizes"].append(info["observation_size"])
            if "end_reason" in info:
                self.info["end_reason"] = info["end_reason"]

            if done:
                break

            # Check if the query failed — add to backtrack list
            obs_str = str(obs)
            if "ERROR" in obs_str or "INVALID" in obs_str or "MALFORMED" in obs_str:
                failed_queries.append(best_candidate)
                self.messages.append({"role": "user", "content": f"Salesforce instance output: {obs_str}\n[This query failed. Try a different approach.]"})
            else:
                self.messages.append({"role": "user", "content": f"Salesforce instance output: {obs_str}"})

            # After getting results, do a normal turn to decide next action or respond
            if self.provider != "openai":
                time.sleep(5)
            current_agent_turn += 1

            res2 = completion(
                messages=self.messages,
                model=self.model,
                temperature=0.0,
                max_tokens=2000 if self.original_model_name not in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-preview-04-17-thinking-4096", "gemini-2.5-pro-preview-03-25"] else 50000,
                top_p=1.0 if self.model not in ["o3-mini-2025-01-31"] else None,
                thinking=thinking,
                additional_drop_params=["temperature"] if self.original_model_name in ["o1-mini", "o1-preview", "o1-2024-12-17", "deepseek-r1", "o3-mini-2025-01-31"] else []
            )

            msg2 = res2.choices[0].message.model_dump()
            usage2 = res2.usage
            for key in self.usage.keys():
                if key != "cost":
                    self.usage[key].append(usage2.get(key, 0))
            self.usage["cost"].append(res2._hidden_params["response_cost"])

            action2 = self.message_action_parser(msg2, self.model)
            print(f"User Turn: {env.current_user_turn} Agent Turn: {current_agent_turn} Agent [ToT-next]: {msg2['content'].strip()[:200]}")
            self.messages.append({"role": "assistant", "content": msg2["content"].strip()})

            if action2 is None:
                self.messages.append({"role": "user", "content": TOT_RULE_STRING})
                continue

            if action2["name"] == "respond":
                obs, reward, done, info = env.step(action2)
                if "end_reason" in info:
                    self.info["end_reason"] = info["end_reason"]
                if action2["name"] == "respond":
                    current_agent_turn = 0
                if done:
                    break
                self.messages.append({"role": "user", "content": obs})
            elif action2["name"] == "execute":
                obs, reward, done, info = env.step(action2)
                if "observation_size" in info:
                    self.info["observation_sizes"].append(info["observation_size"])
                if "end_reason" in info:
                    self.info["end_reason"] = info["end_reason"]
                if done:
                    break
                obs_str2 = str(obs)
                if "ERROR" in obs_str2 or "INVALID" in obs_str2 or "MALFORMED" in obs_str2:
                    failed_queries.append(action2["content"])
                self.messages.append({"role": "user", "content": f"Salesforce instance output: {obs_str2}"})

        if not done:
            if "end_reason" not in info:
                self.info["end_reason"] = {"source": "agent", "message": "Max turns reached"}
        self.info["usage"] = self.usage
        self.info["total_cost"] = sum(cost for cost in self.usage["cost"] if cost is not None)
        self.info["num_turns"] = (env.current_user_turn, current_agent_turn + 1)
        return reward

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    @staticmethod
    def message_action_parser(message: str, model_name: str) -> Dict[str, str]:
        action = None
        content = message["content"].strip()
        # if model_name "deepseek-r1":
        #     content = content.split("</think>")[1]
        resp = parse_wrapped_response(r'<execute>(.*?)</execute>', content).strip()
        if resp:
            action = {"name": "execute", "content": resp}
            return action
        
        resp = parse_wrapped_response(r'<respond>(.*?)</respond>', content).strip()
        if resp:
            action = {"name": "respond", "content": resp}
            return action
        return action
