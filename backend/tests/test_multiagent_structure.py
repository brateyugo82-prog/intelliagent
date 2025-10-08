# Hinweis: Absolute Imports (backend.*) für Render + lokale Uvicorn-Kompatibilität
import importlib
import pkgutil
import os
import json
from backend.master_agent import master

def test_all_agents_return_dict():
    agents_path = os.path.join(os.path.dirname(__file__), '../agents')
    agent_modules = [name for _, name, _ in pkgutil.iter_modules([agents_path])]
    dummy_config = {'client': 'example_client'}
    for agent_name in agent_modules:
        module_path = f"backend.agents.{agent_name}"
        agent_module = importlib.import_module(module_path)
        result = agent_module.run(prompt="test", client="example_client")
        assert isinstance(result, dict)
        # Optional: JSON
        if hasattr(agent_module, 'run_json'):
            json_str = agent_module.run_json(prompt="test", client="example_client")
            assert isinstance(json.loads(json_str), dict)

def test_master_agent_collects_all():
    dummy_config = {'client': 'example_client'}
    results = master.run_workflow(dummy_config)
    assert isinstance(results, dict)
    # Es sollten alle Agenten als Key enthalten sein
    agents_path = os.path.join(os.path.dirname(__file__), '../agents')
    agent_modules = [name for _, name, _ in pkgutil.iter_modules([agents_path])]
    for agent_name in agent_modules:
        assert agent_name in results
