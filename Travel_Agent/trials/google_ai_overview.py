import serpapi
from dotenv import load_dotenv
import os 
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")
if not serpapi:
    print("no api key found.")
else:
    print("api key found. searching...") 
    client = serpapi.Client(api_key=serpapi_key)

    results = client.search({
    "q": ""
    })
    ai_overview = results["ai_overview"]