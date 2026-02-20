from agents.lead_agent import run

CLIENT = "mtm_client"

tests = [
    ("Was kostet ein Umzug von Linden nach Laatzen?", "instagram", "comment"),
    ("Habt ihr Samstag noch Zeit?", "instagram", "dm"),
    ("Cooles Bild 👍", "instagram", "comment"),
]

for msg, platform, source in tests:
    result = run(
        message=msg,
        platform=platform,
        source=f"{platform}_{source}",
        client=CLIENT
    )
    print(msg, "→", result)
