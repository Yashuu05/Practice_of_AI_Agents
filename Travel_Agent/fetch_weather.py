import http.client
import urllib.parse
import json

def fetch_weather(location):
    """
    Fetches the 3-day weather forecast for a specified location with hourly data
    and a 24-hour interval using the Weatherstack API.
    """
    conn = http.client.HTTPSConnection("api.weatherstack.com")
    headers = { 'Accept': "application/json, application/json; Charset=UTF-8" }
    
    # IMPORTANT: Replace 'YOUR_ACCESS_KEY' with your actual weatherstack API access key
    access_key = "13e70157139ebec71223cc00714ed3c1"
    
    # Encode the location to handle spaces and special characters (e.g., 'New York')
    query = urllib.parse.quote(location)
    
    # Constructing the URL path with query parameters according to the requirements:
    # forecast_days=3 (Forecast for 3 days)
    # hourly=1 (Enable hourly data)
    # interval=24 (Interval of 24 hours)
    path = f"/forecast?access_key={access_key}&query={query}&forecast_days=3&hourly=1&interval=24"
    
    try:
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        # Parse and return the JSON response
        json_data = json.loads(data.decode("utf-8"))
        
        # Checking if API returned an error (e.g. invalid key)
        if "error" in json_data:
            print(f"API Error for {location}: {json_data['error']['info']}")
            return None
            
        print(f"Weather Forecast for {location} successfully fetched.")
        return json_data
        
    except Exception as e:
        print(f"An error occurred while fetching weather for {location}: {e}")
        return None

if __name__ == "__main__":
    # Example locations
    print("Fetching weather for New York...")
    ny_weather = fetch_weather("New York")
    if ny_weather:
        print(json.dumps(ny_weather, indent=4))
