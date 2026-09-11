from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage, SystemMessage

class ContentAgent:
    def __init__(self):
        self.config = {"configurable": {"thread_id": "content_thread_1"}}

    DEFAULT_MODEL = "qwen3:8b"
    REQUIREMENT_AGENT_MODEL = "qwen3:8b"
    SCRIPT_AGENT_MODEL = "gemini-3.5-flash" 
    RESEARCH_AGENT_MODEL = "openai/gpt-oss-20b"
    EVALUATION_AGENT_MODEL = "qwen3:8b"

    