from typing import Dict, Any
import os
from datetime import datetime
import re
import ipaddress

class OMLEngine:
    def __init__(self):
        self.cc_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        self.pwd_pattern = re.compile(r'(password|pwd|secret|token)=([^&\s]+)', re.IGNORECASE)

    def transform(self, parsed_data: dict) -> dict:
        if "_error" in parsed_data: return parsed_data

        # --- 1. Deep PII & Advanced 1NF Splitting ---
        req = parsed_data.get("request", "-")
        if req != "-" and req != '""' and req != '"-"':
            # Mask sensitive parameters in URL
            req = self.cc_pattern.sub("[REDACTED_CC]", req)
            req = self.pwd_pattern.sub(r'\1=[REDACTED_SECRET]', req)
            parsed_data["request"] = req

            # Optimized Regex: Ignores stray/unclosed quotes (Fixes clean7.csv)
            m = re.match(r'^\"?([A-Z]+)\s+(/.*?)?(?:\s+(HTTP/[\d\.]+))?\"?$', req)
            if m:
                parsed_data["http_method"] = m.group(1)
                parsed_data["endpoint"] = m.group(2) or "UNKNOWN"
                parsed_data["protocol"] = m.group(3) or "UNKNOWN"
            else:
                parsed_data["http_method"], parsed_data["endpoint"], parsed_data["protocol"] = "UNKNOWN", req, "UNKNOWN"
        else:
            parsed_data["http_method"], parsed_data["endpoint"], parsed_data["protocol"] = "UNKNOWN", "-", "UNKNOWN"

        # --- 2. IP & User Validation ---
        ip_str = parsed_data.get("ip", "-")
        parsed_data["ip_masked"] = ip_str 
        if ip_str != "-":
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if ip_obj.version == 4:
                    parts = ip_str.split('.')
                    parsed_data["ip_masked"] = f"{parts[0]}.{parts[1]}.*.*"
                elif ip_obj.version == 6:
                    parts = ip_str.split(':')
                    parsed_data["ip_masked"] = f"{parts[0]}:{parts[1]}:*:*:*:*"
            except ValueError:
                parsed_data["_error"] = "dq_invalid_ip"

        user = parsed_data.get("user", "-")
        if user not in ["-", None]:
            parsed_data["user_masked"] = " ".join([n[0] + "***" for n in user.split() if n])

        # --- 3. Time Formatting ---
        raw_time = parsed_data.get("time", "")
        if raw_time and raw_time != "-":
            parsed_data["time_iso"] = self._parse_time(raw_time)

        # --- 4. Business Rule Enforcement ---
        try:
            status = int(float(parsed_data.get("status", 0)))
            parsed_data["status"] = status if 100 <= status <= 599 else 0
        except (ValueError, TypeError):
            parsed_data["status"] = 0
        
        return parsed_data

    def _parse_time(self, raw_time: str) -> str:
        t = raw_time.replace(" UTC", " +0000").replace(" IST", " +0530").replace("Z", "+00:00")
        
        formats = [
            "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", 
            "%m/%d/%Y:%H:%M:%S %z", "%m/%d/%Y:%H:%M:%S",
            "%d-%m-%Y:%H:%M:%S %z", "%d-%m-%Y:%H:%M:%S",
            "%d/%b/%Y:%H:%M:%S %z", "%d/%b/%Y:%H:%M:%S", 
            "%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", 
            "%Y/%m/%d %H:%M:%S", "%A, %d-%b-%Y %H:%M:%S %z", "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try: 
                dt = datetime.strptime(t, fmt) if 'T' not in fmt or len(t) < 20 else datetime.fromisoformat(t)
                if 2000 <= dt.year <= datetime.now().year + 1:
                    return dt.isoformat()
                return raw_time 
            except ValueError: continue
            
        if t.isdigit() and len(t) >= 10:
            try: 
                dt = datetime.fromtimestamp(int(t))
                if 2000 <= dt.year <= datetime.now().year + 1: return dt.isoformat()
            except Exception: pass
        return raw_time