"""
Relay CSV Manager Module

This module provides functions to update and clean the CSV file used exclusively by Relay.
"""

import csv
import os
import time
import logging
import tempfile
from rich.console import Console
from utils.device import run_adb
from ocr_filters import process_image

console = Console()


def _initialize_csv(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Subreddit"])


def _append_subreddits(csv_path: str, subreddits: list) -> None:
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for sub in subreddits:
            writer.writerow([sub])
    console.print(f"Wrote batch of {len(subreddits)} subreddits to CSV")


def _process_screenshot(device_id: str) -> list:
    run_adb("shell screencap -p /sdcard/ocr_temp.png", device_id)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        local_path = tmp.name
    run_adb(f"pull /sdcard/ocr_temp.png {local_path}", device_id)
    time.sleep(1)
    raw_subs = process_image(local_path)
    os.remove(local_path)
    valid_subs = []
    for sub in raw_subs:
        clean = sub.strip()  # ...existing cleaning logic...
        if clean and clean not in valid_subs:
            valid_subs.append(clean)
    return valid_subs


def load_existing_relay_subs(csv_path: str) -> set:
    """Load existing subreddits from the Relay CSV file."""
    subs = set()
    if not os.path.exists(csv_path):
        return subs
    with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip header
        for row in reader:
            if row and row[0].strip():
                subs.add(row[0].strip())
    return subs


def update_relay_csv(
    max_iterations: int,
    csv_path: str = "data/relay.csv",
    device_id: str = None,
) -> None:
    _initialize_csv(csv_path)
    previous_subs = set()
    iteration = 0
    batch_size = 10
    new_subs_batch = []

    while iteration < max_iterations:
        iteration += 1
        console.print(f"Iteration {iteration}...")
        valid_subs = _process_screenshot(device_id)
        console.print(f"Found {len(valid_subs)} subreddits: {', '.join(valid_subs)}")

        if set(valid_subs) == previous_subs:
            console.print("OCR results repeated; assuming end of list reached.")
            break

        previous_subs = set(valid_subs)
        new_subs_batch.extend(valid_subs)

        if iteration % batch_size == 0 or iteration == max_iterations:
            if new_subs_batch:
                _append_subreddits(csv_path, new_subs_batch)
                new_subs_batch = []

        console.print("Swiping up to load more...")
        run_adb("shell input swipe 500 1500 500 780 300", device_id)
        time.sleep(2)

    if new_subs_batch:
        _append_subreddits(csv_path, new_subs_batch)
    console.print(f"Completed writing to CSV: {csv_path}")


def cleanup_relay_csv(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    subreddits = set()
    with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip header
        for row in reader:
            if row and row[0].strip():
                subreddits.add(row[0].strip())

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Subreddit"])
        for sub in sorted(subreddits):
            writer.writerow([sub])

    logging.info(f"Cleaned up Relay CSV file: {csv_path}")
