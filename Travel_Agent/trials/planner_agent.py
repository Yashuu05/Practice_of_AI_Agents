from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()
PLANNER_MODEL = "llama3.1:8b"

# define model
planner_model = init_chat_model(
        model=PLANNER_MODEL,
        model_provider="ollama",
        temperature=0
    )

# define custom system prompt
system_msg = SystemMessage("""
            you are a TRIP PLANNER AGENT who is an expert in planning and decision making. 
            your primary task is to create a well defined implementation plan by analyzing the user requirements.
            This implementation plan will be used by other agent "travel_agent" to implement tasks sequentially.
            Following is the list of availble tools to travel_agent:
            1. calculator_tool": "use to perform basic arithematic operations"
            2. weather_tool: "fetches temperature, precipitation details of given place"
            3. web_search_tool: "searches query on the web and returns the result"
            FOLLOW following implementation sequence:
            step 1: read user requirements.
            step 2: read availble tools to satisfy need.
            step 3: craft IMPLEMENTATION PLAN according to user requirements and availble tools.
            IMPLEMENTATION PLAN EXAMPLE:
            - search nearby hotels to <destination_place> for <head_cunt> people
            - search top popular places to visit in <destination_place> for tourists.
            - Search available Flight details for <head_count> people from <source_place> to <destination_place> under <budget> on <departure_date> and <arrival_date>
            - get weather details in <destination_place>
            - calculate total travel cost

            NOTE: The IMPLEMENTATION PLAN MUST include only implementation tasks. No additional text.
            NOTE: replace placeholder with actual values from given EXAMPLE.
            NOTE: No duplicate tasks allowed.
            NOTE: Include what tools to use to accomlplish the task.
        """)

# user input example
user_input = {
    "source_place":"Mumbai, India",
    "destination_place":"Paris, France",
    "head_count":4,
    "total_days_visit":3,
    "departure date":"12 September 2026",
    "arrival_date":"15 September 2026",
    "trip_budget":150000
}

# user query
human_message = HumanMessage(
    f"provide the implementation plan by analyzing given user requirement:\n{user_input}"
)

# define agent 
plan_agent = create_agent(
    model=planner_model,
    system_prompt=system_msg
)
print("response = \n")
response = plan_agent.invoke({"messages": [human_message]})
content = response['messages'][-1].content
print(content.encode('utf-8', errors='ignore').decode('cp1252', errors='ignore'))
