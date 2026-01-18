# SmartShopr for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/PierrePetite/smartshopr-homeassistant)](https://github.com/PierrePetite/smartshopr-homeassistant/releases)
[![License](https://img.shields.io/github/license/PierrePetite/smartshopr-homeassistant)](LICENSE)

<p align="center">
  <img src="https://smartshopr.de/img/smartshopr_icon.png" width="128" height="128" alt="SmartShopr Icon">
</p>

<p align="center">
  <strong>Bring your SmartShopr shopping lists into Home Assistant!</strong>
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| **Shopping Lists** | All your lists (owned + shared) appear as Todo entities |
| **Add Items** | Add items via voice assistant, automation, or Lovelace |
| **Check Off Items** | Mark items as completed directly in Home Assistant |
| **Budget Sensors** | Track your remaining budget with real-time sensors |
| **Expense Tracking** | Monitor monthly expenses with dedicated sensor |
| **Real-time Sync** | Changes sync automatically with the SmartShopr app |

---

## Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click the **three dots** (top right) → **Custom repositories**
4. Add repository: `https://github.com/PierrePetite/smartshopr-homeassistant`
5. Category: **Integration**
6. Search for **SmartShopr** and click **Download**
7. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/smartshopr` folder
2. Copy it to your `config/custom_components/` directory
3. Restart Home Assistant

---

## Configuration

### Step 1: Get your API Key

1. Open the **SmartShopr app** on your iPhone
2. Go to **Settings → Home Assistant**
3. Tap **"Create new API Key"**
4. **Copy the key** (it's only shown once!)

### Step 2: Add Integration

1. In Home Assistant: **Settings → Devices & Services → Add Integration**
2. Search for **SmartShopr**
3. Paste your API Key
4. Done!

---

## Entities

### Todo Lists (Shopping Lists)

Each shopping list becomes a `todo` entity:

```
todo.smartshopr_<list_name>
```

**Supported operations:**
- View items
- Add items (with quantity: `"Milk x2"` or `"2 Milk"`)
- Check off items
- Delete items

### Sensors

**Monthly Expenses:**
```
sensor.smartshopr_monthly_expenses
```
- Current month's total spending
- Attributes: `expense_count`, `totals_by_currency`

**Budget Sensors:**
```
sensor.smartshopr_budget_<budget_name>
```
- Remaining budget amount
- Attributes: `target_amount`, `spent`, `percentage_used`, `expense_count`

---

## Automation Examples

### Add Item via Voice Assistant

```yaml
alias: "Shopping List: Add Item"
trigger:
  - platform: conversation
    command: "Add {item} to the shopping list"
action:
  - service: todo.add_item
    target:
      entity_id: todo.smartshopr_groceries
    data:
      item: "{{ trigger.slots.item }}"
```

### Budget Warning at 80%

```yaml
alias: "Budget Warning"
trigger:
  - platform: template
    value_template: >
      {{ state_attr('sensor.smartshopr_budget_groceries', 'percentage_used') | float > 80 }}
action:
  - service: notify.mobile_app_iphone
    data:
      title: "Budget Warning"
      message: "Your grocery budget is {{ state_attr('sensor.smartshopr_budget_groceries', 'percentage_used') }}% used!"
```

### Daily Shopping Summary

```yaml
alias: "Daily Shopping Summary"
trigger:
  - platform: time
    at: "19:00:00"
action:
  - service: notify.mobile_app_iphone
    data:
      title: "Shopping Summary"
      message: >
        Open items: {{ states('todo.smartshopr_groceries') }}
        Spent this month: {{ states('sensor.smartshopr_monthly_expenses') }}€
```

### Add to List When Item Runs Low

```yaml
alias: "Auto-add milk when low"
trigger:
  - platform: numeric_state
    entity_id: sensor.fridge_milk_level
    below: 20
action:
  - service: todo.add_item
    target:
      entity_id: todo.smartshopr_groceries
    data:
      item: "Milk"
```

---

## Lovelace Cards

### Shopping List Card

```yaml
type: todo-list
entity: todo.smartshopr_groceries
```

### Budget Progress Card

```yaml
type: gauge
entity: sensor.smartshopr_budget_groceries
name: Grocery Budget
unit: €
min: 0
max: 300
severity:
  green: 0
  yellow: 200
  red: 250
```

### Expenses Card

```yaml
type: statistic
entity: sensor.smartshopr_monthly_expenses
name: This Month
stat_type: state
```

---

## Privacy & Security

- API keys are securely stored in Home Assistant
- All communication uses HTTPS
- Data hosted in Frankfurt, Germany (GDPR compliant)
- No tracking, no ads

---

## Troubleshooting

### Integration not showing up?
- Make sure you restarted Home Assistant after installation
- Check the logs: **Settings → System → Logs**

### Items not syncing?
- The integration polls every 30 seconds
- Force refresh: **Developer Tools → Services → `homeassistant.update_entity`**

### Invalid API Key?
- API keys start with `sk_live_`
- Generate a new key in the SmartShopr app if needed

---

## Get SmartShopr

<p align="center">
  <a href="https://apps.apple.com/app/smartshopr-einkaufsliste/id6756917360">
    <img src="https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us" alt="Download on the App Store" height="50">
  </a>
</p>

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **App Support:** smartshopr@ug108.de
- **GitHub Issues:** [Report a bug](https://github.com/PierrePetite/smartshopr-homeassistant/issues)
- **Website:** [smartshopr.de](https://smartshopr.de)

---

<p align="center">
  Made with ❤️ in Germany
</p>
