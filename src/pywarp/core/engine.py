import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Any

from pywarp.core.topology import TopologyManager
from pywarp.parsers.wpl import WPLParser
from pywarp.parsers.oml import OMLEngine
from pywarp.parsers.knowdb import KnowledgeDatabase

_wpl_parser = None
_oml_engine = None
_know_db = None

def _init_worker():
    """Initializes the parsers and memory DB once per CPU core on startup."""
    global _wpl_parser, _oml_engine, _know_db
    _wpl_parser = WPLParser()
    _oml_engine = OMLEngine()
    _know_db = KnowledgeDatabase()

def wpl_parse_worker(raw_log: str) -> Dict[str, Any]:
    """Executes the WPL tokenization, OML transformation, and SQL enrichment."""
    parsed_data = _wpl_parser.parse(raw_log)
    transformed_data = _oml_engine.transform(parsed_data)
    final_data = _know_db.enrich(transformed_data)
    return final_data

class WarpEngine:
    def __init__(self, parse_workers: int = 2, project_root: str = "."):
        self.parse_workers = parse_workers
        self.ingestion_queue = asyncio.Queue(maxsize=10000)
        self.routing_queue = asyncio.Queue(maxsize=10000)
        self._is_running = False
        
        # Boot up the Topology Manager
        self.topology = TopologyManager(project_root)
        self.topology.load()
        
        # Safety check
        if not self.topology.active_sources or not self.topology.active_sinks:
            print("❌ Error: No active sources or sinks found in topology configurations!")
            self._is_running = False

    async def _source_listener(self):
        """Listens to ALL dynamic sources concurrently."""
        for src in self.topology.active_sources:
            await src.connect()
            
        async def pull_from(source):
            async for raw_log in source.read_stream():
                if not self._is_running: break
                await self.ingestion_queue.put(raw_log)
                
        tasks = [pull_from(src) for src in self.topology.active_sources]
        if tasks:
            await asyncio.gather(*tasks)

    async def _sink_writer(self):
        """Writes to ALL dynamic sinks."""
        for sink in self.topology.active_sinks:
            await sink.connect()
            
        while self._is_running:
            data = await self.routing_queue.get()
            
            for sink in self.topology.active_sinks:
                await sink.write(data)
                
            self.routing_queue.task_done()

    async def _orchestrator(self):
        """Pulls from ingestion queue, sends to Process Pool, pushes to routing queue"""
        loop = asyncio.get_running_loop()
        
        with ProcessPoolExecutor(max_workers=self.parse_workers, initializer=_init_worker) as pool:
            print(f"[Engine] Started CPU Pool with {self.parse_workers} workers.")
            
            while self._is_running:
                raw_log = await self.ingestion_queue.get()
                parsed_data = await loop.run_in_executor(pool, wpl_parse_worker, raw_log)
                await self.routing_queue.put(parsed_data)
                self.ingestion_queue.task_done()

    async def run_daemon(self):
        """Boots up the ETL pipeline components."""
        self._is_running = True
        print("🚀 Starting PyWarp Engine...")
        
        tasks = [
            asyncio.create_task(self._source_listener()),
            asyncio.create_task(self._orchestrator()),
            asyncio.create_task(self._sink_writer())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self._is_running = False
            print("\nShutting down engine safely...")
            # Cleanly close all connections
            for src in self.topology.active_sources:
                await src.close()
            for sink in self.topology.active_sinks:
                await sink.close()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    engine = WarpEngine(parse_workers=4)
    try:
        asyncio.run(engine.run_daemon())
    except KeyboardInterrupt:
        pass