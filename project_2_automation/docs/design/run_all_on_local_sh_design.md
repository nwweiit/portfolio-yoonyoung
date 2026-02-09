# 🧪 Performance Test Orchestration Design  
## run_all_on_local.sh

본 문서는 **ECI Test Automation Project**에서 사용한  
`run_all_on_local.sh` 스크립트의 **설계 의도와 실행 구조**를 설명합니다.

이 스크립트는 단순한 성능 테스트 실행기가 아니라,  
**공용 클라우드 환경에서의 서비스 안정성과 회복 능력**을 검증하기 위한  
성능 테스트 오케스트레이터 역할을 수행합니다.

---

## 1. Design Goals

`run_all_on_local.sh`는 다음 목표를 기준으로 설계되었습니다.

- 성능 테스트를 **단일 명령으로 일관되게 실행**
- 테스트 실행 단계와 **결과 판단 로직의 책임 분리**
- 공용 클라우드 환경 특성을 고려한 **안전한 실행**
- 실패 발생 시에도 **환경 오염을 방지하는 Safety Net 확보**
- Load → Spike → Recovery 구조를 통해 **자동 회복 능력 검증**

---

## 2. Overall Execution Flow

```text
LOAD (Initial)
   ↓
SPIKE
   ↓
LOAD (Recovery)
   ↓
SOAK
   ↓
Cleanup (Safety Net)
   ↓
Result Analysis (Python)
```

각 단계는 의도적으로 순차 실행되며,
실행 중 일부 테스트가 실패하더라도 전체 흐름이 중단되지 않도록 설계되었습니다.

---

## 3. Load–Spike–Load Execution Strategy

### 3.1 Why Load → Spike → Load?

본 프로젝트에서는 단순한 **최대 처리량 측정**보다  
**부하 이후 서비스의 회복 가능성**을 더 중요한 품질 지표로 보았습니다.

이를 위해 다음과 같은 실행 구조를 채택했습니다.

#### Initial Load
- 정상적인 운영 부하 상태에서의 **기본 안정성 확인**

#### Spike
- 순간적인 트래픽 급증 상황에서의 **처리 한계 관찰**

#### Recovery Load
- Spike 이후 동일한 부하를 다시 적용하여  
- 서비스가 **정상 상태로 회복되는지 여부 검증**

이를 통해 다음 항목을 확인할 수 있습니다.

- Spike 이후 **에러율이 지속되는지 여부**
- **응답 시간 분산(Response Time Variance)** 이 정상 범위로 복귀하는지
- 리소스 정리 및 상태 복구가 **자동으로 이루어지는지 여부**

---

## 4. Separation of Responsibilities

### 4.1 Shell Script (Execution Orchestration)

Shell Script는 **성능 테스트의 실행 흐름만 담당**하도록 설계되었습니다.

- JMeter 테스트 실행
- 테스트 실행 순서 제어
- 단계별 및 전체 실행 시간 측정
- 테스트 유형별 환경 변수 설정
- 테스트 종료 후 Cleanup 호출

```bash
bash performance/scripts/run_jmeter.sh --glob "*_load.jmx" _local
```

### 4.2 Python Script (Result Evaluation)

Python 스크립트는 결과 해석과 품질 판단만 담당합니다.

- JTL 파일 분석
- Error Rate / Response Time / TPS 계산
- 테스트 유형별 기준 적용
- 실패 여부 판단


```bash
python performance/scripts/analyze_result.py result.jtl
```


이로 인해:

- 실행 로직과 판단 로직이 명확히 분리됨
- 기준 변경 시 Python 코드만 수정 가능
- pytest에 의존하지 않는 독립적인 성능 분석 구조 확보

---

## 5. Test Type–Specific Validation Logic

### 5.1 GET APIs (Load / Spike)

- 사용자 조회 트래픽 특성 반영
- Load / Spike 테스트 수행
- Error Rate, Response Time 중심 검증

```bash
export REQUIRE_GET=true
```

### 5.2 Non-GET APIs (Soak)

- 리소스 생성·삭제를 수반하는 상태 변경 요청
- 단기 고부하 대신 장시간 안정성을 중심으로 검증
- 표준편차(Stdev) 기반 안정성 판단 포함

```bash
export REQUIRE_GET=false
```

---

## 6. Cleanup as a Safety Net

공용 테스트 환경 특성상 성능 테스트 실패 시 리소스 잔존은 치명적인 후속 테스트 오염으로 이어질 수 있습니다.

이를 방지하기 위해:

- 각 JMeter 테스트에 tearDown을 포함
- **추가적으로 Python 기반 Cleanup을 Safety Net으로 실행**

```bash
python performance/cleanup/cleanup_entry.py || true
```

이 구조를 통해:

- 테스트 성공/실패 여부와 무관하게 리소스 정리 보장
- 반복 성능 테스트 가능
- CI 환경에서도 환경 안정성 유지


---

## 7. Time Measurement & Observability

스크립트는 각 단계별 실행 시간을 측정하여 출력합니다.

```text
LOAD Time
SPIKE Time
RECOVERY Time
SOAK Time
TOTAL Time
```

이를 통해:

- 테스트 유형별 비용 파악
- CI 적용 시 단계별 타임아웃 기준 설정 가능
- 성능 테스트 자체의 실행 안정성 검증 가능

---

## 8. Why This Is Not a pytest Test

`run_all_on_local.sh`는 **pytest 기반 테스트가 아닙니다.**

- 테스트 케이스 단위 실행 ❌
- assertion 중심 검증 ❌
- pytest runner 의존 ❌

대신 본 스크립트는 다음 목적을 가집니다.

- **성능 테스트 시스템**으로서의 역할
- 실행 → 분석 → 판단을 포함한 **독립적인 구조**
- 실제 현업에서 사용되는 **성능 테스트 운영 방식에 가까운 설계**

즉, 본 스크립트는  
“테스트 코드”가 아니라 **성능 테스트 오케스트레이션 도구**로 정의됩니다.

---

## 9. Summary

`run_all_on_local.sh`는

- 단순 실행 스크립트가 아닌  
- **성능 테스트 실행을 표준화한 오케스트레이터**이며  
- 공용 클라우드 환경에서의 다음 항목을 검증하기 위해 설계되었습니다.

- **안정성 (Stability)**
- **부하 이후 회복 능력 (Recoverability)**
- **테스트 환경 보호 (Environment Safety)**

본 구조는 이후 **CI 환경으로 확장 가능하도록 설계**되었으며,  
성능 회귀 테스트 및 **품질 기준 판단의 기반 자료**로 활용될 수 있습니다.














