import tomllib
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# -------------------------------------------------------------------
# ENGINE CONFIGURATION (Maps to wparse.toml)
# -------------------------------------------------------------------
class PerformanceConfig(BaseModel):
    rate_limit_rps: int = Field(gt=0, description="Max events per second")
    parse_workers: int = Field(gt=0, le=64, description="Number of CPU cores to use")

class ModelsConfig(BaseModel):
    wpl: str = Field(..., description="Path to WPL parsing rules")
    oml: str = Field(..., description="Path to OML transformation rules")

class TopologyConfig(BaseModel):
    sources: str = Field(..., description="Path to source configurations")
    sinks: str = Field(..., description="Path to sink configurations")

class WparseConfig(BaseModel):
    version: str
    robust: str = "normal"
    skip_parse: bool = False
    skip_sink: bool = False
    performance: PerformanceConfig
    models: ModelsConfig
    topology: TopologyConfig

# -------------------------------------------------------------------
# CONNECTOR CONFIGURATION (Maps to source.d / sink.d files)
# -------------------------------------------------------------------
class ConnectorParams(BaseModel):
    # This acts as a flexible catch-all for varied parameters 
    # (e.g., Kafka needs 'brokers', MySQL needs 'endpoint', File needs 'base')
    model_config = {"extra": "allow"}

class ConnectorDef(BaseModel):
    id: str
    type: str
    allow_override: List[str] = []
    params: ConnectorParams

class ConnectorFile(BaseModel):
    connectors: List[ConnectorDef]

# -------------------------------------------------------------------
# CONFIGURATION LOADER
# -------------------------------------------------------------------
def load_toml_config(file_path: str | Path, model_class: Any) -> Any:
    """Reads a TOML file and returns a strictly validated Pydantic object."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file missing: {path}")
        
    with open(path, "rb") as f:
        data = tomllib.load(f)
        
    return model_class.model_validate(data)