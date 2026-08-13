# TRAVEL AGENT

### OBJECTIVE:
- providing _travel guide_ to the users or travelers

### GOAL:
- making easy to plan trips

### how human plans travel or trip?

1. choose number of people
2. number of days and nights
3. choose the destination location
4. calculate the distance, time from source to destination
5. transport vehicle (Bus, train, Flight)
6. calculate the total ticket price for for travel
7. forecast weather details
8. popular places to visit, dishes, products
9. output

*Variables* / inputs: 
1. source : example: Pune, India
2. destination place : Osaka, Japan
3. number of people (example: 2,4,7)
4. number of days and nights (example: 2 days 1 night)
5. Departure date : example: 26th September 2026
6. Arrival date: 29th September 2026
7. Trip budget : example: INR 80000 or INR 1,40,000

*Output* : 
1. weather details for living days such as temperature, precipitation, AQI etc
2. Trip Recommendation: 
- example: 
	- best places to visit
	- items, products to buy
	- dishes to try
3. Total traveling expense: 
- example:
	- flight : average of INR 30000 per head
	- expected total Flight expense (both arrival and departure): 1,20,000 (for all)
4. Flight Details
5. Hotels nearby destination place and their average Charges
6. Total expected expense:
	1. traveling : 1,20,000 INR
	2. hotel:  30,000 INR
	3. hanging out (average spending) : 20,000 INR
	4. total : 1,70,000 INR
7. Minimum Budget : INR 1,50,000

*tools* : 
1. calculator (calculates expense, budget)
2. weather (weather details)
3. web search (search hotels, places, flights)
4. Map (distance, time)
5. Calendar (adds trip dates)

*tech stack*: 

1. Langchain 
2. Tavily
3. Mongo Db / MySQL
4. langchain-ollama
5. langchain-google

*LLMs*: 

1. function calling : gemini-3.5-flash-lite
2. NLP / summary : ollama llama  

*agent properties*

1. thinking (think before acting)
2. planning (plan before calling tools)
3. memory (save conversations )
4. feedback (improve from feedbacks) - optional

*Sub agents*

1. Master Agent
2. planner agent
3. travel agent

*architecture*

```
================== START ==============================
1. user inputs
	- budget
	- arrival and departure dates
	- number of people
	- destination place
	- source place
	- number of days
----------------------------------------------------
			|
			|
----------------------------------------------------
2. Planner Agent 
	- create a implementation plan
	- deep thinking by analyzing user requirements
-----------------------------------------------------
			|
			|
------------------------------------------------------ 
3. Travel agent
	- recieves implementation plan from planner agent
	- uses various multiple tools
	- gathers necessary information by using tools 
	  such as weather details, available flights and
	  hotels
-------------------------------------------------------
			|
			|
--------------------------------------------------------
4. NLP
	- recieves context and information from travel agent
    - generates human friendly response
	- generates travel guide
--------------------------------------------------------
			|
			|
--------------------------------------------------------
5. OUTPUT
	- expected budget for trip
	- weather summary 
	- nearby hotels
	- recommendation of popular places, dishes, items
======================= END ============================ 
```

*rough project structure*

```
Travel_Agent/
	|___ requirements.txt
	|___ .gitignore
	|___ db/
	|	|___ init_db.py
	|	|___ create_tables.py
	|
	|___ Agent/
	|	|___ tools.py
	|	|___ main.py
	|
	|___ test/
	|	|___ test.py
	| 
	|___ venv/
	|___ .env
	|___ logger.py
	|___ exceptions.py
	
```


### FUTURE EXPANSION

- Clean UI/UX
- Containerization using docker
- deployment 
- Robust agent script 
- multi-model input (audio and image)

### DATABASE 

- DATABASE: MYSQL
- DATABASE NAME: travel_db
- *Tables*: 
    1. input
    2. output

- input:
    - columns:
    1. source 
    2. destination
    3. departure
    4. arrival
    5. budget
    6. head_count

- output:
    - columns:
    1. expected_budget
    2. weather_details
    3. transport_details
    4. trip_recommendation
    5. travel_expense
    6. hotel_details