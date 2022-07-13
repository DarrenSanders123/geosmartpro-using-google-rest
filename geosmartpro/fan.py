"""Platform for fan integration."""
from __future__ import annotations

# import asyncio
import requests

import logging
from anyio import Any

from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from homeassistant.config_entries import ConfigEntry

# Import the device class from the component that you want to support
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)


ORDERED_NAMED_FAN_SPEEDS = ["1", "2", "3"]  # off is not included


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Awesome Light platform."""

    # Add devices
    fans = [["fan"]]
    async_add_entities(AirGo(entry.data) for fan in fans)


class AirGo(FanEntity):
    """Representation of an AirGo fan Light."""

    def __init__(self, fan) -> None:
        """Initialize an Fan."""
        self._room = fan["google_home_room_name"]
        self._name = fan["google_home_device_name"]
        self._username = fan["username"]
        self._host = fan["host"]

        self._attr_supported_features = FanEntityFeature.SET_SPEED
        self._attr_percentage = 1
        self._attr_speed_count = 3
        self._attr_unique_id = f"{self._name}_{self._room}"
        self.current_speed = ""
        self._attr_is_on = False

    @property
    def name(self) -> str:
        """Return the display name of this fan."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if fan is on."""
        return self._attr_is_on

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        requests.post(
            f"{self._host}/assistant",
            json={
                "user": f"{self._username}",
                "command": f"turn on {self._room} {self._name} fan",
            },
        )
        requests.post(
            f"{self._host}/assistant",
            json={
                "user": f"{self._username}",
                "command": f"set {self._room} {self._name} to 1",
            },
        )
        self._attr_is_on = True
        self.current_speed = "1"

    def turn_off(self, **kwargs: Any) -> None:
        requests.post(
            f"{self._host}/assistant",
            json={
                "user": f"{self._username}",
                "command": f"turn off {self._room} {self._name} fan",
            },
        )
        self._attr_is_on = False

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

    def set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        mode = percentage_to_ordered_list_item(ORDERED_NAMED_FAN_SPEEDS, percentage)
        requests.post(
            f"{self._host}/assistant",
            json={
                "user": f"{self._username}",
                "command": f"set {self._room} {self._name} fan to " + mode,
            },
        )

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        try:
            return ordered_list_item_to_percentage(
                ORDERED_NAMED_FAN_SPEEDS, self.current_speed
            )
        except ValueError:
            return 0

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(ORDERED_NAMED_FAN_SPEEDS)
