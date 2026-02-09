from src.utils.endpoints import Endpoints
from config import ZONE_ID



def test_pfs_001_parallel_file_system_list_success(api_client):
    res = api_client.get(Endpoints.PARALLEL_FILE_SYSTEM)
    assert res.status_code == 200, (
        "⛔test_pfs_001_parallel_file_system_list_success - 병렬파일시스템 목록 조회 실패")

    data = res.json()
    assert isinstance(data, list)

    if not data:
        assert data == []
        return

    required_keys = {"id", "name", "status"}
    for item in data:
        assert isinstance(item, dict)
        assert required_keys.issubset(item.keys()), (
            "⛔test_pfs_001_parallel_file_system_list_success - 필수 키 누락")


def test_pfs_002_parallel_file_system_create_fail_quota_exceeded(api_client):
    payload = {
        "name": "pfs-test",
        "zone_id": ZONE_ID,
        "size_gib": 1000,
    }

    res = api_client.post(
        Endpoints.PARALLEL_FILE_SYSTEM,
        json=payload,
    )

    assert res.status_code == 409, (
        "⛔test_pfs_002_parallel_file_system_create_fail_quota_exceeded"
        "- 병렬파일시스템 생성 시도시 쿼터 초과 에러 미발생")

    data = res.json()
    assert data["code"] == "resource_quota_exceed", \
        "⛔test_pfs_002_parallel_file_system_create_fail_quota_exceeded - 잘못된 에러 코드"
    assert "message" in data

    detail = data.get("detail")
    assert isinstance(detail, dict)

    assert detail["resource"] == "parallel_file_system_count"
    assert isinstance(detail["limit"], int)
    assert isinstance(detail["used"], int)
