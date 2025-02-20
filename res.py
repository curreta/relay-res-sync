import json
from typing import List
import logging

logger = logging.getLogger(__name__)


class RESFile:
    def __init__(self, res_backup_path: str):
        self.res_backup_path = res_backup_path
        self.data = self._load_data()

    def _load_data(self):
        logging.debug(f"Loading data from: {self.res_backup_path}")
        with open(self.res_backup_path) as f:
            return json.load(f)

    def extract_subreddits(self) -> List[str]:
        logging.debug("Extracting subreddits")
        return [
            item[0]
            for item in self.data["data"]["RESoptions.filteReddit"]["subreddits"][
                "value"
            ]
            if item and item[0]
        ]
