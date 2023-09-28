import collections
from typing import List, Dict, Set, Optional

from custom_types import StopName, RouteName
from exceptions import InvalidSubwayStopInputException
from models import Route


class SubwaySystemDictGraph:
    def __init__(self, routes: List[Route]):
        self._routes = routes
        self._graph = self.transform_routes_list_to_graph(routes)

    @staticmethod
    def transform_routes_list_to_graph(
        routes: List[Route],
    ) -> Dict[StopName, Dict[StopName, Set[RouteName]]]:
        """
        Transform a list of Route objects into a dictionary-representation of a subway system graph.

        Args:
            routes (List[Route]): A list of Route objects representing subway routes.

        Returns:
            Dict[StopName, Dict[StopName, Set[RouteName]]]: A dictionary-representation of the subway system graph.

        Example return value:
        {
            "Alewife": {"Davis": {"Red Line"}},
            "Davis": {"Alewife": {"Red Line"}, "Porter": {"Red Line"}},
            "Porter": {"Davis": {"Red Line"}, "Harvard": {"Red Line"}},
            "Harvard": {"Porter": {"Red Line"}, "Central": {"Red Line"}},
            "Central": {"Harvard": {"Red Line"}, "Kendall/MIT": {"Red Line"}},
            "Kendall/MIT": {"Central": {"Red Line"}, "Charles/MGH": {"Red Line"}},
            "Charles/MGH": {"Kendall/MIT": {"Red Line"}, "Park Street": {"Red Line"}},
            "Park Street": {
                "Charles/MGH": {"Red Line"},
                "Downtown Crossing": {"Red Line"},
                "Government Center": {
                    "Green Line D",
                    "Green Line E",
                    "Green Line B",
                    "Green Line C",
                },
                "Boylston": {"Green Line D", "Green Line E", "Green Line B", "Green Line C"},
            },
            "Downtown Crossing": {
                "Park Street": {"Red Line"},
                "South Station": {"Red Line"},
                "State": {"Orange Line"},
                "Chinatown": {"Orange Line"},
            },
            ...,
        }
        """
        subway_graph = {}

        for route in routes:
            for route_pattern in route.route_patterns:
                prev_stop = None

                for stop in route_pattern.stops:
                    if stop.name not in subway_graph:
                        subway_graph[stop.name] = {}

                    if prev_stop is not None:
                        # Add stops to network_graph in both directions
                        if prev_stop.name not in subway_graph[stop.name]:
                            subway_graph[stop.name][prev_stop.name] = {route.name}
                        else:
                            subway_graph[stop.name][prev_stop.name].add(route.name)

                        if stop.name not in subway_graph[prev_stop.name]:
                            subway_graph[prev_stop.name][stop.name] = {route.name}
                        else:
                            subway_graph[prev_stop.name][stop.name].add(route.name)

                    prev_stop = stop

        return subway_graph

    def get_transfer_stops(self) -> Dict[StopName, Set[RouteName]]:
        """
        Find stops that serve multiple subway routes.

        Returns:
            Dict[StopName, Set[RouteName]]: A dictionary mapping stop names to sets of route names.
        """
        stops_dict: Dict[StopName, Set[RouteName]] = {}

        for stop_to, stop_from in self._graph.items():
            all_routes_for_stop = set().union(*list(stop_from.values()))
            if len(all_routes_for_stop) > 1:
                stops_dict[stop_to] = all_routes_for_stop

        return stops_dict

    def _remove_route(self, route_name: RouteName):
        new_routes = [route for route in self._routes if route.name != route_name]
        self._routes = new_routes
        self._graph = self.transform_routes_list_to_graph(new_routes)

    def find_routes_between_two_stops(
        self, start_stop_name: str, end_stop_name: str, unavailable_route_name: Optional[str]
    ) -> List[Set[RouteName]]:
        """
        Use Breadth-First Search (BFS) to find all combinations of routes between two subway stops.

        The time complexity of this algorithm is linear O(V + E), where V = number of stops and E = number of connections
        in the subway graph. This is because in the worst case, the algorithm checks all possible stops and connections
        before it finds a set of routes between the start and end stop.

        Args:
            start_stop_name (str): The name of the starting subway stop.
            end_stop_name (str): The name of the destination subway stop.
            unavailable_route_name (str, optional): The name of the unavailable route, if there is one.

        Returns:
            List[Set[RouteName]]: A list of sets, each containing route names representing possible connections
            between the start and end stops.
        """
        if start_stop_name not in self._graph:
            raise InvalidSubwayStopInputException(
                f"'{start_stop_name}' is not a valid subway stop."
            )

        if end_stop_name not in self._graph:
            raise InvalidSubwayStopInputException(
                f"'{end_stop_name}' is not a valid subway stop."
            )

        if unavailable_route_name:
            self._remove_route(RouteName(unavailable_route_name))

        all_routes: List[Set[RouteName]] = []

        # Keep track of visited stops to avoid cycles
        visited = set()

        # Keep stops to visit in a queue, represented by a tuple of stop name and a set of routes
        queue = collections.deque()
        queue.append((start_stop_name, set()))

        while queue:
            current_stop, current_routes = queue.popleft()
            visited.add(current_stop)

            if current_stop == end_stop_name:
                all_routes.append(current_routes)
            else:
                neighbors = self._graph.get(current_stop, {})
                for neighbor_stops, neighbor_routes in neighbors.items():
                    if neighbor_stops not in visited:
                        new_routes = current_routes.union(neighbor_routes)
                        queue.append((neighbor_stops, new_routes))

        return all_routes
