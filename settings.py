from dataclasses import dataclass
from typing import Optional

from exceptions import InvalidSubwaySystemInputException


@dataclass
class Settings:
    transit_api_base_url: str
    api_key: Optional[str] = None


def mbta_settings() -> Settings:
    return Settings(
        transit_api_base_url="https://api-v3.mbta.com",
    )


SUBWAY_SYSTEM_TO_SETTINGS_MAP = {"MBTA": mbta_settings()}


def get_settings(subway_system: str) -> Settings:
    settings = SUBWAY_SYSTEM_TO_SETTINGS_MAP.get(subway_system, None)

    if not settings:
        raise InvalidSubwaySystemInputException(
            f"'{subway_system}' is not a supported subway system."
        )
    return settings
