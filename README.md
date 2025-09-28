# Discord Giveaway Manager Bot

This project is a comprehensive Discord bot designed to manage giveaways with advanced entry requirements and multipliers, track invites, log important events, and facilitate server management with role and channel configurations. The bot utilizes Discord's modern interaction features including slash commands, buttons, and dropdown menus to provide an interactive and user-friendly experience.

The bot stores giveaway data, user invites, voice chat durations, and messages in JSON and SQLite databases to ensure persistence and accuracy.

---

The bot is written in Python using the `discord.py` library with full intent permissions enabled. It supports creating giveaways with customizable parameters such as title, description, duration, emoji, number of winners, and entry requirements including account age, membership length, roles, activity, voice chat duration, and custom statuses.

Users interact with the bot primarily through slash commands and buttons which trigger rich Discord UI components for selecting requirements and multipliers, starting giveaways, and configuring server permissions.

The bot also handles invite tracking by listening to member joins and leaves, updating invite statistics, and logging these events to configurable Discord channels.

Blacklisting features allow server administrators to prevent certain roles or channels from using the bot. Role addition/removal commands give admins control over who can manage giveaway configurations.

---

### Usage

- Run the bot with Python after installing dependencies (`discord.py`, `pytz`, `python-dateutil`, etc.).
- Configure `config.json` to specify server IDs, roles allowed to use the bot, blacklisted roles/channels, and log channel IDs.
- Run the bot, and use slash commands (e.g., `/giveaway`, `/leaderboard`, `/server`) to create giveaways, view statistics, and configure settings.
- Use interactive dropdowns and buttons to set giveaway requirements such as minimum account age, roles required, message activity, voice chat duration, and more.
- The bot ensures only qualified users can enter giveaways by validating requirements before allowing entries.
- Giveaway winners receive notifications, and customizable private win messages can be sent.
- Logs are posted in dedicated channels about user invites, giveaway events, and dropped messages.

---

### Features Summary

- Advanced giveaway creation with flexible requirements and multipliers.
- Interactive Discord UI components for bot commands.
- Persistent storage of giveaways in SQLite and configurations in JSON.
- Invite tracking with join/leave detection and invite usage counts.
- User activity tracking including message count and voice chat time.
- Role and channel blacklisting to restrict bot usage.
- Server settings interface with role/channel management buttons.
- Multi-guild support with custom configuration per server.
- Slash commands and buttons integration for modern Discord bots.
- Embedded messages with rich formatting and images for giveaways.

---

### Dependencies

- Python 3.8+
- `discord.py` (preferably version supporting Discord UI components)
- `pytz`
- `python-dateutil`
- `sqlite3` (standard Python library)
- Other common dependencies like `json`, `asyncio`, and `random`

---

This bot project is ideal for server admins looking to run fair and configurable giveaways with detailed participant filtering, and to maintain community engagement through invite tracking and activity logging.

---


For customization, extend `config.json` and other JSON data files to adjust behavior and appearance. Update the main bot file to add new commands or features as needed.
