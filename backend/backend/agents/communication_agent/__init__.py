from .agent import run

class CommunicationAgent:
    @staticmethod
    def run(*args, **kwargs):
        return run(*args, **kwargs)

__all__ = ["run", "CommunicationAgent"]