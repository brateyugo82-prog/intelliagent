from scheduler.publish_guard import should_auto_publish, is_manual
from core.post_store import mark_manual_required

def handle_platform_publish(post, platform, publish_func):
    if should_auto_publish(platform):
        publish_func(platform, post)
    elif is_manual(platform):
        mark_manual_required(post["id"], platform)
