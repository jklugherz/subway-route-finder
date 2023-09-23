from typing import List

from models import Route
from route_data_repository import RouteDataRepository
from settings import get_settings
from subway_system_dict_graph import SubwaySystemDictGraph


def get_subway_system_from_user() -> str:
    """
    Get the acronym of the subway system from the user.

    Returns:
        str: The acronym of the subway system provided by the user.
    """
    return input(
        "What is the acronym of the subway system you would like to know more about? (Example input: MBTA)\n"
    )


def get_subway_stops_from_user(subway_system: str) -> List[str]:
    """
    Get two subway stops from the user.

    Args:
        subway_system (str): The acronym of the subway system.

    Returns:
        List[str]: A list containing two subway stops provided by the user.
    """
    subway_stops_str = input(
        f"\nPlease provide two {subway_system} subway stops you'd like to travel between. (Example input: Davis, Kendall/MIT)\n"
    )
    return [x.strip() for x in subway_stops_str.split(",")]


def collect_route_info(routes: List[Route]) -> dict:
    """
    Collects and returns route information.

    Args:
        routes (List[Route]): A list of Route objects.

    Returns:
        dict: A dictionary containing route information with route names as keys and their maximum and minimum stops as values.
    """
    route_info = {}
    for route in routes:
        route_info[route.name] = {
            "max_stops": route.max_num_stops,
            "min_stops": route.min_num_stops,
        }
    return route_info


def main():
    print(f"Welcome to subway-route-finder!")

    subway_system = get_subway_system_from_user()
    settings = get_settings(subway_system)
    route_repository = RouteDataRepository(settings)
    routes = route_repository.create_routes_intermediate_data_structure()
    print(routes)

    route_info = collect_route_info(routes)

    max_stops_route_name = max(
        route_info, key=lambda name: route_info[name]["max_stops"]
    )
    min_stops_route_name = min(
        route_info, key=lambda name: route_info[name]["min_stops"]
    )

    print(f"\n{subway_system} Subway Routes: {', '.join(route_info.keys())}\n")
    print(
        f"Route with most stops: {max_stops_route_name} @ {route_info[max_stops_route_name]['max_stops']} stops"
    )
    print(
        f"Route with fewest stops: {min_stops_route_name} @ {route_info[min_stops_route_name]['min_stops']} stops\n "
    )

    graph = SubwaySystemDictGraph(routes)
    transfer_stops = graph.get_transfer_stops()

    print(
        "The following stops serve multiple subway routes and can be used to transfer between routes:"
    )
    for stop_name, routes in transfer_stops.items():
        print(f"{stop_name}: {', '.join(routes)}")

    subway_stop_names = get_subway_stops_from_user(subway_system)

    routes_within_path = graph.find_routes_between_two_stops(*subway_stop_names)
    print(
        f"\nTo travel between these two stops, you can take the following subway routes: {', '.join(routes_within_path[0])}"
    )


if __name__ == "__main__":
    main()
