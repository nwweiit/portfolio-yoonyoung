# Project 2 – API & Performance-Centered Test Automation with E2E

## 🔎 Project Overview

**ECI라는 클라우드 인프라 관리 서비스**를 인증, 환경, 성능을 고려해 **테스트 자동화 체계를 설계**하고<br>
CI 환경에서 **실행 → 검증 → 리포팅까지 연결**하는 것을 목표로 한 프로젝트입니다.

- 테스트 레이어: API / Performance / E2E
- 주요 초점:
  - 인증·환경·리소스 의존성을 고려한 테스트 구조
  - 공용 테스트 환경에서의 안정적인 성능 테스트 설계
 
## 📎 Evidence & Reports

- 🔗 [ECI_Test_Result_Report_Summary](docs/reports/ECI_Test_Result_Report_Summary.md)
  → 자동화 범위, 성능 판단, 실패 분석 요약  
  
- 🔗 [Metrics & Visual Evidence](docs/reports/metrics.md)
  → 테스트 결과, 성능 지표, 실행 증거를 **포트폴리오 관점에서 요약**

- 🔗 [legacy project main README](docs/reports/legacy_project_main_readme.md)
  → 실제 프로젝트 진행 당시 사용된 **원본 팀 문서**

 
## 📊 Project Results (Summary)

- API Tests
  - Total: 158
  - Automated: 137 (86.7%)
  - Parallel Execution: 6 workers
  - Avg Runtime: ~3 min

- Performance Tests
  - Stable: 800 / 30 / 10
  - Upper Bound: 1100 / 40 / 30
  - Stress: 1300 / 40 / 30

- E2E Tests
  - Core VM & Resource Lifecycle Covered
 
## 🖥️ Test Strategy Highlights

### 📐 Resource Dependency & Fixture-based Test Design

본 프로젝트의 테스트 대상 리소스(Network, Storage, Compute)는 **계층적 의존 관계를 가지며, 공용 테스트 환경 특성상 지속적 유지가 불가능**했습니다.
→ 각 테스트가 반드시 다음 원칙을 따르도록 설계했습니다.

이를 통해 테스트 간 간섭을 방지하고 반복 실행 가능한 **상태 격리(State-isolated) 테스트 환경**을 구축했습니다.

- 전체 Test에서 Resource dependency 해결을 위해 

- API Tests:
  - Stateless API 중심으로 병렬 실행
  - Resource dependency는 fixture lifecycle 구조 표준화로 관리

- Performance Tests:
  - GET: Load / Spike
  - POST: Soak only (stateful & resource-intensive)
  - Resource dependency는 setup과 teardown 단계를 거치고, clean up으로 safety net 구축

- E2E Tests:
  - User flow 신뢰성 확보를 위해 순차 실행
  - Resource dependency는 단계별로 생성-삭제를 반복하며 관리 


## 🧠 My Role & Key Contributions

API / Performance 테스트 전반의 **공통 테스트 체계 설계**와 E2E 테스트를 포함한 **실행 환경 구성**에 기여했으며,<br>  
**Network 및 Parallel File System 도메인 테스트 구현을 주도적으로 담당**했습니다.<br>

> E2E 테스트는 API 테스트의 신뢰성 확보를 우선 전략으로 두고,  
> 사용자 흐름 검증을 위한 **보조 수단으로 부분 적용**했습니다.

다음은 해당 프로젝트에서 제가 **핵심 기여한 영역**입니다.

<details>
<summary>1️⃣ OAuth 인증 구조 개선을 통한 API 테스트 안정성 확보</summary>

**기여 내용**
- OAuth 인증 흐름을 분석하여 토큰 발급 로직을 분리
- 발급된 토큰을 .env에 저장하고 pytest fixture로 공통 사용
- 토큰 만료 시 재발급 가능하도록 구조 설계

**결과**
- API 테스트 간 인증 의존성 제거
- 테스트 재사용성과 실행 안정성 확보

</details>

<details>
<summary>2️⃣ 테스트 코드와 실행 환경을 분리하기 위한 환경 변수 표준화</summary>
  
**기여 내용**
- .env + config.py를 통해 계정 정보, ZONE_ID, JMeter 실행 경로 등을 코드와 분리<br>
- 로컬 / CI 환경에서 동일한 테스트 코드 재사용 가능하도록 구성<br>

**결과**
- 환경 변경 시 코드 수정 최소화<br>
- CI 연계 용이성 향상<br>

</details>
  
<details>
<summary>3️⃣ JMeter 기반 성능 테스트 자동화 파이프라인 구축</summary>

**기여 내용**
- JMeter .jmx 실행을 위한 run_jmeter.sh 작성
- 결과 .jtl 파일을 검증하는 Python 스크립트 구현
- 두가지를 한번에 자동실행할 수 있는 run_all_on_local.sh 작성
- Jenkins에서 성능 테스트 자동 실행 가능하도록 구성

**결과**
- 성능 테스트 실행 및 결과 검증 자동화
- 반복 실행 가능성 확보
  
</details>

<details>
<summary>4️⃣ 부하 실험을 통한 성능 한계·안정 구간 도출</summary>

**기여 내용**  
- thread / ramp-up / loop count를 조절하며 부하 실험 수행
- 최대 부하 구간, 성능 한계 지점, 안정 구간 도출

**결과**
- 단순 실행이 아닌 실험 기반 성능 분석 수행
- 성능 기준 판단 근거 확보
- 
</details>

<details>
<summary>5️⃣ Jenkins + Allure를 활용한 CI 기반 테스트 결과 리포팅</summary>

**기여 내용**  
- pytest + Allure 연동
- Jenkins 실행 결과를 시각화된 리포트로 제공

**결과**
- 테스트 결과를 팀 단위로 공유 가능한 산출물로 제공
- 
</details>

<details>
<summary>6️⃣ 프로젝트 산출물 및 결과 보고서 작성</summary>

**기여 내용**
- 프로젝트 전체 흐름과 테스트 전략을 설명하는 main README.md 작성
- 팀 단위 테스트 결과 보고서 작성에 참여
  - 테스트 환경 및 실행 구조 정리
  - 성능 테스트 결과 분석 및 부하 기준 도출
  - 실패 테스트 케이스 원인 분석 및 품질 리스크 정리
  - 자동화를 통해 발견된 주요 결함 요약
  - 향후 테스트 및 기술적 개선 방향 제안
  중심으로 담당

**결과**
- 테스트 범위, 실행 결과, 품질 판단 근거를 외부에서도 이해 가능한 형태로 정리
- 단순 실행 결과 나열이 아닌, **분석·판단 중심의 QA 결과 보고서**로 프로젝트 성과를 문서화
- 향후 회귀 테스트 및 품질 개선 논의에 활용 가능한 기준 자료로 활용 가능

</details>


## 🎯 Troubleshooting & Key Design Decisions

### ⭐ 대표 트러블슈팅 (Core Design Decisions)

<details>
<summary><strong>1️⃣ OAuth 기반 인증 구조에서 API 토큰 전략 전환 이슈</strong></summary>

**문제**  
API 테스트 중 Selenium 기반 재로그인이 간헐적으로 발생하고, 병렬 실행이 불가능한 구조였음.

**해결방법**  
OAuth 기반 UI 로그인 구조를 분석하여 API 단독 토큰 자동화의 한계를 인정하고,  
UI 1회 토큰 발급 + API 테스트 완전 분리 전략으로 전환.

**결과**  
- UI/API 테스트 책임 분리  
- 병렬 실행 가능  
- 테스트 안정성 향상

🔗[OAuth 기반 인증 구조에서 API 토큰 자동화 전략 전환 이슈](docs/troubleshooting/oauth_ui_token_strategy_tradeoff.md)

</details>


<details>
<summary><strong> 2️⃣ pytest fixture 생명주기 및 리소스 정리 안정화 이슈</strong></summary>

**문제**  
리소스 간 의존성이 강한 환경에서 fixture 기반 생성/삭제를 사용하던 중, 테스트 실패 시 리소스가 잔존하여 이후 테스트를 지속적으로 오염시키는 문제가 발생함.
특히 `session scope fixture` 사용으로 삭제 책임이 불명확해짐.

**해결방법**  
- fixture는 리소스 생성 책임만 담당하도록 축소
- 삭제는 별도의 `safe_delete + polling` 유틸 함수로 분리
- 삭제 요청 이후 실제 삭제 완료를 보장하도록 구조 재설계.
- 모든 실제 리소스 fixture를 `function scope`로 전환.

**결과**  
- 테스트 성공/실패 여부와 무관하게 리소스 정리 보장
- 비동기 삭제로 인한 연쇄 실패 제거
- 테스트 신뢰성과 반복 실행 안정성 향상
- fixture scope를 “책임 경계”로 설계하는 기준 확립

🔗[API 테스트에서 fixture의 생명주기와 삭제 보장 이슈](docs/troubleshooting/pytest_fixture_lifecycle_and_cleanup.md)

</details>


<details>
<summary><strong> 3️⃣ Jenkins CI 환경에서 Python 테스트 파이프라인 안정화 이슈</strong></summary>

**문제**  
Jenkins CI 환경에서 `pytest + Allure` 자동화 파이프라인을 구성하던 중 `cleanWs()`와 네트워크 제한으로 인해 가상환경 및 패키지 설치가 간헐적으로 실패하며 
빌드 결과가 환경 상태에 따라 달라지는 문제가 발생함.

**해결방법**  
- 매 빌드 초기화를 포기
- VM에 사전 구성된 Python 가상환경을 재사용하는 전략으로 전환
- Jenkins는 테스트 실행과 리포트 생성만 담당하도록 역할을 단순화

**결과**  
- CI 환경에서 테스트 실행 안정성 확보
- 네트워크/권한 제약 환경에서도 빌드 실패 제거
- 발표·시연 환경에서도 일관된 결과 보장
- “이상적인 CI”보다 “현실적인 CI” 설계 경험 축적
  
🔗[CI 환경 구성 및 Jenkins 안정화 이슈](docs/troubleshooting/CI_environment_and_Jenkinsfile.md)

</details>


<details>
<summary><strong> 4️⃣ 성능 테스트에서 teardown vs cleanup 전략 결정 이슈</strong></summary>

**문제**  
성능 테스트(JMeter) 실행 중 실패가 발생할 경우, tearDown Thread Group이 실행되지 않아 테스트 리소스가 잔존하고
다음 테스트 실행에 영향을 주는 문제가 발생함.

**해결방법**  
- tearDown은 best-effort로 유지
- CI 환경에서는 Jenkinsfile에서 명시적인 cleanup 로직을 별도로 실행하도록 설계
- 로컬 실행(run_all_on_local.sh)에는 safety net으로 cleanup 단계를 추가

**결과**  
- 성능 테스트 실패 시에도 리소스 정리 보장
- CI 환경에서 테스트 결과와 무관한 안정성 확보
- 반복 성능 테스트 시 환경 오염 제거
- teardown과 cleanup의 역할을 명확히 분리한 설계 확립
  
🔗[성능 테스트에서 teardown vs cleanup 전략 결정 이슈](docs/troubleshooting/performance_test_teardown_vs_cleanup_tradeoff.md)

</details>

### 📌 추가 트러블슈팅 (Implementation / Edge Cases)

<details>
<summary><strong> 5️⃣ 로컬 / CI 실행 환경 차이로 인한 성능 테스트 자동화 스크립트 실행 이슈 </strong></summary>
  
🔗[로컬 / CI 실행 환경 차이로 인한 성능 테스트 자동화 스크립트 실행 이슈](docs/troubleshooting/local_ci_execution_entrypoint_issue.md)

</details>

<details>
<summary><strong> 6️⃣ 성능 테스트 설계 오류로 인한 부하 한계치 오판 이슈 </strong></summary>
  
🔗[성능 테스트 설계 오류로 인한 부하 한계치 오판 이슈](docs/troubleshooting/performance_load_design.md)

</details>

<details>
<summary><strong> 7️⃣ MUI Autocomplete 및 Select 자동화 이슈 </strong></summary>
  
🔗[MUI Autocomplete 및 Select 자동화 이슈](docs/troubleshooting/mui_autocomplete_select.md)

</details>


