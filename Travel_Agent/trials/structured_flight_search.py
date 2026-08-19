import os
import json
import serpapi
from dotenv import load_dotenv

# Load environment variables (e.g., API_KEY)
load_dotenv()

def fetch_flights(departure_id, arrival_id, outbound_date, return_date=None, trip_type="2", adults=1, travel_class="1"):
    """
    Fetch flight details using Serpapi Google Flights API.

    Parameters:
    - departure_id: str, e.g., "CDG" (Paris Charles de Gaulle)
    - arrival_id: str, e.g., "AUS" (Austin-Bergstrom)
    - outbound_date: str, format "YYYY-MM-DD"
    - return_date: str, format "YYYY-MM-DD" (optional, required if trip_type is "1")
    - trip_type: str, "1" for Round trip, "2" for One way
    - adults: int, number of adult passengers
    - travel_class: str, "1" (Economy), "2" (Premium economy), "3" (Business), "4" (First)
    """
    # Retrieve API key from environment
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("Error: SERPAPI_KEY not found in environment variables.")
        return None

    client = serpapi.Client(api_key=api_key)
    print("API KEY found. Implementing flight search...")
    # Base parameters for the search
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
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
        print(f"Fetching flights from {departure_id} to {arrival_id} on {outbound_date}...")
        results = client.search(params)
        
        # Structure the extracted data
        structured_data = {
            "best_flights": [],
            "other_flights": [],
            "price_insights": results.get("price_insights", {})
        }

        # Extract best flights
        if "best_flights" in results:
            for flight in results["best_flights"]:
                flight_info = {
                    "airline": flight.get("flights", [{}])[0].get("airline", "Unknown"),
                    "flight_number": flight.get("flights", [{}])[0].get("flight_number", "Unknown"),
                    "departure_airport": flight.get("flights", [{}])[0].get("departure_airport", {}).get("id", departure_id),
                    "arrival_airport": flight.get("flights", [{}])[-1].get("arrival_airport", {}).get("id", arrival_id),
                    "departure_time": flight.get("flights", [{}])[0].get("departure_time", "Unknown"),
                    "arrival_time": flight.get("flights", [{}])[-1].get("arrival_time", "Unknown"),
                    "duration_minutes": flight.get("total_duration", 0),
                    "price_usd": flight.get("price", "Unknown"),
                    "layovers": len(flight.get("flights", [])) - 1
                }
                structured_data["best_flights"].append(flight_info)

        # Extract other flights
        if "other_flights" in results:
            for flight in results["other_flights"]:
                flight_info = {
                    "airline": flight.get("flights", [{}])[0].get("airline", "Unknown"),
                    "flight_number": flight.get("flights", [{}])[0].get("flight_number", "Unknown"),
                    "departure_airport": flight.get("flights", [{}])[0].get("departure_airport", {}).get("id", departure_id),
                    "arrival_airport": flight.get("flights", [{}])[-1].get("arrival_airport", {}).get("id", arrival_id),
                    "departure_time": flight.get("flights", [{}])[0].get("departure_time", "Unknown"),
                    "arrival_time": flight.get("flights", [{}])[-1].get("arrival_time", "Unknown"),
                    "duration_minutes": flight.get("total_duration", 0),
                    "price_usd": flight.get("price", "Unknown"),
                    "layovers": len(flight.get("flights", [])) - 1
                }
                structured_data["other_flights"].append(flight_info)

        return structured_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    from airport_codes import get_iata_by_city

    # Example: User provides cities instead of IATA codes
    departure_city = "London"
    arrival_city = "New York"
    result_limit = 2
    
    # Resolve Departure City
    print(f"fetching IATA by city for {departure_city}...")
    dep_airports = get_iata_by_city(departure_city)
    if not dep_airports:
        print(f"No airport found for {departure_city}")
        exit()
    # Picking the first airport for simplicity (e.g., CDG for Paris)
    departure_id = dep_airports[0]['iata']
    print(f"Resolved {departure_city} to {departure_id} ({dep_airports[0]['name']})")

    # Resolve Arrival City
    print(f"fethcing IATA by city for {arrival_city}...")
    arr_airports = get_iata_by_city(arrival_city)
    if not arr_airports:
        print(f"No airport found for {arrival_city}")
        exit()
    # Picking the first airport for simplicity
    arrival_id = arr_airports[0]['iata']
    print(f"Resolved {arrival_city} to {arrival_id} ({arr_airports[0]['name']})\n")

    # Fetch flight details
    print("fetching flight detials")
    flight_data = fetch_flights(
        departure_id=departure_id, 
        arrival_id=arrival_id, 
        outbound_date="2026-08-18", 
        trip_type="2"
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

