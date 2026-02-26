# Integrationstest: Importe und Workflow
import importlib
import sys

def test_imports():
    import core.main
    import master_agent.master
    import agents.content_agent.agent
    import agents.design_agent.agent
    import agents.publish_agent.agent
    import agents.analytics_agent.agent
    import agents.communication_agent.agent
    print("[OK] All modules imported.")

def test_run_workflow():
    from master_agent import master
    # Simulierter Testlauf (ohne echten OpenAI-Call)
    result = master.run_workflow("mtm", "ping", "website")
    assert isinstance(result, dict)
    for agent in [
        "content_agent", "design_agent", "publish_agent", "analytics_agent", "communication_agent"
    ]:
        assert agent in result
    print("[OK] Workflow run returns all agent keys.")

if __name__ == "__main__":
    test_imports()
    test_run_workflow()
    print("[OK] All integration tests passed.")
