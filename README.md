# subway-route-finder
Lightweight interface to find info about routes in a subway system (ie. MBTA).

## Running the app
Clone this repository.

Inside the project directory, create an activate a Python3 virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```

Run the Python script:
```bash
python main.py
```

An interactive session will start in the terminal, prompting the user to input an acronym of a subway system.
At this time, this application only supports the MBTA, but the code is general enough such that other subway systems with APIs using 
the GTFS (General Transit Feed Specification) format can be supported in the future. 

If the user input is valid, the application will provide a list of subway route names in that subway system, 
the route with the most stops, the route with the least stops, and a list of stops that can be used to transfer between routes.

The application will then prompt the user for two stops and provide a list of routes one would need to use to travel
between those stops.

Here's an example session:
```text
Welcome to subway-route-finder!
What is the acronym of the subway system you would like to know more about? (Example input: MBTA)
>> MBTA

MBTA Subway Routes: Red Line, Mattapan Trolley, Orange Line, Green Line B, Green Line C, Green Line D, Green Line E, Blue Line

Route with most stops: Green Line D @ 25 stops
Route with fewest stops: Mattapan Trolley @ 8 stops
 
The following stops serve multiple subway routes and can be used to transfer between routes:
Park Street: Green Line D, Red Line, Green Line C, Green Line E, Green Line B
Downtown Crossing: Orange Line, Red Line
Ashmont: Red Line, Mattapan Trolley
North Station: Orange Line, Green Line D, Green Line E
Haymarket: Orange Line, Green Line D, Green Line E
State: Orange Line, Blue Line
Government Center: Blue Line, Green Line B, Green Line D, Green Line E, Green Line C
Boylston: Green Line D, Green Line E, Green Line C, Green Line B
Arlington: Green Line D, Green Line E, Green Line C, Green Line B
Copley: Green Line B, Green Line D, Green Line E, Green Line C
Hynes Convention Center: Green Line B, Green Line D, Green Line C
Kenmore: Green Line D, Green Line B, Green Line C
Lechmere: Green Line D, Green Line E
Science Park/West End: Green Line D, Green Line E

Please provide two MBTA subway stops you'd like to travel between. (Example input: Davis, Kendall/MIT)
>> Wonderland, Porter

To travel between these two stops, you can take the following subway routes: Blue Line, Orange Line, Red Line
```

## Running the tests
Inside the project directory and virtual environment, run pytest on the tests directory:
```bash
pytest tests
```


## Notes from the developer
Here are the main considerations I had during development and some insight into my decisions. 

### MBTA API Endpoints 
After reading through the [documentation](https://api-v3.mbta.com/docs/swagger/index.html) and some trial-and-error, I chose two MBTA API endpoints to get route and stop data.
 - `/routes?filter[type]=0,1&include=route_patterns`
   - I filtered by subway types because the scope of this app is limited to subway routes only. I didn't want to reinvent the wheel and write the filtering code if that functionality is provided with the endpoint. It's an easy change if I want to include more route types in the future. 
   - I included the `route_patterns` relationship because routes have a canonical route pattern, which has a representative trip, and trips have stops.
 - `/trips/{trip_id}?include=stops`
   - Trips have an ordered list of stops in the response. 
   - I only wanted trips in a single direction because my graph is undirected.

I did not use the `/stops` endpoint because although I could filter by `route_id`, the stops in the response did not
have an ordered relationship with each other. That relationship only exists for trips.


### Modeling the Route and Stop data
I knew I needed to model the subway system as a graph in order to perform path-finding operations, but I also
modeled routes and stops from the API responses in an intermediate nested class structure using the `dataclasses` module.
(I chose dataclasses because it comes with Python and eliminates the need to write redundant constructor code.)
The intermediate data structure made writing the operations like listing route names straightforward.
This structure is also useful if I want to save the route data to a relational database in the future.

### Modeling the subway as a graph: use a library or write it myself?
I ended up doing both. I searched for a Python package for modeling data as graphs because I knew it would come with an optimized path-finding algorithm.
I tried using the `networkx` library, but ran into a problem where the `shortest_path()` method did not return the routes associated with the path. I ran into 
another problem when I realized I'd need to use the `MultiGraph` class instead of the `Graph` class to model multiple edges (routes) that connect two stops.
I wrote my own graph implementation using dictionaries.

### Which graph search algorithm do I use?
I chose to implement Breadth-First Search to find the routes between two stops. BFS finds the shortest path first, which makes sense for this simple transit use case.
