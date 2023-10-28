import autogen

config_list = autogen.config_list_from_models(model_list=["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"], exclude="aoai")

config_list = [
    {
        'model': 'gpt-3.5-turbo',
        'api_key': "",
    }
]

llm_config = {
    "functions": [
        {
            "name": "python",
            "description": "run cell in ipython and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cell": {
                        "type": "string",
                        "description": "Valid Python cell to execute.",
                    }
                },
                "required": ["cell"],
            },
        },
        {
            "name": "sh",
            "description": "run a shell script and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Valid shell script to execute.",
                    }
                },
                "required": ["script"],
            },
        },
    ],
    "config_list": config_list,
    "request_timeout": 120,
}
chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

# define functions according to the function description
from IPython import get_ipython

def exec_python(cell):
    ipython = get_ipython()
    result = ipython.run_cell(cell)
    log = str(result.result)
    if result.error_before_exec is not None:
        log += f"\n{result.error_before_exec}"
    if result.error_in_exec is not None:
        log += f"\n{result.error_in_exec}"
    return log

def exec_sh(script):
    return user_proxy.execute_code_blocks([("sh", script)])

# register the functions
user_proxy.register_function(
    function_map={
        "python": exec_python,
        "sh": exec_sh,
    }
)

# start the conversation
user_proxy.initiate_chat(
    chatbot,
    message="Draw two agents chatting with each other with an example dialog. Don't add plt.show().",
)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Define basic parameters
face_color = '#FFDDC1'
plt.figure(figsize=(10, 2))

# Agent 1
agent1 = mpatches.FancyBboxPatch((0.02, 0.4), 0.2, 0.6, boxstyle=mpatches.BoxStyle("Round", pad=0.02))
plt.gca().add_artist(agent1)
plt.gca().text(0.12, 0.7, 'Agent 1', ha='center', va='center', fontsize=12, color='blue')

# Agent 2
agent2 = mpatches.FancyBboxPatch((0.45, 0.4), 0.2, 0.6, boxstyle=mpatches.BoxStyle("Round", pad=0.02))
plt.gca().add_artist(agent2)
plt.gca().text(0.55, 0.7, 'Agent 2', ha='center', va='center', fontsize=12, color='red')

# Dialog
plt.gca().text(0.12, 0.35, '\"Hello, how are you?\"', ha='center', va='center', fontsize=10)
plt.gca().text(0.55, 0.15, '\"I\'m fine, thank you!\"', ha='center', va='center', fontsize=10)

# Descriptions
plt.gca().text(0.12, 0.15, 'Greeting', ha='center', va='center', fontsize=10)
plt.gca().text(0.55, 0.35, 'Response', ha='center', va='center', fontsize=10)

plt.axis('off')

import os
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent

# you need to provide a wolfram alpha app id to run this example
if not os.environ.get("WOLFRAM_ALPHA_APPID"):
    os.environ["WOLFRAM_ALPHA_APPID"] = open("wolfram.txt").read().strip()

llm_config = {
    "model": "gpt-4-0613",
    "functions": [
        {
            "name": "query_wolfram",
            "description": "Return the API query result from the Wolfram Alpha. the return is a tuple of (result, is_success).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Wolfram Alpha code to be executed.",
                    }
                },
                "required": ["query"],
            },
        }
    ],
    "config_list": config_list,
}
chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="Only use the functions you have been provided with. Do not ask the user to perform other actions than executing the functions. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

# the key in `function_map` should match the function name in "functions" above
# we register a class instance method directly
user_proxy = autogen.UserProxyAgent(
    "user_proxy",
    max_consecutive_auto_reply=2,
    human_input_mode="NEVER",
    function_map={"query_wolfram": MathUserProxyAgent().execute_one_wolfram_query},
)

# start the conversation
user_proxy.initiate_chat(
    chatbot,
    message="Problem: Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation.",
)