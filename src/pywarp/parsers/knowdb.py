import sqlite3
from typing import Dict, Any
import time

class KnowledgeDatabase:
    def __init__(self):
        # check_same_thread=False allows Streamlit to use this seamlessly
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.last_update = 0
        self._setup_db()

    def _setup_db(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS network_assets (ip_prefix TEXT PRIMARY KEY, department TEXT, threat_level TEXT)")
        self._refresh_threat_intel() # Load initial data

    def _refresh_threat_intel(self):
        """Simulates fetching fresh threat intel every 10 minutes to prevent stale data (Issue #5)"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM network_assets") # Clear old data
        mock_data = [
            ('222.133', 'External_Web', 'High'),
            ('192.168', 'Engineering', 'Low'),
            ('10.0', 'HR_Internal', 'Low'),
            ('8.8', 'Public_DNS', 'Safe'),
            ('2001:0db8', 'IPv6_Gateway', 'Low') # IPv6 Support
        ]
        cursor.executemany("INSERT INTO network_assets VALUES (?, ?, ?)", mock_data)
        self.conn.commit()
        self.last_update = time.time()

    def enrich(self, parsed_data: dict) -> dict:
        if "_error" in parsed_data: return parsed_data

        # Auto-refresh if data is older than 10 minutes
        if time.time() - self.last_update > 600:
            self._refresh_threat_intel()

        # Issue #1: Fallback logic for missing or malformed IPs
        ip = parsed_data.get("ip", "-")
        if ip == "-" or parsed_data.get("_error") == "dq_invalid_ip":
            parsed_data["department"] = "Unknown"
            parsed_data["threat_level"] = "Unverified"
            return parsed_data

        # IP Matching Logic
        prefix = ""
        if ":" in ip:
            prefix = ":".join(ip.split(":")[:2])
        elif "." in ip:
            prefix = ".".join(ip.split(".")[:2])

        cursor = self.conn.cursor()
        cursor.execute("SELECT department, threat_level FROM network_assets WHERE ip_prefix = ?", (prefix,))
        result = cursor.fetchone()

        if result:
            parsed_data["department"], parsed_data["threat_level"] = result
        else:
            parsed_data["department"] = "External_Traffic"
            parsed_data["threat_level"] = "Unverified"

        return parsed_data