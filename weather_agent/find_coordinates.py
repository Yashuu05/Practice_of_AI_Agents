import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from dotenv import load_dotenv
import os 
from tavily import TavilyClient
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model

load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")
if not tavily_key:
    tavily_key = None

URL = "https://api.open-meteo.com/v1/forecast"

class Coordinates(BaseModel):
    latitude: float = Field(description="latitude of a given region")
    longitude: float = Field(description="longitude of a given region")

def corrdinates_model(web_content: str) -> tuple:
    model = init_chat_model(
        model="llama3.1:4b",
        model_provider="ollama",
        temperature=0.3,
    )
    model_with_structure = model.with_structured_output(Coordinates)
    response = model_with_structure.invoke(f"Extract only Latitude and Longitude from given text. Example: Latitude:40.73061\nlongitude:73.935242\nContent: {web_content}")
    
    if response:
        return response.latitude, response.longitude

    print("No response found.")
    return None, None

# get weather details dataframe
def get_weather(latitude:float, longitude:float, timezone:str, forecast_days=3, weather_url=URL):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 3, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    params = {
        "latitude":latitude,
        "longitude":longitude,
        "Daily":["temperature_2m", "rain", "visibility", "wind_speed_80m", "precipitation_probability"],
        "timezone": timezone,
        "forecast_days":forecast_days,
        "temperature_unit":"celsius",
        "wind_speed_unit":"kmh",
        "precipitation_unit":"mm"
    }
    
    responses = openmeteo.weather_api(weather_url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy() 
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_80m = hourly.Variables(3).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {
	"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	).tz_convert(response.Timezone().decode())
    }

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["visibility"] = hourly_visibility
    hourly_data["wind_speed_80m"] = hourly_wind_speed_80m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    return hourly_dataframe


def get_coordinates(country: str, state: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("API key is None. Verify API key.")
        return None
    
    print("API KEY FOUND. Searching web...")
    tavily_client = TavilyClient(api_key=api_key)
    response = tavily_client.search(f"latitude and longitude of {state} in {country}")
    
    if not response.get('results'):
        print("No results found on the web.")
        return ""
        
    content = response['results'][0]['content']
    return str(content).split(sep="\n")[0]


if __name__ == "__main__":

    print("===== program initiated =====")
    user_country = input(str("country = "))
    user_state = input(str("state = "))

    print("searching web...")
    # search the web
    web_content = get_coordinates(country=user_country, state=user_state)
    print("web content extracted =\n", web_content)

    # use model 
    print("\ndetermining the Coordinates...")
    latitude_found, longitude_found = corrdinates_model(web_content=web_content)
    if longitude_found and latitude_found:
        print("latitude found: ", latitude_found)
        print("longitude found: ", longitude_found)

        # call weather api
        user_timezone = "auto"
        print(f"fetching weather for timezone {user_timezone}")
        result = get_weather(
                latitude=latitude_found,
                longitude=longitude_found,
                timezone=user_timezone,
                forecast_days=1,
                weather_url=URL
            )
        print(result)
        
    else: 
        print("No longitude and Latitude found.")