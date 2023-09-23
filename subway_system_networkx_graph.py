from typing import List
import networkx as nx
from networkx import Graph

from models import Route


class SubwaySystemGraph:
    def __init__(self, routes: List[Route]):
        self._graph = self._transform_routes_list_to_graph(routes)

    @staticmethod
    def _transform_routes_list_to_graph(routes: List[Route]) -> Graph:
        """
        Use the networkx library to turn a list of routes into a graph where nodes are stop names and edges
        are two adjacent stops with route name as an attribute.

        Example nodes in returned graph:  [('Alewife', {}), ('Davis', {}), ('Porter', {}), ...]
        Example edges in returned graph:  [('Alewife', 'Davis', {'route': 'Red Line'}), ('Davis', 'Porter', {'route': 'Red Line'}), ...]
        """
        network_graph = nx.Graph()

        for route in routes:
            for route_pattern in route.route_patterns:
                prev_stop = None

                for stop in route_pattern.stops:
                    if stop.name not in network_graph.nodes:
                        network_graph.add_node(stop.name)

                    if prev_stop is not None:
                        # Add stops to network_graph in both directions
                        network_graph.add_edges_from(
                            [(stop.name, prev_stop.name), (prev_stop.name, stop.name)],
                            route=route.name,
                        )

                    prev_stop = stop

        return network_graph

    def get_transfer_stops(self):
        # TODO
        ...

    def find_routes_between_two_stops(
        self, start_stop_name: str, end_stop_name: str
    ) -> List[str]:
        """
        Finds the list of subway route names one will need to use to travel between two stops in the subway system.

        Use the networkx 'shortest_path()' function to get a list of edges for the shortest path between two stops.
        Match those edges with the graph's edges to get the route attributes of those edges.

        The default algorithm for shortest_path is dijkstra's.
        """
        stops_in_shortest_path = nx.shortest_path(
            self._graph, start_stop_name, end_stop_name
        )

        routes_travelled = []
        shortest_path_graph = nx.path_graph(stops_in_shortest_path)

        for from_node, to_node in shortest_path_graph.edges():
            route = self._graph.edges[from_node, to_node]["route"]

            if route not in routes_travelled:
                routes_travelled.append(route)

        return routes_travelled
