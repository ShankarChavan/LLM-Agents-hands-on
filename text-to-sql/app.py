# 1. Configuration
import json
import os
from typing import Annotated, Dict
from spider_env import SpiderEnv
from autogen import ConversableAgent, UserProxyAgent, config_list_from_json

os.environ["AUTOGEN_USE_DOCKER"] = "False"
llm_config = {
    "cache_seed": 48,
    "config_list": [{
        "model": os.environ.get("OPENAI_MODEL_NAME", "llama3-70b-8192"), 
        "api_key": os.environ["GROQ_API_KEY"], 
        "base_url": os.environ.get("OPENAI_API_BASE", "https://api.groq.com/openai/v1")}
    ],
}

# 2. Import Data
gym = SpiderEnv()
observation, info = gym.reset()
question = observation["instruction"]
print(question)
schema = info["schema"]
print(schema)

# 3. Create Agents
def check_termination(msg: Dict):
    if "tool_responses" not in msg:
        return False
    json_str = msg["tool_responses"][0]["content"]
    obj = json.loads(json_str)
    return "error" not in obj or obj["error"] is None and obj["reward"] == 1

sql_writer = ConversableAgent(
    "sql_writer",
    llm_config=llm_config,
    system_message="You are good at writing SQL queries. Always respond with a function call to execute_sql().",
    is_termination_msg=check_termination,
)

user_proxy = UserProxyAgent(
    "user_proxy", 
    human_input_mode="NEVER", 
    max_consecutive_auto_reply=5
)

# 4. Create Tools / Function Calling
@sql_writer.register_for_llm(description="Function for executing SQL query and returning a response")
@user_proxy.register_for_execution()
def execute_sql(reflection: Annotated[str, "Think about what to do"], sql: Annotated[str, "SQL query"]) -> Annotated[Dict[str, str], "Dictionary with keys 'result' and 'error'"]:
    observation, reward, _, _, info = gym.step(sql)
    error = observation["feedback"]["error"]
    if not error and reward == 0:
        error = "The SQL query returned an incorrect result"
    if error:
        return { "error": error, "wrong_result": observation["feedback"]["result"], "correct_result": info["gold_result"], }
    else:
        return { "result": observation["feedback"]["result"], }


# 5. Initiate Chat
prompt_template = f"""Below is the schema for a SQL database:
{schema}
Generate a SQL query to answer the following question:
{question}
"""

user_proxy.initiate_chat(sql_writer, message=prompt_template)