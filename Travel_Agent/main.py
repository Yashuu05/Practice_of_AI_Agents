from langchain.agents import create_agent 
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
import os 
import sys 
from tavily import TavilyClient
from dotenv import load_dotenv
import serpapi
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils import get_iata_by_city, fetch_corrdinates

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
            tools=[calculator_tool, weather_tool, web_search_tool, fetch_and_extract_hotels, fetch_flights],
            system_prompt=system_msg
        )

        return traveller_agent

# fetch hotel details
@tool("hotel_tool", description="fetch hotel details for given place")
def fetch_and_extract_hotels(place:str, check_in_date:None | str, check_out_date:None|str, adults:int, hotel_class:int, limit:int=3):
    """
    Fetches hotel data from Google Hotels API using SerpApi and extracts structured, useful information.
    
    Args:
    - place: name of place to search hotels in.
    - check_in_date: hotel check in date
    - check_out_date: hotel check out date
    - adults: number of adults
    - hotel_class: class hotel (1 to 5)
    - limit: number of search results (1 to 5)
    """
    serpapi_key = os.getenv("SERPAPI_KEY")
    
    if not serpapi_key:
        print("Error: No API key found. Please set SERPAPI_API in your .env file.")
        return None
        
    client = serpapi.Client(api_key=serpapi_key)
    try:
        print(f"API KEY founf. Fetching hotel details for {place}...")
        # Fetch raw results
        results = client.search({
            "engine": "google_hotels",
            "q": f"hotels nearby {place}",
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": adults,
            "hotel_class": hotel_class,
            "currency": "INR" 
        })

        properties = results.get("properties", [])
        extracted_data = []
        
        # Extract structured data and limit the results
        for prop in properties[:limit]:
            hotel_info = {
                "name": prop.get("name"),
                "type": prop.get("type"),
                "description": prop.get("description", "No description available"),
                "rating": prop.get("overall_rating", "N/A"),
                "reviews_count": prop.get("reviews", 0),
                "price_per_night": prop.get("rate_per_night", {}).get("lowest"),
                "total_price": prop.get("total_rate", {}).get("lowest"),
                "link": prop.get("link", prop.get("serpapi_property_details_link")),
                "amenities": prop.get("amenities", [])[:5], # Limit to top 5 amenities
                "gps_coordinates": prop.get("gps_coordinates")
            }
            extracted_data.append(hotel_info)
            
        return extracted_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@tool("fetch_flights", description="fetch flight details")
def fetch_flights(outbound_date, return_date=None, dest_city="",dest_country="",source_city="", source_country="",trip_type="2", adults:int=1, travel_class="1"):
    """
    Fetch flight details using Serpapi Google Flights API.

    Parameters:
    - outbound_date: str, format "YYYY-MM-DD"
    - return_date: str, format "YYYY-MM-DD" (optional, required if trip_type is "1")
    - dest_city: str, destination city 
    - dest_country: str, destination country
    - source_city: str, source city
    - source_country: str, source country
    - trip_type: str, "1" for Round trip, "2" for One way
    - adults: int, number of adult passengers
    - travel_class: str, "1" (Economy), "2" (Premium economy), "3" (Business), "4" (First)
    """
    # Retrieve API key from environment
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("Error: SERPAPI_KEY not found in environment variables.")
        return None
    try:

        client = serpapi.Client(api_key=api_key)
        print("API KEY found. Implementing flight search...")

        # get departure_id and arrival_id for source place
        print("fetching arrival_id...")
        arrival_code, airport_arrival = get_iata_by_city(
            city_name=source_city,
            country_name=source_country,
            db_path=os.path.join(project_root, "db", "CityCode.db")
        )
        print("fetching departure_id...")
        departure_code, airport_destination = get_iata_by_city(
            city_name=dest_city,
            country_name=dest_country,
            db_path=os.path.join(project_root, "db", "CityCode.db")
        )
        if departure_code and arrival_code:
            print(f"arrival_id:{arrival_code}, departure_id: {departure_code}")
            # Base parameters for the search
            params = {
            "engine": "google_flights",
            "departure_id": departure_code,
            "arrival_id": arrival_code,
            "outbound_date": outbound_date,
            "type": trip_type,
            "adults": str(adults),
            "travel_class": travel_class,
            "currency": "USD",
            "hl": "en",
            "gl": "us"
            }

            # Add return date if round trip is selected
            if trip_type == "1" and return_date:
                params["return_date"] = return_date

            try:
                print(f"Fetching flights from {departure_code} to {arrival_code} on {outbound_date}...")
                results = client.search(params)
        
                # Structure the extracted data
                structured_data = {
                    "best_flights": [],
                    "price_insights": results.get("price_insights", {})
                }

                # Extract 3 best flights
                if "best_flights" in results:
                    for flight in results["best_flights"][:3]:
                        flight_info = {
                        "airline": flight.get("flights", [{}])[0].get("airline", "Unknown"),
                        "flight_number": flight.get("flights", [{}])[0].get("flight_number", "Unknown"),
                        "departure_airport": flight.get("flights", [{}])[0].get("departure_airport", {}).get("id", departure_code),
                        "arrival_airport": flight.get("flights", [{}])[-1].get("arrival_airport", {}).get("id", arrival_code),
                        "departure_time": flight.get("flights", [{}])[0].get("departure_time", "Unknown"),
                        "arrival_time": flight.get("flights", [{}])[-1].get("arrival_time", "Unknown"),
                        "duration_minutes": flight.get("total_duration", 0),
                        "price_usd": flight.get("price", "Unknown"),
                        "layovers": len(flight.get("flights", [])) - 1
                        }
                        structured_data["best_flights"].append(flight_info)
                
                return structured_data

            except Exception as e:
                print(f"An error occurred: {e}")
                return None
        else:
            print("No arrival_id and departure_id found")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None 

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