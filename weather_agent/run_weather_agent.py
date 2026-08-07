import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from weather_agent.find_coordinates import get_coordinates, corrdinates_model, get_weather, URL
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model

@tool
def get_weather_details(country_name: str, state_name: str):
    """
    Get weather details for a given country and state/city.
    Pass country_name and state_name to fetch the coordinates and then weather.
    """
    web_content = get_coordinates(country=country_name, state=state_name)

    latitude_found, longitude_found = corrdinates_model(web_content=web_content)

    if longitude_found and latitude_found:
        # call weather api
        print(f"fetching weather for auto timezone")
        result = get_weather(
            latitude=latitude_found,
            longitude=longitude_found,
            timezone="auto",
            forecast_days=1,
            weather_url=URL
        )
        return result.to_dict() # return dictionary so LLM can read it
    else: 
        return "No longitude and Latitude found."

class WeatherAgent:
    def __init__(self):
        self.config = {"configurable":{"thread_id": "weather_thread_1"}}

    def initialize_memory(self):
        memory = InMemorySaver()
        return memory

    def weather_agent(self):

        model = init_chat_model(
            model="gemini-3.1-flash-lite",
            model_provider="google-genai",
            temperature=0.4
        )

        agent = create_agent(
            model,
            tools=[get_weather_details],
            system_prompt="You are a helpful weather assistant.",
            checkpointer=self.initialize_memory()
        )

        return agent

    def run_agent(self, agent, input_prompt:str):
        result = agent.invoke(
            {"messages": [("user", input_prompt)]},
            config=self.config
            )
        output_message = result["messages"][-1]
        
        if isinstance(output_message.content, list):
            text_parts = []
            for block in output_message.content:
                if isinstance(block, dict) and 'text' in block:
                    text_parts.append(block['text'])
                elif isinstance(block, str):
                    text_parts.append(block)
            print("".join(text_parts))
        else:
            print(output_message.content)

if __name__ == "__main__":
    print("=========== AGENT INITIATED ==========")
    user_prompt = str(input("enter prompt= "))
    
    if user_prompt:
        try:
            weather_agent_obj = WeatherAgent()
            agent = weather_agent_obj.weather_agent()
            weather_agent_obj.run_agent(agent=agent, input_prompt=user_prompt)

        except Exception as e:
            print(f"error: {e}")
    else:
        print("Warining: Prompt should not be empty.")