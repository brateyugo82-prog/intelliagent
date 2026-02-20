from .agent import run

class AnalyticsAgent:
    @staticmethod
    def run(*args, **kwargs):
        return run(*args, **kwargs)

__all__ = ["run", "AnalyticsAgent"]