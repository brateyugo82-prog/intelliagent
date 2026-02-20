from .agent import run

class PublishAgent:
    @staticmethod
    def run(*args, **kwargs):
        return run(*args, **kwargs)

__all__ = ["run", "PublishAgent"]