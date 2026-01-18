"""Sensor platform for SmartShopr."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
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
    """Set up SmartShopr sensor entities."""
    coordinator: SmartShoprDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Monthly expenses sensor
    entities.append(SmartShoprMonthlyExpensesSensor(coordinator))

    # Budget sensors
    for budget in coordinator.data.get("budgets", []):
        entities.append(
            SmartShoprBudgetSensor(
                coordinator,
                budget["id"],
                budget["name"],
            )
        )

    async_add_entities(entities)


class SmartShoprMonthlyExpensesSensor(CoordinatorEntity, SensorEntity):
    """Sensor for monthly expenses."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = CURRENCY_EURO
    _attr_icon = "mdi:cash-register"

    def __init__(self, coordinator: SmartShoprDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = "smartshopr_monthly_expenses"
        self._attr_name = "SmartShopr Monthly Expenses"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        expenses = self.coordinator.data.get("expenses", {})
        totals = expenses.get("totals", {})
        # Return EUR total, or sum of all currencies
        if "EUR" in totals:
            return round(totals["EUR"], 2)
        elif totals:
            return round(sum(totals.values()), 2)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        expenses = self.coordinator.data.get("expenses", {})
        return {
            "month": expenses.get("month"),
            "expense_count": expenses.get("expense_count", 0),
            "totals_by_currency": expenses.get("totals", {}),
        }


class SmartShoprBudgetSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a budget's remaining amount."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_EURO
    _attr_icon = "mdi:piggy-bank"

    def __init__(
        self,
        coordinator: SmartShoprDataUpdateCoordinator,
        budget_id: str,
        budget_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._budget_id = budget_id
        self._budget_name = budget_name
        self._attr_unique_id = f"smartshopr_budget_{budget_id}"
        self._attr_name = f"Budget: {budget_name}"

    @property
    def _budget_data(self) -> dict[str, Any] | None:
        """Get the budget data from coordinator."""
        for budget in self.coordinator.data.get("budgets", []):
            if budget["id"] == self._budget_id:
                return budget
        return None

    @property
    def native_value(self) -> float | None:
        """Return remaining budget amount."""
        budget = self._budget_data
        if budget is None:
            return None
        return budget.get("remaining")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        budget = self._budget_data
        if budget is None:
            return {}

        attrs = {
            "budget_name": budget.get("name"),
            "target_amount": budget.get("target_amount"),
            "spent": budget.get("spent", 0),
            "expense_count": budget.get("expense_count", 0),
            "shared": budget.get("shared", False),
        }

        # Calculate percentage used
        target = budget.get("target_amount")
        spent = budget.get("spent", 0)
        if target and target > 0:
            attrs["percentage_used"] = round((spent / target) * 100, 1)

        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on budget status."""
        budget = self._budget_data
        if budget is None:
            return "mdi:piggy-bank"

        target = budget.get("target_amount")
        spent = budget.get("spent", 0)

        if target and target > 0:
            percentage = (spent / target) * 100
            if percentage >= 100:
                return "mdi:piggy-bank-outline"  # Over budget
            elif percentage >= 80:
                return "mdi:alert-circle"  # Warning
        return "mdi:piggy-bank"
