import yaml
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

def get_config():
    with open(PROJECT_ROOT / "config" / "config.yaml", 'r') as f:
        return yaml.safe_load(f)

def get_synonyms():
    with open(PROJECT_ROOT / "config" / "synonyms.json", 'r') as f:
        return json.load(f)