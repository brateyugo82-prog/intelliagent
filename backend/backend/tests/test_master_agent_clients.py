# Hinweis: Absolute Imports (backend.*) für Render + lokale Uvicorn-Kompatibilität
import os
import json
import shutil
import tempfile
from master_agent import master
from dotenv import dotenv_values

def setup_client(tmpdir, env_vars=None, config=None):
    client_dir = os.path.join(tmpdir, 'clients', 'testclient')
    os.makedirs(os.path.join(client_dir, 'output'))
    os.makedirs(os.path.join(client_dir, 'assets'))
    # .env
    env_path = os.path.join(client_dir, '.env')
    with open(env_path, 'w') as f:
        f.write('\n'.join([f"{k}={v}" for k, v in (env_vars or {}).items()]))
    # config.json
    config_path = os.path.join(client_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config or {"foo": "bar"}, f)
    return client_dir

def test_env_loading_and_output(tmp_path, monkeypatch):
    # Setup
    env_vars = {"TEST_KEY": "12345"}
    config = {"foo": "bar"}
    client_dir = setup_client(tmp_path, env_vars, config)
    monkeypatch.chdir(os.path.join(tmp_path, 'clients'))
    # Test
    results = master.run_workflow('testclient')
    # .env geladen?
    loaded = dotenv_values(os.path.join(client_dir, '.env'))
    assert loaded["TEST_KEY"] == "12345"
    # Output geschrieben?
    output_path = os.path.join(client_dir, 'output', 'workflow_result.json')
    assert os.path.exists(output_path)
    with open(output_path) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    # Jeder Agent gibt Dict zurück oder enthält error
    for v in data.values():
        assert isinstance(v, dict)
