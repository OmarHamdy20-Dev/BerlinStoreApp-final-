# BerlinStoreApp Developer Guide

## Overview

This project is a Windows-only Steam account manager built with `CustomTkinter`. It uses a single-file GUI architecture in `main.py`, with support for themes, account scanning, and animated navigation.

## Project structure

- `main.py`
  - App entry point and main class: `BerlinSteamApp`
  - Theme management via `ThemeManager`
  - Steam account scanning via `SteamManager`
  - Page and layout setup in `_build_layout`, `_build_sidebar`, `_build_pages`
  - Settings and runtime state updates
- `theme_config.json`
  - Stores selected theme
- `download.png`
  - Window icon file
- `logo.png`
  - Sidebar logo image
- `berlin_steam.log`
  - Log file created at runtime

## Main components

### `ThemeManager`

- Loads and saves theme selection from `theme_config.json`
- Applies colors defined in `THEMES` to widgets across the UI
- Supports multiple named themes: `dark`, `light`, `cyberpunk`, `ocean`, `neon`

### `SteamManager`

- Detects Steam installation path via Windows registry
- Reads account configuration files to list Steam accounts
- Returns account data for display in the accounts page

### `BerlinSteamApp`

- Initializes the app window and theme
- Builds the sidebar, pages, and status bar
- Handles page transitions and event callbacks
- Maintains UI state like current page, theme, and auto-refresh

## Development setup

1. Create or activate a Python virtual environment.
2. Install dependencies:

```powershell
pip install customtkinter
```

3. Run the app locally:

```powershell
py main.py
```

## Recommended workflow

- Edit layout and theming in `main.py`.
- Keep UI colors centralized in the `THEMES` dictionary.
- Use `logger` output to troubleshoot account detection and file reading.
- Keep image assets in the project root so `tk.PhotoImage` can load them reliably.

## Customizing themes

- Theme definitions live in the `THEMES` dictionary near the top of `main.py`.
- Each theme includes color keys like `main_bg`, `sidebar_bg`, `card_bg`, `accent`, and text colors.
- Theme selection persists by writing the selected theme name to `theme_config.json`.

## Troubleshooting

- If the app fails to detect Steam, confirm Steam is installed and the Windows registry contains the expected keys.
- If `logo.png` or `download.png` is not displayed, verify the files exist in the app folder and are valid PNG images.
- Use `berlin_steam.log` to inspect runtime errors and status messages.

## Notes

- The app is currently designed for Windows and uses `winreg`.
- For cross-platform support, remove registry dependency and replace Windows-specific Steam detection.
- Consider splitting `main.py` into modules for UI, theme management, and account logic if the project grows.
