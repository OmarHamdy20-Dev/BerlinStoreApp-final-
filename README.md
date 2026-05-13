# BerlinStoreApp

A polished Steam account manager for Windows, designed for users who want fast Steam account switching, modern themes, and a clean interface.

## What it does

BerlinStoreApp detects Steam installations, lists Steam accounts, and provides a user-friendly dashboard for switching profiles and customizing the UI.

## Features

- ✅ Modern dashboard with quick action cards
- ✅ Automatic Steam account detection
- ✅ Animated page transitions and responsive interface
- ✅ Multiple theme support: Dark, Light, Cyberpunk, Ocean, Neon
- ✅ Settings page for themes, animations, scaling, and auto-refresh
- ✅ Custom icon support using `download.png`
- ✅ Sidebar logo support with `logo.png`

## Requirements

- Windows 10 or 11
- Python 3.9 or newer
- `customtkinter` package

## How to use

1. Start the app.
2. Use the **Dashboard** for a quick overview.
3. Switch to **Accounts** to refresh and manage Steam accounts.
4. Open **Settings** to select a theme and adjust UI preferences.

## Important files

- `main.py` — main application code
- `theme_config.json` — saved theme selection
- `download.png` — window icon image
- `logo.png` — sidebar logo image
- `berlin_steam.log` — runtime log file

## Notes

- Steam path is detected via the Windows registry.
- Themes are saved automatically in `theme_config.json`.

## License

No license specified. Use and modify as needed.
 
