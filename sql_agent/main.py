from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from sql_agent.sql_tools import *
load_dotenv()
class SQLAgent:

    def __init__(self):
        self.config = {"configurable": {"thread_id": "sql_thread_1"}}

    def init_memory(self):
        memory = InMemorySaver()
        return memory

    def read_system_prompt(self, path=os.path.join(project_root, "sql_agent", "system_prompt.md")):
        try:
            with open(file=path, mode="r", encoding="utf-8") as f:
                system_prompt = f.read()
            if system_prompt:
                print("System Prompt read successful.")
                return system_prompt.format(top_k=5)
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def run_sql_agent(self, input_prompt: str):

        # 1. define agent
        gemini_model = init_chat_model(
                model="gemini-3.5-flash-lite",
            model_provider="google-genai",
            temperature=0.5
        )

        # 2. define agent
        sql_agent = create_agent(
            model=gemini_model,
            tools=[sql_db_list_tables, sql_db_schema, sql_db_query, sql_db_query_checker],
            system_prompt=self.read_system_prompt() or "",
            checkpointer=self.init_memory()
        )
        
        stream = sql_agent.stream(
            {"messages": [{"role": "user", "content": input_prompt}]},
            self.config,
            stream_mode="values"
        )
        for event in stream:
            event["messages"][-1].pretty_print()

        final_state = event


if __name__ == "__main__":
    print("Agent Initiated.")
    user_input = "Which Region has highest Profit?"
    obj = SQLAgent()
    obj.run_sql_agent(input_prompt=user_input)