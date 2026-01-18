"""DataUpdateCoordinator for SmartShopr."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SmartShoprApiClient, SmartShoprApiError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SmartShoprDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching SmartShopr data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: SmartShoprApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from SmartShopr API."""
        try:
            # Fetch all data in parallel
            lists = await self.client.get_lists()
            budgets = await self.client.get_budgets()
            expenses = await self.client.get_monthly_expenses()

            # Fetch items for each list
            lists_with_items = []
            for shopping_list in lists:
                items = await self.client.get_list_items(shopping_list["id"])
                lists_with_items.append({
                    **shopping_list,
                    "items": items,
                })

            return {
                "lists": lists_with_items,
                "budgets": budgets,
                "expenses": expenses,
            }

        except SmartShoprApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
