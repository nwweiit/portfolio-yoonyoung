## 문제 상황

- 테스트 대상 시스템의 리소스 관리 정책상 **테스트 대상 리소스는 항상 초기 상태(삭제된 상태)**를 유지해야 함
- 기존에는 생성된 리소스를 유지한 채 조회/수정/삭제가 가능했으나 정책 변경 이후 단일 테스트 흐름으로는 리소스 상태 유지가 불가능해짐
- 리소스 간 의존성이 강하여 테스트마다 **순차 생성 / 역순 삭제**를 수행하는 fixture를 리소스별로 구성함
- 그러나 테스트 반복 실행 과정에서 **리소스 정리가 누락되거나 다음 테스트에 영향을 주는 현상**이 발생
- 특히 상위 리소스를 `session scope` fixture로 구성하면서 테스트 실패 시 삭제 책임이 명확하지 않아 리소스가 잔존하고 이후 테스트를 지속적으로 오염시키는 문제가 발생함

---

## 문제 발생 조건

- pytest fixture는 자원의 **생성/소멸 시점 자체는 관리**할 수 있으나
  - 삭제 요청 이후 **리소스가 실제로 제거되었는지**까지는 보장하지 않음
- 비동기 삭제 구조(API 특성)로 인해
  - 하위 리소스 삭제 요청 직후
  - 상위 리소스 삭제가 시도되면서 연쇄 실패 발생 가능
- 삭제 중 하나라도 실패할 경우,
  - fixture `finally` 블록 내 이후 정리 로직이 중단되어
  - 리소스 일부가 잔존하는 상태로 다음 테스트가 실행됨
- `session scope` fixture 사용으로 인해
  - 리소스 삭제 책임이 테스트 단위와 분리되고
  - 실패 시 정리 누락의 영향 범위가 확대됨

→ 결과적으로 문제의 핵심은 **fixture 간 삭제 순서 그 자체가 아니라 삭제 요청 이후 실제 삭제 완료를 보장하지 않는 구조**에 있었음

---

## 해결 및 결과
### 삭제 완료 보장을 위한 구조 변경 (핵심 코드)

#### 해결 전 (fixture teardown에서 delete만 호출)

```
@pytest.fixture
def nic_stack(api_client, vnet_id):
    subnet_id = NetworkResources.create_subnet(api_client, vnet_id)
    nic_id = NetworkResources.create_network_interface(api_client, subnet_id)
    yield {"subnet_id": subnet_id, "nic_id": nic_id}
    NetworkResources.delete_network_interface(api_client, nic_id)
    NetworkResources.delete_subnet(api_client, subnet_id)
```


#### 해결 후 (삭제 완료 보장 로직 분리)

```
def safe_delete(api_client, endpoint, resource_id):
    api_client.delete(f"{endpoint}/{resource_id}")
    wait_until_resource_deleted(api_client, endpoint, resource_id)
```
```
def wait_until_resource_deleted(api_client, endpoint, resource_id):
    for _ in range(10):
        res = api_client.get(f"{endpoint}/{resource_id}")
        if res.status_code == 404:
            return
    raise AssertionError("Delete not completed")
```




- 리소스 생성과 삭제의 책임을 명확히 분리하기 위해 fixture는 **생성 책임**, 별도의 유틸 함수는 **삭제 완료 보장 책임**을 갖도록 구조를 재설계
- 리소스 간 종속성을 명시적으로 고려하여
  - 하위 리소스가 실제로 삭제 완료된 이후
  - 상위 리소스 삭제가 진행되도록 설계 수정
- 삭제 요청 이후 상태를 폴링하여 **리소스가 완전히 제거되었음을 확인한 뒤 다음 단계로 진행**
- 테스트 성공/실패 여부와 무관하게 리소스 생성 및 삭제가 일관되게 수행됨을 검증
- 리소스 잔존으로 인해 테스트 흐름이 꼬이거나 다음 테스트 결과를 오염시키는 문제가 제거됨



---

## ✅최종 정리

- pytest fixture는 **편의 도구**이지 리소스 생명주기 전체를 책임지는 수단은 아님
- fixture 설계 시 실행 편의성뿐 아니라
  - **삭제 완료 보장**
  - **리소스 생명주기 책임**
  - **테스트 신뢰성**
  까지 함께 고려해야 함
- `scope` 선택은 단순한 성능 최적화 문제가 아니라 **삭제 책임을 누구에게 부여할 것인지에 대한 설계 결정**임을 학습함
