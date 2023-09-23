import json
from typing import List, Dict

import requests

from custom_types import RouteID, StopID, RouteName, StopName
from exceptions import TransitAPIRequestException
from models import Route, RoutePattern, Stop
from settings import Settings


class RouteDataRepository:
    def __init__(self, settings: Settings):
        self._base_url = settings.transit_api_base_url
        self._api_key = settings.api_key

    def create_routes_intermediate_data_structure(self) -> List[Route]:
        """
        Create a list of Route objects with data from the /routes and /trips APIs.

        Returns:
            List[Route]: A list of Route objects.

        Example return value:
          [Route(
            route_id="Red",
            name="Red Line",
            route_patterns=[
                RoutePattern(
                    route_pattern_id="Red-1-0",
                    route_pattern_name="Alewife - Ashmont",
                    representative_trip_id="canonical-Red-C2-0",
                    stops=[
                        Stop(stop_id="70061", name="Alewife"),
                        Stop(stop_id="70063", name="Davis"),
                        Stop(stop_id="70065", name="Porter"),
                        Stop(stop_id="70067", name="Harvard"),
                        Stop(stop_id="70069", name="Central"),
                        Stop(stop_id="70071", name="Kendall/MIT"),
                        Stop(stop_id="70073", name="Charles/MGH"),
                        Stop(stop_id="70075", name="Park Street"),
                        Stop(stop_id="70077", name="Downtown Crossing"),
                        Stop(stop_id="70079", name="South Station"),
                        Stop(stop_id="70081", name="Broadway"),
                        Stop(stop_id="70083", name="Andrew"),
                        Stop(stop_id="70085", name="JFK/UMass"),
                        Stop(stop_id="70087", name="Savin Hill"),
                        Stop(stop_id="70089", name="Fields Corner"),
                        Stop(stop_id="70091", name="Shawmut"),
                        Stop(stop_id="70093", name="Ashmont"),
                    ],
                ),
                RoutePattern(
                    route_pattern_id="Red-3-0",
                    route_pattern_name="Alewife - Braintree",
                    representative_trip_id="canonical-Red-C1-0",
                    stops=[
                        Stop(stop_id="70061", name="Alewife"),
                        Stop(stop_id="70063", name="Davis"),
                        Stop(stop_id="70065", name="Porter"),
                        Stop(stop_id="70067", name="Harvard"),
                        Stop(stop_id="70069", name="Central"),
                        Stop(stop_id="70071", name="Kendall/MIT"),
                        Stop(stop_id="70073", name="Charles/MGH"),
                        Stop(stop_id="70075", name="Park Street"),
                        Stop(stop_id="70077", name="Downtown Crossing"),
                        Stop(stop_id="70079", name="South Station"),
                        Stop(stop_id="70081", name="Broadway"),
                        Stop(stop_id="70083", name="Andrew"),
                        Stop(stop_id="70095", name="JFK/UMass"),
                        Stop(stop_id="70097", name="North Quincy"),
                        Stop(stop_id="70099", name="Wollaston"),
                        Stop(stop_id="70101", name="Quincy Center"),
                        Stop(stop_id="70103", name="Quincy Adams"),
                        Stop(stop_id="70105", name="Braintree"),
                    ],
                ),
            ],
            ...
          ]
        """
        routes: List[Route] = []

        get_routes_response = self._get_subway_routes_and_route_patterns()
        route_patterns_map = self._map_route_patterns_to_route_id(
            get_routes_response["included"]
        )

        for raw_route in get_routes_response["data"]:
            route_id = RouteID(raw_route["id"])
            route_patterns = route_patterns_map.get(route_id)
            self._populate_stops_for_route_patterns(route_patterns)

            route = Route(
                route_id=route_id,
                name=RouteName(raw_route["attributes"]["long_name"]),
                route_patterns=route_patterns,
            )
            routes.append(route)

        return routes

    def _get_subway_routes_and_route_patterns(self) -> dict:
        """
        Fetches subway route data via the /routes API. Filters by routes of types 0 and 1 (light rail and heavy rail)
        and includes route patterns for each route.

        Returns:
            dict: The API response as a dictionary.
        """
        query_params = {"filter[type]": "0,1", "include": "route_patterns"}
        if self._api_key:
            query_params["api_key"] = self._api_key

        get_routes_url = f"{self._base_url}/routes"
        response_dict = self.make_http_get_request(get_routes_url, query_params)
        return response_dict

    @staticmethod
    def _map_route_patterns_to_route_id(
        route_patterns_dicts: List[dict],
    ) -> Dict[RouteID, List[RoutePattern]]:
        """
        One route (i.e. Red Line) can have multiple route patterns (i.e. to Ashmont or to Braintree), each of which has
        its own representative trip.

        This function parses a list of route pattern dicts into a map where the key is a RouteID
        and the value is a list of RoutePatterns, which includes only canonical route patterns in a single direction.

        The returned RoutePattern objects will not yet have 'stops' attribute populated.

        Args:
            route_patterns_dicts (List[dict]): List of route pattern dictionaries.

        Returns:
            Dict[RouteID, List[RoutePattern]]: A dictionary mapping RouteID to lists of RoutePattern objects.
        """
        route_patterns_map: Dict[RouteID, List[RoutePattern]] = {}

        for route_pattern_resp in route_patterns_dicts:
            if (
                route_pattern_resp["attributes"].get("canonical")
                and route_pattern_resp["attributes"].get("direction_id") == 0
            ):
                route_id = RouteID(
                    route_pattern_resp["relationships"]["route"]["data"]["id"]
                )
                representative_trip_id = route_pattern_resp["relationships"][
                    "representative_trip"
                ]["data"]["id"]

                route_pattern = RoutePattern(
                    route_pattern_id=route_pattern_resp["id"],
                    route_pattern_name=route_pattern_resp["attributes"]["name"],
                    representative_trip_id=representative_trip_id,
                )
                if route_id not in route_patterns_map:
                    route_patterns_map[route_id] = [route_pattern]
                else:
                    route_patterns_map[route_id].append(route_pattern)

        return route_patterns_map

    def _populate_stops_for_route_patterns(
        self, route_patterns: List[RoutePattern]
    ) -> None:
        """
        Populates the 'stops' attribute of each RoutePattern object from the list of Stop objects (in order)
        for the representative trip of the route pattern.

        The list of stops for representative trip is fetched using the /trips API.

        Args:
            route_patterns (List[RoutePattern]): List of RoutePattern objects to populate with stops.
        """
        for route_pattern in route_patterns:
            get_trips_response = self._get_trip_and_stops(
                route_pattern.representative_trip_id
            )

            # Use 'included' response to populate Stop objects because the stop name is located here in the response.
            stops_map: Dict[StopID, Stop] = {}
            for stop_response in get_trips_response["included"]:
                stop = Stop(
                    stop_id=StopID(stop_response["id"]),
                    name=StopName(stop_response["attributes"]["name"]),
                )
                stops_map[stop_response["id"]] = stop

            # This part of the response has the stops in order by ID.
            for raw_stop in get_trips_response["data"]["relationships"]["stops"][
                "data"
            ]:
                route_pattern.stops.append(stops_map[raw_stop["id"]])

    def _get_trip_and_stops(
        self,
        trip_id: str,
    ) -> dict:
        """
        Fetches trip data for a single trip_id via the /trips API, including stops.

        Args:
            trip_id (str): The ID of the trip to fetch.

        Returns:
            dict: The API response as a dictionary.
        """
        query_params = {"include": "stops"}
        if self._api_key:
            query_params["api_key"] = self._api_key

        get_trips_url = f"{self._base_url}/trips/{trip_id}"
        response_dict = self.make_http_get_request(get_trips_url, query_params)
        return response_dict

    @staticmethod
    def make_http_get_request(url: str, query_params: Dict[str, str] = None) -> dict:
        """
        Makes an HTTP GET request to the specified URL with optional query parameters.

        Args:
            url (str): The URL to make the request to.
            query_params (Dict[str, str]): Optional query parameters.

        Returns:
            dict: The API response as a dictionary.
        """
        raw_response = requests.get(url, params=query_params)

        if raw_response.status_code != 200:
            raise TransitAPIRequestException(
                f"Received non-200 response from url: {url}"
            )
        return json.loads(raw_response.text)
