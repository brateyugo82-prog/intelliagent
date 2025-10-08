import os
import tempfile
import shutil
from dotenv import load_dotenv, dotenv_values
import pytest

def test_client_env_loading():
    # Setup: Temporäres Client-Verzeichnis mit .env
    temp_dir = tempfile.mkdtemp()
    env_path = os.path.join(temp_dir, '.env')
    with open(env_path, 'w') as f:
        f.write('TEST_KEY=12345\n')
    # Laden
    load_dotenv(env_path, override=True)
    assert os.environ.get('TEST_KEY') == '12345'
    # Cleanup
    shutil.rmtree(temp_dir)


def test_client_assets_access():
    # Setup: Temporäres Client-Verzeichnis mit assets
    temp_dir = tempfile.mkdtemp()
    assets_dir = os.path.join(temp_dir, 'assets')
    os.makedirs(assets_dir)
    label_path = os.path.join(assets_dir, 'label.txt')
    with open(label_path, 'w') as f:
        f.write('TestLabel')
    # Zugriff simulieren
    assert os.path.exists(label_path)
    with open(label_path) as f:
        content = f.read()
    assert content == 'TestLabel'
    # Cleanup
    shutil.rmtree(temp_dir)
