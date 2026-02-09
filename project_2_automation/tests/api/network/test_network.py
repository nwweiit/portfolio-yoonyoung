from src.utils.endpoints import Endpoints
import uuid
from tests.api.network.helpers import NetworkResources, safe_delete, wait_until_resource_deleted
from config import ZONE_ID

def test_nt_001_network_interface_list_success(api_client):
    response = api_client.get(Endpoints.NETWORK_INTERFACE)
    assert response.status_code == 200, (
    "⛔test_nt_001_network_interface_list_success - 네트워크 인터페이스 목록 조회 실패")

    data = response.json()

    assert isinstance(data, list), "⛔test_nt_001_network_interface_list_success - 응답 타입 오류"

    if not data:
        assert data == []
        return

    required_keys = {"id", "name", "status"}

    for item in data:
        assert required_keys.issubset(item.keys()), \
            "⛔test_nt_001_network_interface_list_success - 필수 필드 누락"
        assert isinstance(item["status"], str)


def test_nt_002_network_interface_list_without_token(unauthenticated_api_client):
    response = unauthenticated_api_client.get(Endpoints.NETWORK_INTERFACE)
    assert response.status_code == 401, \
        "⛔test_nt_002_network_interface_list_without_token - 인증 없이도 목록 조회 가능"

    data = response.json()
    assert isinstance(data, dict), \
        "⛔test_nt_002_network_interface_list_without_token - 에러 응답 타입 오류"

    assert any(key in data for key in ("message", "error", "detail")), \
        "⛔test_nt_002_network_interface_list_without_token - 에러 메시지 필드 오류"


def test_nt_003_network_interface_list_with_invalid_token(invalid_token_api_client):
    response = invalid_token_api_client.get(Endpoints.NETWORK_INTERFACE)

    assert response.status_code in (401, 403), \
        "⛔test_nt_003_network_interface_list_with_invalid_token - 유효하지 않은 토큰 오류 미반환"

    data = response.json()
    assert isinstance(data, dict), \
        "⛔test_nt_003_network_interface_list_with_invalid_token - 에러 응답 타입 오류"
    assert any(key in data for key in ("detail", "message", "error")), \
        "⛔test_nt_003_network_interface_list_with_invalid_token - 에러 메시지 필드 오류"


def test_nt_004_network_interface_get_by_id(api_client, nic_stack):
    nic_id = nic_stack["nic_id"]

    response = api_client.get(f"{Endpoints.NETWORK_INTERFACE}/{nic_id}")
    assert response.status_code == 200, \
        "⛔test_nt_004_network_interface_get_by_id - 네트워크 인터페이스 단일 조회 실패"

    data = response.json()
    assert isinstance(data, dict)
    assert isinstance(data.get("id"), str)
    assert data.get("id") == nic_id, \
        "⛔test_nt_004_network_interface_get_by_id - 조회된 ID 불일치"
    assert "status" in data
    assert isinstance(data["status"], str), \
        "⛔test_nt_004_network_interface_get_by_id - status 타입 오류"


def test_nt_005_network_interface_get_by_id_not_found(api_client):
    random_id = str(uuid.uuid4())

    response = api_client.get(f"{Endpoints.NETWORK_INTERFACE}/{random_id}")

    assert response.status_code in (404, 409), \
        "⛔test_nt_005_network_interface_get_by_id_not_found - \
            존재하지 않는 네트워크 인터페이스 조회 시 오류 미반환"


def test_nt_006_network_interface_create_success(api_client,subnet_stack_no_nic):
    payload = {
        "name": "nic-test-team03",
        "attached_subnet_id": subnet_stack_no_nic["subnet_id"],
        "dr": False,
        "zone_id": ZONE_ID,
    }

    nic_id = None

    try:
        response = api_client.post(
            Endpoints.NETWORK_INTERFACE,
            json=payload,
        )
        assert response.status_code == 200, \
            "⛔test_nt_006_network_interface_create_success - 네트워크 인터페이스 생성 실패"

        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], str)

        nic_id = data["id"]
        get_res = api_client.get(
            f"{Endpoints.NETWORK_INTERFACE}/{nic_id}"
        )
        assert get_res.status_code == 200, \
            "⛔test_nt_006_network_interface_create_success - 생성된 네트워크 인터페이스 조회 실패"

        get_data = get_res.json()
        assert get_data["attached_subnet_id"] == payload["attached_subnet_id"], \
            "⛔test_nt_006_network_interface_create_success - \
                생성된 네트워크 인터페이스의 서브넷 ID 불일치"

    finally:
        safe_delete(
            api_client,
            Endpoints.NETWORK_INTERFACE,
            nic_id,
        )


def test_nt_007_network_interface_duplicate_name_allowed(duplicate_nic_creator):
    id1 = duplicate_nic_creator("nic-duplicate-test")
    id2 = duplicate_nic_creator("nic-duplicate-test")

    assert id1 != id2, \
        "⛔test_nt_007_network_interface_duplicate_name_allowed - 중복 이름 허용되지 않음"


def test_nt_008_network_interface_update_success(api_client, nic_stack):
    nic_id = nic_stack["nic_id"]

    payload = {
        "name": "nic-updated-name-team03"
    }

    patch_res = api_client.patch(
        f"{Endpoints.NETWORK_INTERFACE}/{nic_id}",
        json=payload,
    )
    assert patch_res.status_code == 200, \
        "⛔test_nt_008_network_interface_update_success - 네트워크 인터페이스 업데이트 실패"

    patch_data = patch_res.json()
    assert patch_data.get("id") == nic_id, \
        "⛔test_nt_008_network_interface_update_success - 수정된 ID 불일치"

    get_res = api_client.get(
        f"{Endpoints.NETWORK_INTERFACE}/{nic_id}"
    )
    assert get_res.status_code == 200

    data = get_res.json()
    assert data["id"] == nic_id
    assert data["name"] == payload["name"], \
        "⛔test_nt_008_network_interface_update_success - 수정 내용 반영 실패"


def test_nt_009_network_interface_delete_success(api_client,subnet_stack_no_nic):
    subnet_id = subnet_stack_no_nic["subnet_id"]

    nic_id = NetworkResources.create_network_interface(api_client,subnet_id)


    delete_res = api_client.delete(f"{Endpoints.NETWORK_INTERFACE}/{nic_id}")
    assert delete_res.status_code == 200, \
        "⛔test_nt_009_network_interface_delete_success - 네트워크 인터페이스 삭제 실패"

    delete_data = delete_res.json()
    assert delete_data["id"] == nic_id, \
        "⛔test_nt_009_network_interface_delete_success - 삭제된 ID 불일치"
    assert delete_data["status"] == "deleted", \
        "⛔test_nt_009_network_interface_delete_success - 삭제 상태값 오류"

    wait_until_resource_deleted(api_client,Endpoints.NETWORK_INTERFACE,nic_id)


def test_nt_010_subnet_list_success(api_client):
    response = api_client.get(Endpoints.SUBNET)
    assert response.status_code == 200, \
        "⛔test_nt_010_subnet_list_success - 서브넷 목록 조회 실패"

    data = response.json()
    assert isinstance(data, list), \
        "⛔test_nt_010_subnet_list_success - 응답 타입 오류"

    if not data:
        assert data == []
        return

    required_keys = {
        "id",
        "name",
        "attached_network_id",
        "purpose",
        "network_gw",
        "status",
    }

    for item in data:
        assert isinstance(item, dict)
        assert required_keys.issubset(item.keys()), \
            "⛔test_nt_010_subnet_list_success - 필수 필드 누락"
        assert isinstance(item["id"], str)
        assert isinstance(item["name"], str)
        assert isinstance(item["attached_network_id"], str)
        assert isinstance(item["purpose"], str)
        assert isinstance(item["network_gw"], str)
        assert isinstance(item["status"], str)


def test_nt_011_subnet_get_by_id(api_client, subnet_stack):
    subnet_id = subnet_stack["subnet_id"]
    vnet_id = subnet_stack["vnet_id"]

    response = api_client.get(f"{Endpoints.SUBNET}/{subnet_id}")
    assert response.status_code == 200, "⛔test_nt_011_subnet_get_by_id - 서브넷 단일 조회 실패"

    data = response.json()
    assert isinstance(data, dict)

    required_keys = {
        "id",
        "name",
        "status",
        "attached_network_id",
        "network_gw",
    }
    assert required_keys.issubset(data.keys()), "⛔test_nt_011_subnet_get_by_id - 필수 필드 누락"

    assert data["id"] == subnet_id, "⛔test_nt_011_subnet_get_by_id - 조회된 서브넷 ID 불일치"
    assert data["attached_network_id"] == vnet_id, \
        "⛔test_nt_011_subnet_get_by_id - 연결된 가상네트워크 ID 불일치"
    assert isinstance(data["status"], str)


def test_nt_012_subnet_create_success(api_client,vnet_id):
    payload = {
        "name": "subnet-test-team03",
        "attached_network_id": vnet_id,
        "purpose": "virtual_machine",
        "network_gw": "192.168.10.1/24",
        "zone_id": ZONE_ID,
    }

    subnet_id = None

    try:
        response = api_client.post(
            Endpoints.SUBNET,
            json=payload,
        )
        assert response.status_code == 200, "⛔test_nt_012_subnet_create_success - 서브넷 생성 실패"

        create_data = response.json()
        assert "id" in create_data
        subnet_id = create_data["id"]

        get_res = api_client.get(
            f"{Endpoints.SUBNET}/{subnet_id}"
        )
        assert get_res.status_code == 200, \
            "⛔test_nt_012_subnet_create_success - 생성된 서브넷 조회 실패"

        data = get_res.json()
        assert data["name"] == payload["name"], \
            "⛔test_nt_012_subnet_create_success - 서브넷 이름 불일치"
        assert data["attached_network_id"] == payload["attached_network_id"], \
            "⛔test_nt_012_subnet_create_success - 연결된 가상네트워크 ID 불일치"
        assert data["network_gw"] == payload["network_gw"], \
            "⛔test_nt_012_subnet_create_success - 네트워크 게이트웨이 불일치"

    finally:
        safe_delete(api_client,Endpoints.SUBNET,subnet_id)


def test_nt_013_subnet_create_fail_when_vnet_conflict(api_client, vnet_id):
    payload = {
        "name": "subnet-1",
        "zone_id": ZONE_ID,
        "attached_network_id": vnet_id,
        "purpose": "virtual_machine",
        "network_gw": "192.168.10.1/24",
    }

    res1 = api_client.post(Endpoints.SUBNET, json=payload)
    assert res1.status_code == 200
    subnet_id = res1.json()["id"]

    try:
        res2 = api_client.post(
            Endpoints.SUBNET,
            json={**payload, "name": "subnet-2"},
        )
        assert res2.status_code == 409, \
            "⛔test_nt_013_subnet_create_fail_when_vnet_conflict - 가상네트워크 충돌 오류 미반환"

        data = res2.json()
        assert data["code"] == "conflict_network_gw", \
            "⛔test_nt_013_subnet_create_fail_when_vnet_conflict - 충돌 오류 코드 불일치"
        assert "detail" in data
        assert "resource_subnet" in data["detail"]

    finally:
        safe_delete(api_client, Endpoints.SUBNET, subnet_id)


def test_nt_014_subnet_update_success(api_client, subnet_stack):
    subnet_id = subnet_stack["subnet_id"]

    payload = {
        "name": "subnet-updated-name-team03"
    }

    patch_res = api_client.patch(
        f"{Endpoints.SUBNET}/{subnet_id}",
        json=payload,
    )
    assert patch_res.status_code == 200, "⛔test_nt_014_subnet_update_success - 서브넷 수정 실패"

    patch_data = patch_res.json()
    assert patch_data.get("id") == subnet_id, \
        "⛔test_nt_014_subnet_update_success - 수정된 ID 불일치"

    get_res = api_client.get(
        f"{Endpoints.SUBNET}/{subnet_id}"
    )
    assert get_res.status_code == 200

    data = get_res.json()
    assert data["id"] == subnet_id
    assert data["name"] == payload["name"]


def test_nt_015_subnet_delete_success(api_client, vnet_id):
    subnet_id = NetworkResources.create_subnet(api_client, vnet_id)

    delete_res = api_client.delete(f"{Endpoints.SUBNET}/{subnet_id}")
    assert delete_res.status_code == 200, "⛔test_nt_015_subnet_delete_success - 서브넷 삭제 실패"

    delete_data = delete_res.json()
    assert delete_data["id"] == subnet_id
    assert delete_data["status"] == "deleted", \
        "⛔test_nt_015_subnet_delete_success - 삭제 상태값 오류"

    wait_until_resource_deleted(api_client,Endpoints.SUBNET,subnet_id)


def test_nt_016_vnet_list_success(api_client):
    response = api_client.get(Endpoints.VIRTUAL_NETWORK)
    assert response.status_code == 200, \
        "⛔test_nt_016_vnet_list_success - 가상 네트워크 목록 조회 실패"

    data = response.json()
    assert isinstance(data, list), "⛔test_nt_016_vnet_list_success - 응답 타입 오류"

    if not data:
        assert data == []
        return

    required_keys = {
        "id",
        "name",
        "status",
    }

    for item in data:
        assert isinstance(item, dict)
        assert required_keys.issubset(item.keys()), \
            "⛔test_nt_016_vnet_list_success - 필수 필드 누락"
        assert isinstance(item["id"], str)
        assert isinstance(item["name"], str)
        assert isinstance(item["status"], str)


def test_nt_017_vnet_get_by_id(api_client, vnet_id):
    response = api_client.get(f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}")
    assert response.status_code == 200, \
        "⛔test_nt_017_vnet_get_by_id - 가상 네트워크 단일 조회 실패"

    data = response.json()
    assert isinstance(data, dict), "⛔test_nt_017_vnet_get_by_id - 응답 타입 오류"

    required_keys = {
        "id",
        "name",
        "status",
    }
    assert required_keys.issubset(data.keys()), "⛔test_nt_017_vnet_get_by_id - 필수 필드 누락"

    assert data["id"] == vnet_id
    assert isinstance(data["name"], str)
    assert isinstance(data["status"], str)


def test_nt_018_vnet_create_success(api_client):
    payload = {
        "name": "vnet-test-team03",
        "zone_id": ZONE_ID,
        "network_cidr": "192.168.0.0/16",
    }

    vnet_id = None

    try:
        response = api_client.post(Endpoints.VIRTUAL_NETWORK,json=payload)
        assert response.status_code == 200, \
            "⛔test_nt_018_vnet_create_success - 가상 네트워크 생성 실패"

        create_data = response.json()
        assert "id" in create_data
        vnet_id = create_data["id"]

        get_res = api_client.get(f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}")
        assert get_res.status_code == 200, \
            "⛔test_nt_018_vnet_create_success - 생성된 가상 네트워크 조회 실패"

        data = get_res.json()
        assert data["name"] == payload["name"], \
            "⛔test_nt_018_vnet_create_success - 가상 네트워크 이름 불일치"
        assert data["network_cidr"] == payload["network_cidr"]
        assert data["status"] in ("available", "active", "idle"), \
            "⛔test_nt_018_vnet_create_success - 생성된 가상 네트워크 상태값 오류"

    finally:
        safe_delete(api_client,Endpoints.VIRTUAL_NETWORK,vnet_id)


def test_nt_019_vnet_update_success(api_client, vnet_id):
    payload = {
        "name": "vnet-updated-name-team03"
    }

    patch_res = api_client.patch(
        f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}",
        json=payload,
    )
    assert patch_res.status_code == 200, \
        "⛔test_nt_019_vnet_update_success - 가상 네트워크 수정 실패"

    patch_data = patch_res.json()
    assert patch_data.get("id") == vnet_id

    get_res = api_client.get(f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}")
    assert get_res.status_code == 200, \
        "⛔test_nt_019_vnet_update_success - 수정된 가상 네트워크 조회 실패"

    data = get_res.json()
    assert data["id"] == vnet_id, "⛔test_nt_019_vnet_update_success - 조회된 ID 불일치"
    assert data["name"] == payload["name"]
    assert data["status"] in ("available", "active", "idle"), \
        "⛔test_nt_019_vnet_update_success - 가상 네트워크 상태값 오류"


def test_nt_020_vnet_delete_success(api_client):
    payload = {
        "name": "vnet-delete-test-team03",
        "zone_id": ZONE_ID,
        "network_cidr": "192.168.0.0/16",
    }

    create_res = api_client.post(Endpoints.VIRTUAL_NETWORK,json=payload,)
    assert create_res.status_code == 200, \
        "⛔test_nt_020_vnet_delete_success - 가상 네트워크 생성 실패"

    vnet_id = create_res.json()["id"]

    delete_res = api_client.delete(
        f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}"
    )
    assert delete_res.status_code == 200, \
        "⛔test_nt_020_vnet_delete_success - 가상 네트워크 삭제 실패"

    delete_data = delete_res.json()
    assert delete_data["id"] == vnet_id
    assert delete_data["status"] == "deleted", \
        "⛔test_nt_020_vnet_delete_success - 삭제 상태값 오류"

    wait_until_resource_deleted(api_client,Endpoints.VIRTUAL_NETWORK,vnet_id)


def test_nt_021_vnet_delete_fail_when_subnet_exists(api_client, subnet_stack):
    vnet_id = subnet_stack["vnet_id"]

    res = api_client.delete(
        f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}"
    )

    assert res.status_code == 409, \
        "⛔test_nt_021_vnet_delete_fail_when_subnet_exists - \
            서브넷 존재 시 가상 네트워크 삭제 오류 미반환"

    data = res.json()
    assert data["code"] == "subnet_found"

    assert "detail" in data
    assert "resource_subnet" in data["detail"]



def test_nt_022_public_ip_list_success(api_client):
    response = api_client.get(Endpoints.PUBLIC_IP)
    assert response.status_code == 200, \
        "⛔test_nt_022_public_ip_list_success - 공인 IP 목록 조회 실패"

    data = response.json()
    assert isinstance(data, list), "⛔test_nt_022_public_ip_list_success - 응답 타입 오류"

    if not data:
        return

    required_keys = {
        "id",
        "ip",
        "status",
        "attached_network_interface_id",
    }

    assert required_keys.issubset(data[0].keys()), \
        "⛔test_nt_022_public_ip_list_success - 필수 필드 누락"
    
        
def test_nt_023_public_ip_get_by_id(api_client, public_ip_stack):
    public_ip_id = public_ip_stack["public_ip_id"]

    response = api_client.get(f"{Endpoints.PUBLIC_IP}/{public_ip_id}")
    assert response.status_code == 200, "⛔test_nt_023_public_ip_get_by_id - 공인 IP 단일 조회 실패"

    data = response.json()
    assert isinstance(data, dict), "⛔test_nt_023_public_ip_get_by_id - 응답 타입 오류"

    required_keys = {
        "id",
        "ip",
        "status",
        "attached_network_interface_id",
    }
    assert required_keys.issubset(data.keys()), "⛔test_nt_023_public_ip_get_by_id - 필수 필드 누락"

    assert data["id"] == public_ip_id
    assert isinstance(data["ip"], str)
    assert isinstance(data["status"], str)
    attached_id = data["attached_network_interface_id"]
    assert attached_id is None or isinstance(attached_id, str)



def test_nt_024_public_ip_create_success(api_client):
    payload = {
        "zone_id": ZONE_ID,
        "ddos": True,
        "dr": False,
        "tags": {},
    }

    public_ip_id = None

    try:
        response = api_client.post(
            Endpoints.PUBLIC_IP,
            json=payload,
        )
        assert response.status_code == 200, \
            "⛔test_nt_024_public_ip_create_success - 공인 IP 생성 실패"

        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], str)

        public_ip_id = data["id"]

        get_res = api_client.get(
            f"{Endpoints.PUBLIC_IP}/{public_ip_id}"
        )
        assert get_res.status_code == 200, \
            "⛔test_nt_024_public_ip_create_success - 생성된 공인 IP 조회 실패"

        get_data = get_res.json()
        assert get_data["id"] == public_ip_id
        assert isinstance(get_data["ip"], str)
        assert get_data["status"] in ("active", "available", "idle")

        attached_id = get_data.get("attached_network_interface_id")
        assert attached_id is None or isinstance(attached_id, str), \
            "⛔test_nt_024_public_ip_create_success - 연결된 네트워크 인터페이스 타입 오류"

    finally:
        safe_delete(api_client,Endpoints.PUBLIC_IP,public_ip_id)


def test_nt_025_public_ip_update_attach_and_detach_success(api_client,public_ip_stack):
    public_ip_id = public_ip_stack["public_ip_id"]
    nic_id = public_ip_stack["nic_id"]


    attach_res = api_client.patch(
        f"{Endpoints.PUBLIC_IP}/{public_ip_id}",
        json={"attached_network_interface_id": nic_id},
    )
    assert attach_res.status_code == 200,  \
        "⛔test_nt_025_public_ip_update_attach_and_detach_success - 공인 IP 연결 실패"
    assert attach_res.json()["id"] == public_ip_id

    get_res = api_client.get(f"{Endpoints.PUBLIC_IP}/{public_ip_id}")
    assert get_res.status_code == 200, \
        "⛔test_nt_025_public_ip_update_attach_and_detach_success - 공인 IP 조회 실패"

    data = get_res.json()
    assert data["attached_network_interface_id"] == nic_id


    detach_res = api_client.patch(
        f"{Endpoints.PUBLIC_IP}/{public_ip_id}",
        json={"attached_network_interface_id": None},
    )
    assert detach_res.status_code == 200,  \
        "⛔test_nt_025_public_ip_update_attach_and_detach_success - 공인 IP 연결 해제 실패"
    assert detach_res.json()["id"] == public_ip_id


    get_res = api_client.get(f"{Endpoints.PUBLIC_IP}/{public_ip_id}")
    assert get_res.status_code == 200, \
        "⛔test_nt_025_public_ip_update_attach_and_detach_success - 공인 IP 조회 실패"

    data = get_res.json()
    assert data["attached_network_interface_id"] is None, \
        "⛔test_nt_025_public_ip_update_attach_and_detach_success - 공인 IP 연결 해제 반영 실패"


def test_nt_026_public_ip_delete_success(api_client):
    payload = {
        "zone_id": ZONE_ID,
        "ddos": True,
        "dr": False,
        "tags": {},
    }

    create_res = api_client.post(Endpoints.PUBLIC_IP, json=payload)
    assert create_res.status_code == 200, \
        "⛔test_nt_026_public_ip_delete_success - 공인 IP 생성 실패"

    public_ip_id = create_res.json()["id"]

    delete_res = api_client.delete(f"{Endpoints.PUBLIC_IP}/{public_ip_id}")
    assert delete_res.status_code == 200, \
        "⛔test_nt_026_public_ip_delete_success - 공인 IP 삭제 실패"

    delete_data = delete_res.json()
    assert delete_data["id"] == public_ip_id
    assert delete_data["status"] == "deleted", \
        "⛔test_nt_026_public_ip_delete_success - 삭제 상태값 오류"

    wait_until_resource_deleted(api_client, Endpoints.PUBLIC_IP, public_ip_id)
