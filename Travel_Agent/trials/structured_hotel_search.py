import os
import json
from dotenv import load_dotenv
import serpapi

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
    load_dotenv()
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

if __name__ == "__main__":
    extracted_hotels = fetch_and_extract_hotels()
    
    if extracted_hotels:
        # Print structured results
        print("Extracted Hotel Information:")
        print(json.dumps(extracted_hotels, indent=4))
        
        # Save to file for further inspection
        output_file = "extracted_hotels_results.json"
        with open(output_file, "w") as f:
            json.dump(extracted_hotels, f, indent=4)
        print(f"\nExtracted results successfully saved to {output_file}")
