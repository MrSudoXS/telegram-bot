import json
import os
from config import DB_FILE


class Database:
    def __init__(self, db_file=None):
        self.db_file = db_file or DB_FILE
        self.data = {
            "enemies":             [],
            "spams":               [],
            "auto_spams":          [],
            "auto_mention_spams":  [],
            "muted":               [],
            "reactions":           {},
            "time_name":           False,
        }
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.data.pop("banned", None)
            else:
                self.data = {
                    "enemies":             [],
                    "spams":               [],
                    "auto_spams":          [],
                    "auto_mention_spams":  [],
                    "muted":               [],
                    "reactions":           {},
                    "time_name":           False,
                }
        except Exception as e:
            print(f"[db load] {e}")

    def set_db_file(self, db_file):
        self.db_file = db_file
        self._load()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.db_file) or ".", exist_ok=True)
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[db save] {e}")

    def add(self, key, value):
        if key not in self.data:
            self.data[key] = []
        if value not in self.data[key]:
            self.data[key].append(value)
            self.save()

    def remove(self, key, value):
        if key in self.data and value in self.data[key]:
            self.data[key].remove(value)
            self.save()

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else [])


db = Database()
