import re
from typing import Dict, Any
import html
import hashlib
from collections import deque

class WPLParser:
    def __init__(self):
        # Extracts alpha statuses ("OK") and negative numbers ("-100") 
        self.pattern = re.compile(
            r'^(?P<ip>[\w\.:]+|-)\s+(?:-\s+)?(?P<user>".*?"|[^\[\]]+?|-)\s+\[(?P<time>.*?)\]\s+(?:\"(?P<request>.*)\"|(?P<request_unquoted>.*?))(?:\s+(?P<status>-?\d+|[A-Za-z]+))?\s*$'
        )
        self.seen_hashes = deque(maxlen=5000)

    def parse(self, raw_log: str) -> dict:
        if not raw_log or str(raw_log).strip() == "":
            return {"_error": "wpl_empty", "raw_payload": ""}

        log_hash = hashlib.md5(raw_log.encode('utf-8')).hexdigest()
        if log_hash in self.seen_hashes:
            return {"_error": "dq_duplicate", "raw_payload": raw_log.strip()}
        self.seen_hashes.append(log_hash)

        match = self.pattern.search(raw_log)
        if not match:
            return {"_error": "wpl_miss", "raw_payload": raw_log.strip()}

        data = match.groupdict()
        
        # Consolidate Request & Targeted XSS Stripping
        raw_req = data.get("request") or data.get("request_unquoted") or "-"
        data["request"] = re.sub(r'<[^>]*>', '', raw_req.strip()) 
        
        if "request_unquoted" in data: del data["request_unquoted"]
            
        if data.get("user"):
            data["user"] = data["user"].replace('"', '').strip()
            
        return {k: v for k, v in data.items() if v is not None}