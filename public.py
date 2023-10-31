import autogen
from autogen.agentchat import AssistantAgent, UserProxyAgent

import os
from SearchOrAccessGithubCodebase import *
from dotenv import load_dotenv
from dotenv import dotenv_values

from langchain.document_loaders import ConfluenceLoader, GitLoader, TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.agents.agent_toolkits.github.toolkit import GitHubToolkit
from langchain.utilities.github import GitHubAPIWrapper
from langchain.document_loaders import GitLoader
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.agent_toolkits import FileManagementToolkit

# Load environment variables from .env file
if os.path.exists(".env"):
    load_dotenv(override=True)
    env = dotenv_values(".env")

# Setup embeddings
embeddings_chunk_size = 16
embeddings_deployment = "text-embedding-ada-002"
embedding = OpenAIEmbeddings(
    deployment=embeddings_deployment,
    chunk_size=embeddings_chunk_size)

github_persist_directory = "chroma/" + env["GITHUB_BASE_BRANCH"]

if os.path.exists(github_persist_directory):
    # Load a Chroma vector store
    github_vectordb = Chroma(
        persist_directory=github_persist_directory, embedding_function=embedding)

elif env["GITHUB_LOCAL_DIR"]:
    loader = GitLoader(
        clone_url="https://github.com/" + env["GITHUB_REPOSITORY"],
        repo_path="./" + env["GITHUB_LOCAL_DIR"],
        branch=env["GITHUB_BASE_BRANCH"]
        # file_filter=lambda file_path: file_path.endswith(".tf"),
    )
    data = loader.load_and_split()

    # Create a Chroma vector store
    github_vectordb = Chroma.from_documents(
        documents=data, embedding=embedding, persist_directory=github_persist_directory)

config_list = [
    {
        'model': env["AZURE_OPENAI_MODEL"],
        'api_key': env["AZURE_OPENAI_KEY"],
        'api_base': env["AZURE_OPENAI_BASE"],
        'api_type': 'azure',
        'api_version': '2023-07-01-preview',
    },
]

# Define a function to generate llm_config from a LangChain tool


def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.replace(' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args

    return function_schema


if github_vectordb is None:
    print("No vector store found")
    exit

retriever = github_vectordb.as_retriever(search_kwargs={"score_threshold": .5})
search_codebase = SearchOrAccessGithubCodebase(retriever=retriever)

# Now use AutoGen with Langchain Tool
functions = []
function_map = {}
github = GitHubAPIWrapper()
gitHubToolkit = GitHubToolkit.from_github_api_wrapper(github)
fileManagementToolkit = FileManagementToolkit(
    root_dir=str("./" + env["GITHUB_LOCAL_DIR"])
) 
tools = [search_codebase, *gitHubToolkit.get_tools(), *fileManagementToolkit.get_tools()]

for tool in tools:
    tool_schema = generate_llm_config(tool)
    print(tool_schema)
    functions.append(tool_schema)
    function_map[tool.name.replace(' ', '_')] = tool._run


# user_proxy.initiate_chat(assistant, message="Hi")
llm_config = {
    "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
    "functions": functions,
    # "max_tokens": 8192,
}

user_proxy = UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    # human_input_mode="TERMINATE",
    human_input_mode="ALWAYS",
)
# Register the tool and start the conversation
user_proxy.register_function(
    function_map=function_map
)

coder = AssistantAgent(
    name="Coder",
    is_termination_msg=lambda x: True if "TERMINATE" in x.get(
        "content") else False,
    llm_config=llm_config,
)

# 1) All tasks
# user_proxy.initiate_chat(coder, message="You are tasked with completing issues on a github repository. Please look at the existing issues and complete them.")

# 2) Specific Task
# issue = github.get_issue(296)

# prompt = f"""
# You have been assigned the below issue. Complete it to the best of your ability.
# Remember to first make a plan and pay attention to details like file names and commonsense.
# Then execute the plan and use tools appropriately.
# Finally, make a pull request to merge your changes.
# Issue: {issue["title"]}
# Issue Description: {issue['body']}
# Comments: {issue['comments']}"""

# user_proxy.initiate_chat(coder, message=prompt)

#3) Generic task
user_proxy.initiate_chat(coder, message="Review the local git repo (path 'storybook-design-system') for possible improvements. It is a Storybook project coded in React/Javascript and yarn storybook is the primary way to run it.")