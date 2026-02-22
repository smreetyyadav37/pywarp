import json
import os
from pathlib import Path
from pywarp.connectors.base import WarpSource, WarpSink

class FileSource(WarpSource):
    async def connect(self):
        base_path = Path(self.config.get("base", "."))
        file_path = base_path / self.config.get("file", "in.dat")
        
        if not file_path.exists():
            print(f"[FileSource] Warning: {file_path} does not exist. Creating mock file.")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text('127.0.0.1 - - [06/Aug/2019:12:12:19 +0800] "GET /mock HTTP/1.1"\n')
            
        self.file_handle = open(file_path, "r", encoding="utf-8")
        print(f"[FileSource] Connected to {file_path}")

    async def read_stream(self):
        if self.file_handle:
            for line in self.file_handle:
                yield line.strip()

    async def close(self):
        if self.file_handle:
            self.file_handle.close()
            print(f"[FileSource] Closed connection.")

class FileJsonSink(WarpSink):
    async def connect(self):
        base_path = Path(self.config.get("base", "."))
        file_path = base_path / self.config.get("file", "out.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open in append mode with explicit encoding
        self.file_handle = open(file_path, "a", encoding="utf-8")
        print(f"[FileJsonSink] Connected to {file_path}")

    async def write(self, data: dict):
        if self.file_handle:
            # We use json.dumps and add a real newline character.
            # os.linesep ensures compatibility across Windows/Linux.
            record = json.dumps(data) + os.linesep
            self.file_handle.write(record)
            
            # Flush ensures the record is written to disk immediately
            # preventing the 'one long line' buffering issue in VS Code.
            self.file_handle.flush()
            print(f"[FileJsonSink] Wrote record to {self.config.get('file')}")

    async def close(self):
        if self.file_handle:
            self.file_handle.close()
            print(f"[FileJsonSink] Closed connection.")
        