import random
import uuid 
from config import ZONE_ID
from src.utils.endpoints import Endpoints





def wait_until_resource_deleted(api_client, endpoint, resource_id, max_attempts=10):
    last_response = None

    for _ in range(max_attempts):
        res = api_client.get(f"{endpoint}/{resource_id}")
        last_response = res

        if res.status_code == 404:
            return

        if res.status_code == 200:
            status = res.json().get("status")
            if status == "deleted":
                return

    raise AssertionError(
        f"[Delete not completed]\n"
        f"endpoint={endpoint}\n"
        f"resource_id={resource_id}\n"
        f"attempts={max_attempts}\n"
        f"last_status_code={last_response.status_code}\n"
        f"last_body={last_response.text}"
    )


def safe_delete(api_client, endpoint, resource_id):
    if not resource_id:
        return

    delete_res = api_client.delete(f"{endpoint}/{resource_id}")

    if delete_res.status_code == 404:
        return  
    if delete_res.status_code not in (200, 204):
        raise AssertionError(
            f"[Delete request failed]\n"
            f"endpoint={endpoint}\n"
            f"resource_id={resource_id}\n"
            f"status={delete_res.status_code}\n"
            f"body={delete_res.text}"
        )

    wait_until_resource_deleted(api_client, endpoint, resource_id)


class NetworkResources:
    @staticmethod
    def create_subnet(api_client, vnet_id):
        resp = api_client.post(
            Endpoints.SUBNET,
            json={
                "name": f"subnet-{uuid.uuid4().hex[:6]}-team03",
                "attached_network_id": vnet_id,
                "network_gw": f"192.168.{random.randint(10, 250)}.1/24",
                "purpose": "virtual_machine",
                "zone_id": ZONE_ID,
            },
        )
        assert resp.status_code == 200, resp.text
        return resp.json()["id"]


    @staticmethod
    def delete_subnet(api_client, subnet_id):
        resp = api_client.delete(f"{Endpoints.SUBNET}/{subnet_id}")
        assert resp.status_code in (200, 204), resp.text


    @staticmethod
    def create_network_interface(api_client, subnet_id):
        resp = api_client.post(
            Endpoints.NETWORK_INTERFACE,
            json={
                "name": f"nic-{uuid.uuid4().hex[:6]}-team03",
                "attached_subnet_id": subnet_id,
                "dr": False,
                "zone_id": ZONE_ID,
            },
        )
        assert resp.status_code == 200, resp.text
        return resp.json()["id"]


    @staticmethod
    def delete_network_interface(api_client, nic_id):
        resp = api_client.delete(f"{Endpoints.NETWORK_INTERFACE}/{nic_id}")
        assert resp.status_code in (200, 204), resp.text


    @staticmethod
    def create_public_ip(api_client, nic_id):
        resp = api_client.post(
            Endpoints.PUBLIC_IP,
            json={
                "zone_id": ZONE_ID,
                "dr": False,
                "ddos": True,
                "tags": {},
            },
        )
        assert resp.status_code == 200, resp.text
        return resp.json()["id"]


    @staticmethod
    def delete_public_ip(api_client, public_ip_id):
        resp = api_client.delete(f"{Endpoints.PUBLIC_IP}/{public_ip_id}")
        assert resp.status_code in (200, 204), resp.text
