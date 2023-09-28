import pytest

from custom_types import RouteID, RouteName, StopID, StopName
from exceptions import InvalidSubwayStopInputException
from models import RoutePattern, Route, Stop
from subway_system_dict_graph import SubwaySystemDictGraph

ROUTES = [
    Route(
        route_id=RouteID("Red"),
        name=RouteName("Red Line"),
        route_patterns=[
            RoutePattern(
                route_pattern_id="Red-1-0",
                route_pattern_name="Alewife - Ashmont",
                representative_trip_id="canonical-Red-C2-0",
                stops=[
                    Stop(stop_id=StopID("70061"), name=StopName("Alewife")),
                    Stop(stop_id=StopID("70075"), name=StopName("Park Street")),
                    Stop(stop_id=StopID("70077"), name=StopName("Downtown Crossing")),
                    Stop(stop_id=StopID("70079"), name=StopName("South Station")),
                    Stop(stop_id=StopID("70087"), name=StopName("Savin Hill")),
                    Stop(stop_id=StopID("70089"), name=StopName("Fields Corner")),
                    Stop(stop_id=StopID("70091"), name=StopName("Shawmut")),
                    Stop(stop_id=StopID("70093"), name=StopName("Ashmont")),
                ],
            ),
            RoutePattern(
                route_pattern_id="Red-3-0",
                route_pattern_name="Alewife - Braintree",
                representative_trip_id="canonical-Red-C1-0",
                stops=[
                    Stop(stop_id=StopID("70061"), name=StopName("Alewife")),
                    Stop(stop_id=StopID("70075"), name=StopName("Park Street")),
                    Stop(stop_id=StopID("70077"), name=StopName("Downtown Crossing")),
                    Stop(stop_id=StopID("70079"), name=StopName("South Station")),
                    Stop(stop_id=StopID("70097"), name=StopName("North Quincy")),
                    Stop(stop_id=StopID("70099"), name=StopName("Wollaston")),
                    Stop(stop_id=StopID("70101"), name=StopName("Quincy Center")),
                    Stop(stop_id=StopID("70103"), name=StopName("Quincy Adams")),
                    Stop(stop_id=StopID("70105"), name=StopName("Braintree")),
                ],
            ),
        ],
    ),
    Route(
        route_id=RouteID("Green-B"),
        name=RouteName("Green Line B"),
        route_patterns=[
            RoutePattern(
                route_pattern_id="Green-B-812-0",
                route_pattern_name="Government Center - Boston College",
                representative_trip_id="canonical-Green-B-C1-0",
                stops=[
                    Stop(stop_id=StopID("70196"), name=StopName("Park Street")),
                    Stop(stop_id=StopID("70159"), name=StopName("Boylston")),
                    Stop(stop_id=StopID("70157"), name=StopName("Arlington")),
                    Stop(stop_id=StopID("70155"), name=StopName("Copley")),
                    Stop(
                        stop_id=StopID("70153"),
                        name=StopName("Hynes Convention Center"),
                    ),
                    Stop(stop_id=StopID("71151"), name=StopName("Kenmore")),
                    Stop(stop_id=StopID("70149"), name=StopName("Blandford Street")),
                ],
            )
        ],
    ),
    Route(
        route_id=RouteID("Green-D"),
        name=RouteName("Green Line D"),
        route_patterns=[
            RoutePattern(
                route_pattern_id="Green-D-855-0",
                route_pattern_name="Union Square - Riverside",
                representative_trip_id="canonical-Green-D-C1-0",
                stops=[
                    Stop(stop_id=StopID("70504"), name=StopName("Union Square")),
                    Stop(stop_id=StopID("70196"), name=StopName("Park Street")),
                    Stop(stop_id=StopID("70159"), name=StopName("Boylston")),
                    Stop(stop_id=StopID("70157"), name=StopName("Arlington")),
                    Stop(stop_id=StopID("70155"), name=StopName("Copley")),
                    Stop(
                        stop_id=StopID("70153"),
                        name=StopName("Hynes Convention Center"),
                    ),
                    Stop(stop_id=StopID("71151"), name=StopName("Kenmore")),
                    Stop(stop_id=StopID("70187"), name=StopName("Fenway")),
                ],
            )
        ],
    ),
]


def test_transform_routes_list_to_graph():
    graph = SubwaySystemDictGraph.transform_routes_list_to_graph(routes=ROUTES)
    assert graph == {
        "Alewife": {"Park Street": {"Red Line"}},
        "Park Street": {
            "Alewife": {"Red Line"},
            "Downtown Crossing": {"Red Line"},
            "Boylston": {"Green Line B", "Green Line D"},
            "Union Square": {"Green Line D"},
        },
        "Downtown Crossing": {
            "Park Street": {"Red Line"},
            "South Station": {"Red Line"},
        },
        "South Station": {
            "Downtown Crossing": {"Red Line"},
            "Savin Hill": {"Red Line"},
            "North Quincy": {"Red Line"},
        },
        "Savin Hill": {"South Station": {"Red Line"}, "Fields Corner": {"Red Line"}},
        "Fields Corner": {"Savin Hill": {"Red Line"}, "Shawmut": {"Red Line"}},
        "Shawmut": {"Fields Corner": {"Red Line"}, "Ashmont": {"Red Line"}},
        "Ashmont": {"Shawmut": {"Red Line"}},
        "North Quincy": {"South Station": {"Red Line"}, "Wollaston": {"Red Line"}},
        "Wollaston": {"North Quincy": {"Red Line"}, "Quincy Center": {"Red Line"}},
        "Quincy Center": {"Wollaston": {"Red Line"}, "Quincy Adams": {"Red Line"}},
        "Quincy Adams": {"Quincy Center": {"Red Line"}, "Braintree": {"Red Line"}},
        "Braintree": {"Quincy Adams": {"Red Line"}},
        "Boylston": {
            "Park Street": {"Green Line B", "Green Line D"},
            "Arlington": {"Green Line B", "Green Line D"},
        },
        "Arlington": {
            "Boylston": {"Green Line B", "Green Line D"},
            "Copley": {"Green Line B", "Green Line D"},
        },
        "Copley": {
            "Arlington": {"Green Line B", "Green Line D"},
            "Hynes Convention Center": {"Green Line B", "Green Line D"},
        },
        "Hynes Convention Center": {
            "Copley": {"Green Line B", "Green Line D"},
            "Kenmore": {"Green Line B", "Green Line D"},
        },
        "Kenmore": {
            "Hynes Convention Center": {"Green Line B", "Green Line D"},
            "Blandford Street": {"Green Line B"},
            "Fenway": {"Green Line D"},
        },
        "Blandford Street": {"Kenmore": {"Green Line B"}},
        "Union Square": {"Park Street": {"Green Line D"}},
        "Fenway": {"Kenmore": {"Green Line D"}},
    }


def test_get_transfer_stops():
    graph = SubwaySystemDictGraph(routes=ROUTES)
    transfer_stops = graph.get_transfer_stops()

    assert transfer_stops == {
        "Arlington": {"Green Line D", "Green Line B"},
        "Boylston": {"Green Line D", "Green Line B"},
        "Copley": {"Green Line D", "Green Line B"},
        "Hynes Convention Center": {"Green Line D", "Green Line B"},
        "Kenmore": {"Green Line D", "Green Line B"},
        "Park Street": {"Green Line D", "Red Line", "Green Line B"},
    }


test_parameters = (
    "start_stop, end_stop, expected_routes",
    [
        ("Fields Corner", "Union Square", [{"Green Line D", "Red Line"}]),
        ("Park Street", "Quincy Adams", [{"Red Line"}]),
        ("Fenway", "Union Square", [{"Green Line D", "Green Line B"}]),
        ("Union Square", "Alewife", [{"Green Line D", "Red Line"}]),
        ("Ashmont", "Arlington", [{"Green Line B", "Red Line", "Green Line D"}]),
    ],
)


@pytest.mark.parametrize(*test_parameters)
def test_find_routes_between_two_stops(start_stop, end_stop, expected_routes):
    graph = SubwaySystemDictGraph(routes=ROUTES)
    routes = graph.find_routes_between_two_stops(start_stop, end_stop)

    assert routes == expected_routes


def test_find_routes_between_two_stops_raises_error():
    graph = SubwaySystemDictGraph(routes=ROUTES)

    with pytest.raises(InvalidSubwayStopInputException):
        graph.find_routes_between_two_stops("West Station", "Alewife")


def test__remove_route():
    graph = SubwaySystemDictGraph(routes=ROUTES)
    graph._remove_route(RouteName("Red Line"))

    assert graph._routes == ROUTES[1:]

    assert graph._graph == {
        "Park Street": {
            "Boylston": {"Green Line B", "Green Line D"},
            "Union Square": {"Green Line D"},
        },
        "Boylston": {
            "Park Street": {"Green Line B", "Green Line D"},
            "Arlington": {"Green Line B", "Green Line D"},
        },
        "Arlington": {
            "Boylston": {"Green Line B", "Green Line D"},
            "Copley": {"Green Line B", "Green Line D"},
        },
        "Copley": {
            "Arlington": {"Green Line B", "Green Line D"},
            "Hynes Convention Center": {"Green Line B", "Green Line D"},
        },
        "Hynes Convention Center": {
            "Copley": {"Green Line B", "Green Line D"},
            "Kenmore": {"Green Line B", "Green Line D"},
        },
        "Kenmore": {
            "Hynes Convention Center": {"Green Line B", "Green Line D"},
            "Blandford Street": {"Green Line B"},
            "Fenway": {"Green Line D"},
        },
        "Blandford Street": {"Kenmore": {"Green Line B"}},
        "Union Square": {"Park Street": {"Green Line D"}},
        "Fenway": {"Kenmore": {"Green Line D"}},
    }


def test_find_routes_between_two_stops_with_unavailable_route():
    graph = SubwaySystemDictGraph(routes=ROUTES)

    routes = graph.find_routes_between_two_stops("Park Street", "Alewife", "Red Line")

    assert not routes
