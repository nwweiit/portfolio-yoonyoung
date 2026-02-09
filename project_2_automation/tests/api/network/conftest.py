import pytest
import uuid
from src.utils.api_client import APIClient
from src.utils.endpoints import Endpoints
from config import ZONE_ID
from tests.api.network.helpers import NetworkResources


##아예 토큰 없는 클라이언트

@pytest.fixture
def unauthenticated_api_client():
    return APIClient(access_token=None)   


##무작위 토큰 사용

@pytest.fixture
def invalid_token_api_client():
    return APIClient(access_token="invalid.random.token")


##가상 네트워크 생성 및 삭제

@pytest.fixture
def vnet_id(api_client):
    payload = {
        "name": f"vnet-{uuid.uuid4().hex[:6]}-team03",
        "network_cidr": "192.168.0.0/16",
        "zone_id": ZONE_ID,
    }

    res = api_client.post(Endpoints.VIRTUAL_NETWORK, json=payload)
    assert res.status_code == 200, res.text

    vnet_id = res.json()["id"]
    yield vnet_id

    res = api_client.delete(f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}")
    assert res.status_code in (200, 204), (
        f"VNet delete failed. vnet_id={vnet_id}, "
        f"status={res.status_code}, body={res.text}"
    )


##서브넷 스택 생성 및 삭제

@pytest.fixture
def subnet_stack(api_client, vnet_id):
    subnet_id = None
    try:
        subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
        yield {
            "vnet_id": vnet_id,
            "subnet_id": subnet_id,
        }
    finally:
        if subnet_id:
            res = api_client.delete(f"{Endpoints.SUBNET}/{subnet_id}")
            assert res.status_code in (200, 204), (
                f"Subnet delete failed. subnet_id={subnet_id}, "
                f"status={res.status_code}, body={res.text}"
            )


##네트워크 인터페이스용 서브넷 스택 생성 및 삭제

@pytest.fixture
def subnet_stack_no_nic(api_client, vnet_id):
    subnet_id = None
    try:
        subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
        yield {
            "vnet_id": vnet_id,
            "subnet_id": subnet_id,
        }
    finally:
        if subnet_id:
            res = api_client.delete(f"{Endpoints.SUBNET}/{subnet_id}")

            assert res.status_code in (200, 204), (
                f"[Subnet teardown failed]\n"
                f"subnet_id={subnet_id}\n"
                f"status={res.status_code}\n"
                f"body={res.text}\n"
                f"Hint: A network interface may still be attached."
            )


##네트워크 인터페이스 스택 생성 및 삭제

@pytest.fixture
def nic_stack(api_client, vnet_id):
    subnet_id = None
    nic_id = None
    try:
        subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
        nic_id = NetworkResources.create_network_interface(api_client, subnet_id)
        yield {
            "vnet_id": vnet_id,
            "subnet_id": subnet_id,
            "nic_id": nic_id,
        }
    finally:
        if nic_id:
            NetworkResources.delete_network_interface(api_client, nic_id)
        if subnet_id:
            NetworkResources.delete_subnet(api_client, subnet_id)


##공인 ip용 네트워크 인터페이스 스택 생성 및 삭제

@pytest.fixture
def nic_stack_no_public_ip(api_client, vnet_id):
    subnet_id = None
    nic_id = None
    try:
        subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
        nic_id = NetworkResources.create_network_interface(api_client, subnet_id)

        yield {
            "vnet_id": vnet_id,
            "subnet_id": subnet_id,
            "nic_id": nic_id,
        }

    finally:
        if nic_id:
            res = api_client.delete(f"{Endpoints.NETWORK_INTERFACE}/{nic_id}")

            assert res.status_code in (200, 204), (
                f"[NIC teardown failed]\n"
                f"nic_id={nic_id}\n"
                f"status={res.status_code}\n"
                f"body={res.text}\n"
                f"Hint: A public IP may still be attached."
            )

        if subnet_id:
            NetworkResources.delete_subnet(api_client, subnet_id)


##공인 ip 스택 생성 및 삭제

@pytest.fixture
def public_ip_stack(api_client, vnet_id):
    subnet_id = None
    nic_id = None
    public_ip_id = None
    try:
        subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
        nic_id = NetworkResources.create_network_interface(api_client, subnet_id)
        public_ip_id = NetworkResources.create_public_ip(api_client, nic_id)
        yield {
            "vnet_id": vnet_id,
            "subnet_id": subnet_id,
            "nic_id": nic_id,
            "public_ip_id": public_ip_id,
        }
    finally:
        if public_ip_id:
            NetworkResources.delete_public_ip(api_client, public_ip_id)
        if nic_id:
            NetworkResources.delete_network_interface(api_client, nic_id)
        if subnet_id:
            NetworkResources.delete_subnet(api_client, subnet_id)


##중복 이름 네트워크 인터페이스 생성 및 삭제

@pytest.fixture
def duplicate_nic_creator(api_client, vnet_id):
    created_nics = []
    created_subnets = []

    def _create(name: str) -> str:

        subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
        created_subnets.append(subnet_id)

        res = api_client.post(
            Endpoints.NETWORK_INTERFACE,
            json={
                "name": name,
                "attached_subnet_id": subnet_id,
                "dr": False,
                "zone_id": ZONE_ID,
            },
        )
        assert res.status_code == 200, res.text

        nic_id = res.json()["id"]
        created_nics.append(nic_id)
        return nic_id

    yield _create

    for nic_id in created_nics:
        NetworkResources.delete_network_interface(api_client, nic_id)
    for subnet_id in created_subnets:
        NetworkResources.delete_subnet(api_client, subnet_id)
