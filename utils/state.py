from config import DEFAULT_REPLIES, OWNER_ID
from utils.database import db


class State:
    def __init__(self):
        self.reload()
        self.AUTO_TASKS           = {}
        self.AUTO_TARGETS         = {}
        self.AUTO_MENTION_TASK    = None
        self.AUTO_MENTION_TARGET  = None
        self.REPLIES              = DEFAULT_REPLIES
        self.BASE_NAME            = None
        self.OWNER_ID             = OWNER_ID
        self.SESSION_NAME         = None
        self.HELP_BOT_USERNAME    = None
        self.HELP_BOT_CLIENT      = None
        self.HELP_BOT_START_ERROR = None

    def reload(self):
        self.ENEMIES = set(self._normalize_ids(db.get("enemies", [])))
        self.ENEMY_RESPONSES = {str(k): str(v) for k, v in db.get("enemy_responses", {}).items()}
        self.SPAMS = set(self._normalize_ids(db.get("spams", [])))
        self.AUTO_SPAMS = set(self._normalize_ids(db.get("auto_spams", [])))
        self.AUTO_MENTION_SPAMS = set(self._normalize_ids(db.get("auto_mention_spams", [])))
        self.MUTED = set(self._normalize_ids(db.get("muted", [])))
        self.REACTIONS = db.get("reactions", {})
        self.TIME_NAME = db.data.get("time_name", False)

    @staticmethod
    def _normalize_ids(values):
        normalized = []
        for value in values:
            try:
                normalized.append(int(value))
            except Exception:
                continue
        return normalized
        self.AUTO_TASKS           = {}
        self.AUTO_TARGETS         = {}
        self.AUTO_MENTION_TASK    = None
        self.AUTO_MENTION_TARGET  = None
        self.REPLIES              = DEFAULT_REPLIES
        self.BASE_NAME            = None
        self.OWNER_ID             = OWNER_ID
        self.SESSION_NAME         = None

    @staticmethod
    def _normalize_ids(values):
        normalized = []
        for value in values:
            try:
                normalized.append(int(value))
            except Exception:
                continue
        return normalized

    def add_enemy(self, uid, response=None):
        uid = int(uid)
        self.ENEMIES.add(uid)
        db.add("enemies", uid)
        self.ENEMY_RESPONSES[str(uid)] = response.strip() if response else ""
        db.data["enemy_responses"] = self.ENEMY_RESPONSES
        db.save()

    def remove_enemy(self, uid):
        uid = int(uid)
        self.ENEMIES.discard(uid)
        db.remove("enemies", uid)
        self.ENEMY_RESPONSES.pop(str(uid), None)
        db.data["enemy_responses"] = self.ENEMY_RESPONSES
        db.save()

    def clear_enemies(self):
        self.ENEMIES.clear()
        db.data["enemies"] = []
        self.ENEMY_RESPONSES = {}
        db.data["enemy_responses"] = {}
        db.save()

    def add_spam(self, uid):
        uid = int(uid)
        self.SPAMS.add(uid)
        db.add("spams", uid)

    def remove_spam(self, uid):
        uid = int(uid)
        self.SPAMS.discard(uid)
        db.remove("spams", uid)

    def clear_spams(self):
        self.SPAMS.clear()
        db.data["spams"] = []
        db.save()

    def add_auto_spam(self, uid):
        uid = int(uid)
        self.AUTO_SPAMS.add(uid)
        db.add("auto_spams", uid)
        self.AUTO_TARGETS.setdefault(uid, None)

    def remove_auto_spam(self, uid):
        uid = int(uid)
        self.AUTO_SPAMS.discard(uid)
        db.remove("auto_spams", uid)
        self.AUTO_TARGETS.pop(uid, None)
        if uid in self.AUTO_TASKS:
            self.AUTO_TASKS[uid].cancel()
            del self.AUTO_TASKS[uid]

    def clear_auto_spams(self):
        for uid in list(self.AUTO_TASKS.keys()):
            try:
                self.AUTO_TASKS[uid].cancel()
            except Exception:
                pass
        self.AUTO_TASKS.clear()
        self.AUTO_TARGETS.clear()
        self.AUTO_SPAMS.clear()
        db.data["auto_spams"] = []
        db.save()

    def add_auto_mention_spam(self, uid):
        uid = int(uid)
        self.AUTO_MENTION_SPAMS.add(uid)
        db.add("auto_mention_spams", uid)

    def remove_auto_mention_spam(self, uid):
        uid = int(uid)
        self.AUTO_MENTION_SPAMS.discard(uid)
        db.remove("auto_mention_spams", uid)
        if not self.AUTO_MENTION_SPAMS and self.AUTO_MENTION_TASK is not None:
            try:
                self.AUTO_MENTION_TASK.cancel()
            except Exception:
                pass
            self.AUTO_MENTION_TASK = None

    def clear_auto_mention_spams(self):
        if self.AUTO_MENTION_TASK is not None:
            try:
                self.AUTO_MENTION_TASK.cancel()
            except Exception:
                pass
        self.AUTO_MENTION_TASK = None
        self.AUTO_MENTION_TARGET = None
        self.AUTO_MENTION_SPAMS.clear()
        db.data["auto_mention_spams"] = []
        db.save()

    def add_muted(self, uid):
        self.MUTED.add(uid)
        db.add("muted", uid)

    def remove_muted(self, uid):
        self.MUTED.discard(uid)
        db.remove("muted", uid)

    def clear_muted(self):
        self.MUTED.clear()
        db.data["muted"] = []
        db.save()

    def set_reaction(self, uid, emoji):
        self.REACTIONS[str(uid)] = emoji
        db.data["reactions"] = self.REACTIONS
        db.save()

    def remove_reaction(self, uid):
        key = str(uid)
        if key in self.REACTIONS:
            del self.REACTIONS[key]
            db.data["reactions"] = self.REACTIONS
            db.save()

    def clear_reactions(self):
        self.REACTIONS.clear()
        db.data["reactions"] = {}
        db.save()

    def set_time_name(self, enabled: bool):
        self.TIME_NAME = enabled
        db.data["time_name"] = enabled
        db.save()

    def set_owner_id(self, owner_id):
        try:
            self.OWNER_ID = int(owner_id)
        except Exception:
            self.OWNER_ID = None

    def set_session_name(self, session_name):
        self.SESSION_NAME = session_name


state = State()
