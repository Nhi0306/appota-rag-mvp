from __future__ import annotations

import json
import os
import uuid
from datetime import datetime


class AuditLogger:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def log(self, record: dict) -> str:
        rid = str(uuid.uuid4())[:8]
        record = dict(record)
        record["audit_id"] = rid
        record["timestamp"] = datetime.now().isoformat()
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        except OSError:
            pass
        return rid
