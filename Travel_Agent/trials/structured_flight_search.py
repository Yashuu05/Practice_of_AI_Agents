import os
import sys
import json
import serpapi
from dotenv import load_dotenv
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from trials.airport_codes import get_iata_by_city

# Load environment variables (e.g., API_KEY)
load_dotenv()

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

                # Extract best flights
                if "best_flights" in results:
                    for flight in results["best_flights"]:
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

if __name__ == "__main__":
    print("======== PROGRAM INITIATED ========")
    # Fetch flight details
    print("fetching flight detials")
    flight_data = fetch_flights(
        outbound_date="2026-09-05",
        return_date="2026-09-10",
        dest_city="London",
        dest_country="",
        source_city="New York",
        source_country="",
        trip_type="2",
        adults=3,
        travel_class="1",
    )
    
    if flight_data:
        # Save output to a JSON file for reference
        output_file = "flight_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(flight_data, f, indent=4)
        print(f"Successfully fetched and structured flight details. Saved to {output_file}.")
        
        # Display best flights summary
        print("\n--- Best Flights ---")
        for f in flight_data["best_flights"][:2]:  # Print top 3 results
            print(f"{f['airline']} {f['flight_number']} | {f['departure_time']} -> {f['arrival_time']} | "
                  f"{f['duration_minutes']} mins | Layovers: {f['layovers']} | Price: ${f['price_usd']}")