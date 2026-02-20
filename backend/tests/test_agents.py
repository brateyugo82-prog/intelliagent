# Hinweis: Absolute Imports (backend.*) für Render + lokale Uvicorn-Kompatibilität
import pytest
import json
from agents.content_agent import agent as content_agent
from agents.design_agent import agent as design_agent
from agents.publish_agent import agent as publish_agent
from agents.analytics_agent import agent as analytics_agent
from agents.communication_agent import agent as communication_agent

def test_content_agent():
    result = content_agent.run(prompt="test", client="test")
    assert isinstance(result, dict)
    # json_str = content_agent.run_json(prompt="test", client="test")
    # assert isinstance(json.loads(json_str), dict)

def test_design_agent():
    result = design_agent.run(prompt="test", client="test")
    assert isinstance(result, dict)
    # json_str = design_agent.run_json(prompt="test", client="test")
    # assert isinstance(json.loads(json_str), dict)

def test_publish_agent():
    result = publish_agent.run(prompt="test", client="test")
    assert isinstance(result, dict)
    # json_str = publish_agent.run_json(prompt="test", client="test")
    # assert isinstance(json.loads(json_str), dict)

def test_analytics_agent():
    result = analytics_agent.run(prompt="test", client="test")
    assert isinstance(result, dict)
    # json_str = analytics_agent.run_json(prompt="test", client="test")
    # assert isinstance(json.loads(json_str), dict)

def test_communication_agent():
    result = communication_agent.run(prompt="test", client="test")
    assert isinstance(result, dict)
    # json_str = communication_agent.run_json(prompt="test", client="test")
    # assert isinstance(json.loads(json_str), dict)
