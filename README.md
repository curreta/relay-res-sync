# README

## Overview

This project provides scripts to sync subreddit filters stored in your Reddit Enhancement Suite to the Relay for Reddit Android application via ADB.

## Setup

- Use UV
- Ensure `adb` is installed and available in your PATH.
- For OCR, install Tesseract.

## Data Folder Structure

The project expects a `data` folder with the following files:

- `RES.json`: A backup export file from Reddit Enhancement Suite (RES)
- `relay.csv`: Generated automatically when getting the list of subreddits stored in your Android app. Contains the list of currently filtered subreddits from the Relay app.

## Pre-Run Setup

Before running any commands, the main entrypoint (`main.py`) executes a pre-run setup that:

- Verifies ADB availability
- Checks Tesseract OCR installation
- Validates Android device connection
- Configures logging

## Usage

All commands use UV. For most common operations:

```bash
# Sync filters from RES backup (data/RES.json) to Relay
uv run main.py filters sync-all

# Add specific subreddit filters
uv run main.py filters add "subreddit1, subreddit2"

# Show status
uv run main.py status

# Update Relay CSV through OCR scanning
uv run main.py update-csv
```

### Advanced Options

The commands above support additional parameters for custom configurations:

```bash
# Custom RES backup location and device ID
uv run main.py filters sync-all path/to/backup.json --device DEVICE_ID --max-additions 50

# Status with custom file paths
uv run main.py status path/to/backup.json path/to/relay.csv

# Update CSV with iteration limit
uv run main.py update-csv --max-iterations 100
```

## Finding the Filter Button Coordinates

The script requires the exact screen coordinates of the "+" button in Relay's filter list. To find these coordinates:

1. Connect your device and enable USB debugging
2. Open Relay for Reddit and navigate to Settings > Filters
3. In your terminal/command prompt run:
   ```bash
   adb shell getevent -l
   ```
4. Tap the "+" button in Relay's filter list
5. Look for position values in the output:
   ```
   /dev/input/event3: EV_ABS       ABS_MT_POSITION_X    0000035f
   /dev/input/event3: EV_ABS       ABS_MT_POSITION_Y    00000262
   ```
6. Convert these hex values to decimal (currently configured as X: 863, Y: 610)
7. Update the coordinates in `relay.py`'s `add_subreddit_filter` method if they differ on your device

Note: These coordinates are device-specific and depend on screen resolution and density. The current values (863, 610) work for the original development device.

## Additional Notes

- Note: I had to stop using ENTER for submitting the words to the filter and move to a coordinate where the + button is on the app because pressing ENTER would sometimes insert a space between subreddits (e.g., "AccidentalRenaissance" would become "Accidental Renaissance" and fail to submit)
- Note: Tesseract coupled with the font used when capturing subreddit lists from the app page by page sometimes confuses zeros with O's.
- Note: The OCR filtering is currently manually cropping based on what works for my phone screen, and will probably not crop properly on other phone devices. Future improvement could include a calibrate command to determine the proper crop location and submit button coordinates for different devices.
