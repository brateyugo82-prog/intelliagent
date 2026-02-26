def base_post_id(post_id: str) -> str:
    if not isinstance(post_id, str):
        return ""
    if post_id.endswith("_facebook"):
        return post_id[:-9]
    if post_id.endswith("_linkedin"):
        return post_id[:-9]
    return post_id
