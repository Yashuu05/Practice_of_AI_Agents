from langchain.agents import create_agent 
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
import os 
from tavily import TavilyClient
from dotenv import load_dotenv
from ensure import ensure_annotations

load_dotenv()

MAIN_MODEL = "gemini-3.5-flash-lite"
PLANNER_MODEL = "qwen3.5:0.8b"
TRAVEL_MODEL = "openai/gpt-oss-20b"
NLP_MODEL    = "llama3.1:8b"
TAVILTY_KEY = os.getenv("TAVILY_API_KEY")

class SubAgents:

    def __init__(self):
        pass 

    def planner_agent(self):

        # define model
        planner_model = init_chat_model(
            model = PLANNER_MODEL,
            model_provider="ollama"
        )

        # define custom system prompt
        system_msg = SystemMessage("""
            you are a TRIP PLANNER AGENT who is an expert in planning and decision making. 
            your primary task is to create a well defined implemetation plan by analyzing the user requirements.
            This implementation plan will be used by other agent "travel_agent" to implement tasks sequentially.
            IMPLEMENTATION PLAN EXAMPLE:
            - search nearby hotels to Miami for 5 people
            - search top popular places to visit in Miami
            - Search Flight Tickets for 5 people Economic class from Florida to Miami under $$ budget
            - get 3 day weather details in Miami
            - Calculate minimum budget required to visit 3 days in Miami.

            NOTE: given variables in example may change according to user input.
            NOTE: use "available_tool" tool to return available tools. IF TASK in IMPLEMENTATION PLAN cannot executed by existing tools, remove that task.
        """)

        # define agent
        plan_agent = create_agent(
            model=planner_model,
            tools=[available_tool],
            system_prompt=system_msg
        )

        return plan_agent

    def travel_agent(self):
        travel_model = init_chat_model(
            model=TRAVEL_MODEL,
            model_provider="google-genai"
        )

        system_msg = (
            """
            Your are a TRAVEL AGENT whose responsibility is to gather necessary information
            in order to plan the TRIP or JOURNEY.
            FOLLOW all steps included in the IMPLEMENTATION PLAN.
            You are provided with the various tools. Use these tools to gather information as asked in IMPLEMENTATION PLAN.
            USE "available_tools" tool to list available tools to use.
            If NO TOOL is supported to satisfied the given task in IMPLEMENTATION PLAN then return "NO TOOLS FOUND"
            STIRCTLY follow the IMPLEMENTATION PLAN.
            """
        )

        traveller_agent = create_agent(
            model=travel_model,
            tools=[calculator_tool, weather_tool, web_search_tool, available_tool],
            system_prompt=system_msg
        )

        return traveller_agent

# CALCULATOR TOOL
@tool("calculator_tool", description="tool to perform basic arithematic operations")
def calculator_tool(operation: str, num1: float, num2: float) -> float:
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

# WEB SEARCH TOOL
@tool("web_search_tool", description="searches the web")
def web_search_tool(query: str):
    """
    Use this function to search the query on the web to gather information
    Use this tool to search popular places to visit, hotels, flight details and additional information.
    Args:
    query: string to search on the web
    """
    tavily_client = TavilyClient(api_key=TAVILTY_KEY)
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

# WEATHER TOOL
@tool("weather_tool", description="get weather details")
def weather_tool():
    """
    use this tool to get the weather details of given destination place
    """
    pass 

# AVAILABLE TOOL
@tool("available_tool", description="list available tools")
def available_tool(tools : list= ["calculator_tool","weather_tool","search_web_tool"]) -> dict:
    """
    This tool returns available tools only "call_planner_agent" and "call_travel_agent"
    """
    tools_list = {}
    for i in range(len(tools)):
        tools_list[f"tool_{i}"] = tool[i]

    return tools_list

# PLANNER AGENT TOOL
@tool("call_planner_agent", description="this tools creates implementation plan")
def call_planner_agent(user_input) -> str:
    """
    use this tool in first priority to create the implementation plan

    Args:
    query: inputs given by user

    returns:
    implementation plan
    """
    human_msg = HumanMessage(f"Create an Implementation Plan by analyzing following given user inputs:\n{user_input}")
    planner_agent = SubAgents.planner_agent()
    result = planner_agent.invoke(human_msg)
    return result["messages"][-1].content[0]['text']

# TRAVEL AGENT TOOL
@tool("call_travel_agent", description="this tool gathers necessary information")
def call_travel_agent(plan) -> str:
    """
    this tool must be run after the call_planner_agent tool to gather the necessary information
    Strictly provide the plan returned by call_planner_agent tool as an input
    Args:
    query: input to traveller agent

    returns:
    detailed information
    """
    human_msg = HumanMessage(f"As a TRAVEL AGENT implement the task given in the IMPLEMENTATION PLAN. PLAN:\n{plan}")
    planner_agent = SubAgents.travel_agent()
    result = planner_agent.invoke(human_msg)
    return result["messages"][-1].content[0]['text']

## MAIN AGENT--------------------------->
def run_main_agent(user_input: str, tool_lst: list):

        thread_config = {"configurable": {"thread_id": "1"}}

        main_model = init_chat_model(
            model=MAIN_MODEL,
            model_provider="google-genai",
        )

        system_msg = (
            """
            You are a MASTER AGENT working in professional TRAVEL AGENCY.
            You are a CENTRAL UNIT which controls the communication and flow logic between subagents.
            You have two subagents ready to assit called as "call_planner_agent" and "call_travel_agent".
            STRICTLY follow the following sequence:
            Use "call_planner_agent" first to create an IMPLEMENTATION PLAN
            Provide IMPLEMENTATION PLAN to "call_travel_agent" to implement tasks and gather data.
            Use raw data returned by "call_travel_agent" to analyse and generate natrual language response by summarizing raw data.
            Your Response should be structured, clean, and user-friendly to convey TRIP details to user.
            """
        )
        main_agent = create_agent(
            model=main_model, 
            tools=tool_lst,
            system_prompt=system_msg,
            checkpointer=InMemorySaver(),
        )

        human_msg = HumanMessage(f"Provide TRIP or TRAVEL details to user by analysing given inputs:\n{user_input}")
        response = main_agent.invoke(
            human_msg,
            thread_config)["messages"][-1].content[0]['text']

        return response
        
if __name__ == "__main__":

    user_inputs = {
        "source": "Pune City, Maharashtra, India",
        "destination":"Osaka, Japan",
        "departure": "2 September 2026",
        "arrival": "6 September 2026",
        "head count": 4,
        "budget": "INR 250000" 
    }

    # call main agent
    print("PROGRAM INITIATED")
    final_response = run_main_agent(
        user_input=user_inputs,
        tool_lst=[call_planner_agent, call_travel_agent]
    )

    print("==================== AI RESPONSE ======================")
    print(f"\n{final_response}")