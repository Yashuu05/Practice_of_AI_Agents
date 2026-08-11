from ensure import ensure_annotations
from langchain.agents import create_agent
from tavily import TavilyClient
import os 
from langchain.tools import tool
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")

@tool(name_or_callable="web_search", description="searches the web")
def web_search(query: str):
    """
    Use this function to search the query on the web to gather information

    Args:
        query: query to search on web 
    """
    tavily_client = TavilyClient(api_key=tavily_key)
    try:
        if not tavily_client:
            return "No API KEY found to access the web"
        else: 
            response = tavily_client.search(query)
            if not response.get('results'):
                return "No results found on the web."
            return response
    except Exception as e:
        return f"{e}"

@tool(name_or_callable="calculator", description="performs arithmatic operations")
def calculator(operation: str, num1: float, num2: float) -> float:
    """Performs basic mathematical operations.
    
    Args:
        operation: The operation to perform ('add', 'subtract', 'multiply', 'divide').
        num1: The first number.
        num2: The second number.
    """
    if operation == 'add':
        return num1 + num2
    elif operation == 'subtract':
        return num1 - num2
    elif operation == 'multiply':
        return num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            raise ValueError("Cannot divide by zero")
        return num1 / num2
    else:
        raise ValueError(f"Unsupported operation: {operation}")

# create list of availble tools to use
tools_to_use = [web_search, calculator]

class PersonalChefAgent:

    def __init__(self):
        self.config = {"configurable": {"thread_id": "chef_thread_1"}}

    @ensure_annotations
    def define_model(self, model_name: str, model_provider: str):
        """
        - defines LLM to act as a central brain of agent
        - inputs:
        1. model_name: name of LLM or model
        2. model_provider: name of provider of whom LLM you are using
        3. temp: temperature of LLM from 0 to 1 (default is 0.5)
        - output: model object
        """

        model = init_chat_model(
            model=model_name,
            model_provider=model_provider
        )
        return model

    def init_memory(self):
        memory = InMemorySaver()
        return memory

    @ensure_annotations
    def run_chef_agent(self, llm, user_query: str, tool_lst: list, system_intruction: str):
        """
        - defines agent and runs it
        - inputs:
        1. llm: pre-defined LLM model object
        2. user_query: user prompt
        3. tool_lst: list of tools for agent use
        4. system_intruction: custom system prompt to LLM
        """
        # define agent
        agent = create_agent(
            model=llm,
            tools=tool_lst,
            system_prompt=system_intruction,
            checkpointer = self.init_memory(),
        )
        # user prompt
        question = HumanMessage(content=f"{user_query}")
        # run agent 
        response = agent.invoke(
            {'messages':[question]},
            config=self.config,
        )
        print(response['messages'][-1].content[0]['text'])

if __name__ == "__main__":

    system_prompt = """
    You are a personal chef. The user will give you a list of ingredients they have left over in their house.
    Using the "web_search" tool, search the web for recipes that can be made with the ingredients they have.
    Use "calculator" tool to calculate the amount ingredients required. 
    Return concise recipe suggestions in smaller maneagable steps.
    """
    chef = PersonalChefAgent()

    # 1. define LLM
    print("defining model....")
    LLM = chef.define_model(
        model_name="gemini-3.5-flash-lite",
        model_provider="google-genai"
    )

    # 2. run agent
    print("running agent...")
    chef.run_chef_agent(
        llm=LLM,
        user_query="I have some leftover chicken and rice. What can I make?",
        tool_lst=tools_to_use,
        system_intruction = system_prompt
    )