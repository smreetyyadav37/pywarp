import tomllib
from pathlib import Path
from typing import List

from pywarp.connectors.base import WarpSource, WarpSink
from pywarp.connectors.file import FileSource, FileJsonSink

# THE REGISTRY: Maps string names from TOML to actual Python Classes
CONNECTOR_REGISTRY = {
    "file_src": FileSource,
    "file_json_sink": FileJsonSink,
    # In the future, you just add: "kafka_src": KafkaSource
}

class TopologyManager:
    def __init__(self, project_root: str):
        self.topology_dir = Path(project_root) / "topology"
        self.active_sources: List[WarpSource] = []
        self.active_sinks: List[WarpSink] = []

    def load(self):
        """Scans the TOML files and instantiates the requested connectors."""
        print("[Topology] Scanning configuration files...")
        self._load_sources()
        self._load_sinks()

    def _load_sources(self):
        src_file = self.topology_dir / "sources" / "wpsrc.toml"
        if not src_file.exists():
            print(f"[Topology] Warning: Missing source config at {src_file}")
            return

        with open(src_file, "rb") as f:
            data = tomllib.load(f)
            
            # Loop through all sources defined in the TOML
            for src_cfg in data.get("sources", []):
                if src_cfg.get("enable", False):  # Only load if enabled = true
                    c_type = src_cfg["connect"]
                    if c_type in CONNECTOR_REGISTRY:
                        # Dynamically create the class!
                        connector_class = CONNECTOR_REGISTRY[c_type]
                        instance = connector_class(src_cfg.get("params", {}))
                        self.active_sources.append(instance)
                        print(f"[Topology] Loaded Source: {src_cfg.get('key')} ({c_type})")

    def _load_sinks(self):
        # For simplicity, we target the business demo sink
        sink_file = self.topology_dir / "sinks" / "business.d" / "demo.toml"
        if not sink_file.exists():
            print(f"[Topology] Warning: Missing sink config at {sink_file}")
            return

        with open(sink_file, "rb") as f:
            data = tomllib.load(f)
            
            for sink_cfg in data.get("sink_group", {}).get("sinks", []):
                c_type = sink_cfg["connect"]
                if c_type in CONNECTOR_REGISTRY:
                    connector_class = CONNECTOR_REGISTRY[c_type]
                    instance = connector_class(sink_cfg.get("params", {}))
                    self.active_sinks.append(instance)
                    print(f"[Topology] Loaded Sink: {sink_cfg.get('name')} ({c_type})")