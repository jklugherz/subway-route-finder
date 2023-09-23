from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from custom_types import RouteID, StopID, RouteName, StopName


@dataclass
class Route:
    route_id: RouteID
    name: RouteName
    route_patterns: List[RoutePattern] = field(default_factory=list)

    @property
    def max_num_stops(self):
        return max(route_pattern.num_stops for route_pattern in self.route_patterns)

    @property
    def min_num_stops(self):
        return min(route_pattern.num_stops for route_pattern in self.route_patterns)


@dataclass
class RoutePattern:
    route_pattern_id: str
    route_pattern_name: str
    representative_trip_id: str
    stops: List[Stop] = field(default_factory=list)

    @property
    def num_stops(self) -> int:
        return len(self.stops)


@dataclass
class Stop:
    stop_id: StopID
    name: StopName
