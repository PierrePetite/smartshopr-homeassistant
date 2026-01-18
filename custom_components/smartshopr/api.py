"""SmartShopr API Client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class SmartShoprApiError(Exception):
    """Exception for SmartShopr API errors."""


class SmartShoprAuthError(SmartShoprApiError):
    """Exception for authentication errors."""


class SmartShoprApiClient:
    """Client for SmartShopr API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._session = session
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        url = f"{API_BASE_URL}/{endpoint}"

        try:
            async with asyncio.timeout(10):
                if method == "GET":
                    response = await self._session.get(url, headers=self._headers)
                elif method == "POST":
                    response = await self._session.post(url, headers=self._headers, json=data)
                elif method == "PATCH":
                    response = await self._session.patch(url, headers=self._headers, json=data)
                elif method == "DELETE":
                    response = await self._session.delete(url, headers=self._headers)
                else:
                    raise SmartShoprApiError(f"Unknown method: {method}")

                if response.status == 401:
                    raise SmartShoprAuthError("Invalid API key")

                if response.status == 403:
                    raise SmartShoprApiError("Access denied")

                if response.status >= 400:
                    error_data = await response.json()
                    raise SmartShoprApiError(error_data.get("error", "Unknown error"))

                return await response.json()

        except asyncio.TimeoutError as err:
            raise SmartShoprApiError("Request timeout") from err
        except aiohttp.ClientError as err:
            raise SmartShoprApiError(f"Connection error: {err}") from err

    async def validate_api_key(self) -> bool:
        """Validate the API key by fetching lists."""
        try:
            await self.get_lists()
            return True
        except SmartShoprAuthError:
            return False
        except SmartShoprApiError:
            # Other errors might be temporary, key might still be valid
            return True

    # Lists
    async def get_lists(self) -> list[dict[str, Any]]:
        """Get all shopping lists."""
        result = await self._request("GET", "lists")
        return result.get("lists", [])

    async def get_list_items(self, list_id: str) -> list[dict[str, Any]]:
        """Get items for a shopping list."""
        result = await self._request("GET", f"lists/{list_id}/items")
        return result.get("items", [])

    async def add_item(
        self,
        list_id: str,
        name: str,
        quantity_value: int = 1,
        quantity_unit: str | None = None,
    ) -> dict[str, Any]:
        """Add an item to a shopping list."""
        data = {
            "name": name,
            "quantity_value": quantity_value,
        }
        if quantity_unit:
            data["quantity_unit"] = quantity_unit

        result = await self._request("POST", f"lists/{list_id}/items", data)
        return result.get("item", {})

    async def update_item(
        self,
        item_id: str,
        is_completed: bool | None = None,
        name: str | None = None,
        quantity_value: int | None = None,
    ) -> dict[str, Any]:
        """Update an item."""
        data = {}
        if is_completed is not None:
            data["is_completed"] = is_completed
        if name is not None:
            data["name"] = name
        if quantity_value is not None:
            data["quantity_value"] = quantity_value

        result = await self._request("PATCH", f"items/{item_id}", data)
        return result.get("item", {})

    async def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        result = await self._request("DELETE", f"items/{item_id}")
        return result.get("success", False)

    # Budgets
    async def get_budgets(self) -> list[dict[str, Any]]:
        """Get all budgets."""
        result = await self._request("GET", "budgets")
        return result.get("budgets", [])

    # Expenses
    async def get_monthly_expenses(self) -> dict[str, Any]:
        """Get current month expenses."""
        return await self._request("GET", "expenses/month")
