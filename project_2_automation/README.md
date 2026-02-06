# Project 2 – API & Performance Test Automation

## 🔎 Project Overview

**ECI라는 클라우드 인프라 관리 서비스**를 인증, 환경, 성능을 고려해 **테스트 자동화 체계를 설계**하고<br>
CI 환경에서 **실행 → 검증 → 리포팅까지 연결**하는 것을 목표로 한 프로젝트입니다.


## 🧠 My Role & Key Contributions

API / Performance 테스트 전반의 **공통 테스트 체계 설계** 와 E2E 테스트를 포함한 **실행 환경 구성**에 기여했으며<br>
그중 **Network 및 Parallel File System 도메인의 테스트 구현을 주도적으로 담당**했습니다.<br>

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


## 📎 Evidence & Reports

- 📄 **Test Result Report (Markdown)**  
  → 자동화 범위, 성능 판단, 실패 분석 요약  
  🔗 docs/reports/test_result_report.md


