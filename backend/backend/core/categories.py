VALID_IMAGE_CATEGORIES = {
    "finished_work",
    "work_action",
    "process_detail",
    "team_vehicle",
    "empty_space",
}

def safe_category(cat: str | None) -> str:
    if not isinstance(cat, str):
        return "finished_work"
    c = cat.strip().lower()
    return c if c in VALID_IMAGE_CATEGORIES else "finished_work"
