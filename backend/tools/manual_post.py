import sys
from api.publisher import publish_single_post

if __name__ == "__main__":
    post_id = sys.argv[1]
    platform = sys.argv[2]

    res = publish_single_post(
        client="mtm_client",
        post_id=post_id,
        platform=platform,
        manual=True,
    )

    print("✅ MANUAL POST:", res)
