from .agent import run

class ContentAgent:
    @staticmethod
    def run(*args, **kwargs):
        return run(*args, **kwargs)

__all__ = ["run", "ContentAgent"]