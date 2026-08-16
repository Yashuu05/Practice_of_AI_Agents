from langchain.agents import create_agent 
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
import os 
import sys 
from tavily import TavilyClient
from dotenv import load_dotenv
import sqlite3
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

MAIN_MODEL = "gemini-3.5-flash-lite"
PLANNER_MODEL = "qwen3.5:0.8b"
TRAVEL_MODEL = "gemini-3.1-flash-lite"
TAVILY_KEY = os.getenv("TAVILY_API_KEY")

class SubAgents:
    @staticmethod
    def planner_agent():
        # define model
        planner_model = init_chat_model(
            model=PLANNER_MODEL,
            model_provider="ollama"
        )

        # define custom system prompt
        system_msg = SystemMessage("""
            you are a TRIP PLANNER AGENT who is an expert in planning and decision making. 
            your primary task is to create a well defined implementation plan by analyzing the user requirements.
            This implementation plan will be used by other agent "travel_agent" to implement tasks sequentially.
            IMPLEMENTATION PLAN EXAMPLE:
            - search nearby hotels to Miami for 5 people
            - search top popular places to visit in Miami
            - Search Flight Tickets for 5 people Economic class from Florida to Miami under budget
            - get weather details in Miami
            - Calculate minimum budget required to visit 3 days in Miami.

            NOTE: given variables in example may change according to user input.
        """)

        # define agent (no tools needed for planner)
        plan_agent = create_agent(
            model=planner_model,
            tools=[],
            system_prompt=system_msg
        )

        return plan_agent

    @staticmethod
    def travel_agent():
        travel_model = init_chat_model(
            model=TRAVEL_MODEL,
            model_provider="google-genai"
        )

        system_msg = SystemMessage("""
            You are a TRAVEL AGENT whose responsibility is to gather necessary information
            in order to plan the TRIP or JOURNEY.
            FOLLOW all steps included in the IMPLEMENTATION PLAN.
            You are provided with various tools. Use these tools to gather information as asked in IMPLEMENTATION PLAN.
            STRICTLY follow the IMPLEMENTATION PLAN and return the gathered information.
        """)

        traveller_agent = create_agent(
            model=travel_model,
            tools=[calculator_tool, weather_tool, web_search_tool],
            system_prompt=system_msg
        )

        return traveller_agent


def fetch_corrdinates(city: str, country: str, db_name:str, table_name: str):
    db_path = os.path.join(project_root,"Travel_Agent","db",f"{db_name}")

    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if city and country=="":
                cursor.execute(f"""
                    SELECT latitude, longitude
                    FROM {table_name}
                    WHERE City LIKE '%{city}%'
                """)
                return cursor.fetchall()

            elif country and city=="":
                cursor.execute(f"""
                    SELECT latitude, longitude
                    FROM {table_name}
                    WHERE Country LIKE '%{country}%'
                """)
                return cursor.fetchall()

            elif city and country:
                cursor.execute(f"""
                    SELECT latitude, longitude
                    FROM {table_name}
                    WHERE City LIKE '%{city}%' AND Country LIKE '%{country}%'
                """)
                return cursor.fetchall()

            else:
                return "Error: No value for city and country provided"
    except Exception as e:
        return e

# CALCULATOR TOOL
@tool("calculator_tool", description="Tool to perform basic arithmetic operations. Input operations: 'add', 'subtract', 'multiply', 'divide'")
def calculator_tool(operation: str, num1: float, num2: float) -> float:
    """Performs basic mathematical operations."""
    print("using calculator tool...")
    if operation == 'add': return num1 + num2
    elif operation == 'subtract': return num1 - num2
    elif operation == 'multiply': return num1 * num2
    elif operation == 'divide':
        if num2 == 0: raise ValueError("Cannot divide by zero")
        return num1 / num2
    else: raise ValueError(f"Unsupported operation: {operation}")

# WEB SEARCH TOOL
@tool("web_search_tool", description="Searches the web for places, flights, and hotels")
def web_search_tool(query: str):
    """Use this function to search the query on the web to gather information."""

    print(f"using web search to query: {query}")
    if not TAVILY_KEY:
        return "No API KEY found to access the web"
    
    tavily_client = TavilyClient(api_key=TAVILY_KEY)
    try:
        response = tavily_client.search(query)
        if not response.get('results'):
            return "No results found on the web."
        
        # Format results as string to avoid passing dicts directly
        results = [res['content'] for res in response['results']]
        return "\n".join(results)
    except Exception as e:
        return f"Error: {e}"

# weather tool
@tool("weather_tool", description="Get weather details for a destination")  
def weather_tool(forcast_days: int=3, city:str="", country: str="") -> dict:
    """
    This tool returns weather details for specific city or country
    """
    try:
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)
        url = "https://api.open-meteo.com/v1/forecast"

        ## get latitude and longitude from sqlite database 
        result= fetch_corrdinates(city=city, 
                    country=country, 
                    db_name="TouristPlace.db", 
                    table_name="coordinates")
        lat, long = result[0]

        params = {
	    "latitude": lat,
	    "longitude": long,
	    "daily":["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
	    "forecast_days": forcast_days,
        }
        responses = openmeteo.weather_api(url, params = params)

        response = responses[0]
        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()

        daily_data = {
	        "date": pd.date_range(
		        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
		        end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
		        freq = pd.Timedelta(seconds = daily.Interval()),
		        inclusive = "left"
	        )
        }

        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["precipitation_sum"] = daily_precipitation_sum

        daily_dataframe = pd.DataFrame(data = daily_data)
        daily_dict = daily_dataframe.to_dict()
        return daily_dict

    except Exception as e:
        return e

# EXTRACT CONTENT HELPER
def extract_content(result_dict):
    """Helper to robustly extract text content from agent invoke response."""
    try:
        content = result_dict["messages"][-1].content
        if isinstance(content, list):
            return content[0].get('text', str(content))
        return content
    except Exception as e:
        return str(result_dict)

# PLANNER AGENT TOOL
@tool("call_planner_agent", description="Creates an implementation plan by analyzing user requirements")
def call_planner_agent(user_input: str) -> str:
    """Use this tool in first priority to create the implementation plan."""
    human_msg = HumanMessage(f"Create an Implementation Plan by analyzing following given user inputs:\n{user_input}")
    planner_agent = SubAgents.planner_agent()
    result = planner_agent.invoke(human_msg)
    return extract_content(result)

# TRAVEL AGENT TOOL
@tool("call_travel_agent", description="Gathers necessary information based on the plan")
def call_travel_agent(plan: str) -> str:
    """This tool must be run after the call_planner_agent tool to gather the necessary information."""
    human_msg = HumanMessage(f"As a TRAVEL AGENT implement the task given in the IMPLEMENTATION PLAN. PLAN:\n{plan}")
    travel_agent = SubAgents.travel_agent()
    result = travel_agent.invoke(human_msg)
    return extract_content(result)

## MAIN AGENT--------------------------->
def run_main_agent(user_input: dict):

    thread_config = {"configurable": {"thread_id": "1"}}

    main_model = init_chat_model(
        model=MAIN_MODEL,
        model_provider="google-genai",
    )

    system_msg = SystemMessage("""
        You are a MASTER AGENT working in a professional TRAVEL AGENCY.
        You are a CENTRAL UNIT which controls the communication and flow logic between subagents.
        You have two subagents ready to assist: "call_planner_agent" and "call_travel_agent".
        STRICTLY follow this sequence:
        1. Use "call_planner_agent" first to create an IMPLEMENTATION PLAN based on user input.
        2. Provide the IMPLEMENTATION PLAN to "call_travel_agent" to implement tasks and gather data.
        3. Use raw data returned by "call_travel_agent" to analyze and generate a final natural language response summarizing the TRIP details.
        Your Response should be structured, clean, and user-friendly.
    """)

    main_agent = create_agent(
        model=main_model, 
        tools=[call_planner_agent, call_travel_agent],
        system_prompt=system_msg,
        checkpointer=InMemorySaver(),
    )

    input_str = "\n".join([f"{k}: {v}" for k, v in user_input.items()])
    human_msg = HumanMessage(f"Provide TRIP or TRAVEL details to user by analyzing given inputs:\n{input_str}")
    
    response = main_agent.invoke(human_msg, thread_config)
    return extract_content(response)
        
if __name__ == "__main__":
    user_inputs = {
        "source": "Pune City, Maharashtra, India",
        "destination": "Osaka, Japan",
        "departure": "2 September 2026",
        "arrival": "6 September 2026",
        "head count": 4,
        "budget": "INR 250000" 
    }

    print("==================== PROGRAM INITIATED ======================")
    final_response = run_main_agent(user_inputs)

    print("\n==================== AI RESPONSE ======================")
    print(f"\n{final_response}")