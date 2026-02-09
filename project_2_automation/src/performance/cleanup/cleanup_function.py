from src.utils.endpoints import Endpoints

##동적 리소스 정리를 위해 JENKINS에서는 외부 cleanup 방식
##로컬에서는 JMeter tearDown + Groovy 기반 정리 방식을 채택


def _safe_delete(api_client, url: str):
    try:
        api_client.delete(url)
    except Exception:
        pass


def cleanup_nics(api_client, build_id: str):
    res = api_client.get(Endpoints.NETWORK_INTERFACE)
    assert res.status_code == 200

    for nic in res.json():
        name = nic.get("name", "")
        nic_id = nic.get("id")

        if build_id not in name:
            continue

        _safe_delete(api_client, f"{Endpoints.NETWORK_INTERFACE}/{nic_id}")


def cleanup_block_storages(api_client, build_id: str):
    res = api_client.get(Endpoints.BLOCK_STORAGE)
    assert res.status_code == 200

    for storage in res.json():
        name = storage.get("name", "")
        storage_id = storage.get("id")

        if build_id not in name:
            continue

        _safe_delete(api_client, f"{Endpoints.BLOCK_STORAGE}/{storage_id}")


def cleanup_vms(api_client, build_id: str):
    res = api_client.get(Endpoints.VIRTUAL_MACHINE)
    assert res.status_code == 200

    for vm in res.json():
        name = vm.get("name", "")
        vm_id = vm.get("id")

        if build_id not in name:
            continue

        _safe_delete(api_client, f"{Endpoints.VIRTUAL_MACHINE}/{vm_id}")


def cleanup_subnets(api_client, build_id: str):
    res = api_client.get(Endpoints.SUBNET)
    assert res.status_code == 200

    for subnet in res.json():
        name = subnet.get("name", "")
        subnet_id = subnet.get("id")

        if build_id not in name:
            continue

        _safe_delete(api_client, f"{Endpoints.SUBNET}/{subnet_id}")


def cleanup_vnets(api_client, build_id: str):
    res = api_client.get(Endpoints.VIRTUAL_NETWORK)
    assert res.status_code == 200

    for vnet in res.json():
        name = vnet.get("name", "")
        vnet_id = vnet.get("id")

        if build_id not in name:
            continue

        _safe_delete(api_client, f"{Endpoints.VIRTUAL_NETWORK}/{vnet_id}")


def cleanup_all_resources(api_client, build_id: str):
    cleanup_vms(api_client, build_id)
    cleanup_block_storages(api_client, build_id)
    cleanup_nics(api_client, build_id)
    cleanup_subnets(api_client, build_id)
    cleanup_vnets(api_client, build_id)
