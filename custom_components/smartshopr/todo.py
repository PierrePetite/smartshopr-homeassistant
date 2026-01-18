"""Todo platform for SmartShopr."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartShoprDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SmartShopr todo entities."""
    coordinator: SmartShoprDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for shopping_list in coordinator.data.get("lists", []):
        entities.append(
            SmartShoprTodoListEntity(
                coordinator,
                shopping_list["id"],
                shopping_list["name"],
                shopping_list.get("shared", False),
            )
        )

    async_add_entities(entities)


class SmartShoprTodoListEntity(CoordinatorEntity, TodoListEntity):
    """A SmartShopr shopping list as a todo entity."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(
        self,
        coordinator: SmartShoprDataUpdateCoordinator,
        list_id: str,
        list_name: str,
        is_shared: bool,
    ) -> None:
        """Initialize the todo list entity."""
        super().__init__(coordinator)
        self._list_id = list_id
        self._list_name = list_name
        self._is_shared = is_shared
        self._attr_unique_id = f"smartshopr_list_{list_id}"
        self._attr_name = list_name

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:cart" if not self._is_shared else "mdi:cart-heart"

    @property
    def todo_items(self) -> list[TodoItem]:
        """Return the todo items."""
        items = []
        for shopping_list in self.coordinator.data.get("lists", []):
            if shopping_list["id"] == self._list_id:
                for item in shopping_list.get("items", []):
                    status = (
                        TodoItemStatus.COMPLETED
                        if item.get("is_completed")
                        else TodoItemStatus.NEEDS_ACTION
                    )
                    # Format name with quantity if > 1
                    name = item["name"]
                    qty = item.get("quantity_value", 1)
                    unit = item.get("quantity_unit")
                    if qty > 1:
                        if unit:
                            name = f"{name} ({qty} {unit})"
                        else:
                            name = f"{name} (x{qty})"
                    elif unit:
                        name = f"{name} ({unit})"

                    items.append(
                        TodoItem(
                            uid=item["id"],
                            summary=name,
                            status=status,
                        )
                    )
                break
        return items

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a new todo item."""
        # Parse name for quantity (e.g., "Milk x2" or "2 Milk")
        name = item.summary
        quantity = 1

        # Check for "x2" at end
        if " x" in name:
            parts = name.rsplit(" x", 1)
            if len(parts) == 2 and parts[1].isdigit():
                name = parts[0]
                quantity = int(parts[1])

        # Check for number at start (e.g., "2 Milk")
        parts = name.split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            quantity = int(parts[0])
            name = parts[1]

        await self.coordinator.client.add_item(
            self._list_id,
            name,
            quantity,
        )
        await self.coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a todo item."""
        is_completed = item.status == TodoItemStatus.COMPLETED
        await self.coordinator.client.update_item(
            item.uid,
            is_completed=is_completed,
        )
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete todo items."""
        for uid in uids:
            await self.coordinator.client.delete_item(uid)
        await self.coordinator.async_request_refresh()
