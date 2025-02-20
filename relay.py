import time
import logging
from typing import Optional

from utils.device import run_adb, get_device_id
from relay_csv_manager import load_existing_relay_subs, cleanup_relay_csv
from res import RESFile


class RelayAutomation:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id or get_device_id()
        self.RELAY_PACKAGE = "reddit.news"
        self.RELAY_FILTER_ACTIVITY = "reddit.news.IntentFilterActivity"

    def add_subreddit_filter(self, subreddit: str) -> bool:
        try:
            run_adb(f"shell input text {subreddit}", self.device_id)
            time.sleep(0.5)
            # Location of submit button (+) in Relay For Reddit Filter list
            run_adb("shell input tap 863 610", self.device_id)
            time.sleep(1)
            return True
        except Exception as e:
            logging.error(f"Failed to add filter for {subreddit}: {e}")
            return False

    def sync_from_res(
        self,
        res_backup: str,
        csv_path: str = "data/relay.csv",
        max_additions: int = None,
    ) -> None:
        logging.info(f"Syncing subreddits using RES backup: {res_backup}")
        res_obj = RESFile(res_backup)
        subs = res_obj.extract_subreddits()

        existing_subs = load_existing_relay_subs(csv_path)
        pre_filter_count = len(subs)
        subs = [sub for sub in subs if sub not in existing_subs]
        logging.info(
            f"Filtered subreddits from {pre_filter_count} to {len(subs)} after excluding CSV entries"
        )

        count = 0
        for sub in sorted(subs):
            if max_additions is not None and count >= max_additions:
                break
            logging.info(f"Attempting to add filter for subreddit: {sub}")
            success = self.add_subreddit_filter(sub)
            if success:
                logging.info(f"Successfully added filter for {sub}")
                count += 1
            else:
                logging.error(f"Failed to add filter for {sub}")
            time.sleep(1.5)
        logging.info(f"Completed syncing filters. Total filters added: {count}")

        # Optionally cleanup CSV after sync
        cleanup_relay_csv(csv_path)
