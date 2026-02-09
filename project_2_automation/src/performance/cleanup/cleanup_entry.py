
import os
from src.utils.api_client import APIClient
from cleanup import cleanup_all_resources


def main():
    token = os.getenv("ECI_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("ECI_ACCESS_TOKEN 없음")

    build_id = os.getenv("BUILD_ID")
    if not build_id:
        raise RuntimeError("BUILD_ID 없음")

    api_client = APIClient(token)
    cleanup_all_resources(api_client, build_id)


if __name__ == "__main__":
    main()
