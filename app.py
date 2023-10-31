from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen import UserProxyAgent
from autogen import config_list_from_json
from chromadb.utils import embedding_functions
from langchain.text_splitter import SpacyTextSplitter
from spacy import load


nlp = load("en_core_web_sm")

config_list = config_list_from_json('OAI_CONFIG_LIST.json')

llm_config={
    "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}


assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=config_list[0]['api_key'], model_name="text-embedding-ada-002")

spacy_splitter = SpacyTextSplitter()

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    retrieve_config={
        "task": "qa",
        "docs_path": "https://raw.githubusercontent.com/microsoft/autogen/main/README.md",
        "custom_text_split_function": spacy_splitter.split_text,
        "embedding_function": openai_ef,
    },
)

assistant.reset()
ragproxyagent.initiate_chat(assistant, problem="What is autogen?")

assistant.reset()
userproxyagent = UserProxyAgent(name="userproxyagent")
userproxyagent.initiate_chat(assistant, message="What is autogen?")


