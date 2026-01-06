ECI Test Automation Project_team03 
=

**Automated test project for ECI services using pytest, Jenkins, and JMeter.**

> **왜 나만 안 되는 걸까?** 그 의문에는 언제나 정답이 있습니다. \
> 저희는 정답을 찾아내서 어디에서든 동작하게 만드는 사람들입니다.


## 🔎Project Overview

- 대상 서비스: **Elice Cloud Infrastructure(ECI)**
- 목적: 클라우드 서비스의 동작을 확인하기 위한 API 기능 테스트, 성능 테스트, 사용자흐름을 고려한 E2E 테스트
- 특징:
    - **Page Object Model(POM)** 기반 구조
    - **명시적 대기**를 활용한 안정적인 테스트
    - **CI 환경(Jenkins)을 이용한 자동화**를 통해 주기적인 기능 및 성능 점검
    - 로컬/CI환경에서의 **API 및 Performance 테스트 병렬 실행 전략**을 통한 테스트 소모 시간 단축
    - **부하-스파이크-부하 테스트의 구조**로 클라우드 환경의 자동적인 복구 안정성 평가
    - 주요 기능을 기준으로 한 **사용자 중심 E2E 테스트 시나리오 구성**
    - 자원 상태 및 사용량 확인 API를 포함한 **서비스 가시성(Visibility) 기능 검증**

## ⌨️Tech Stack

- **Language** : Python 3.11.6
- **Test Framework** : pytest 8.3.4
- **Browser Automation** : Selenium WebDriver 4.26.1(Chrome)
- **CI/CD** : Jenkins
- **Test case Management** : [Google Sheets](https://docs.google.com/spreadsheets/d/1e8LNYk1bJ4Kj9FAFixmPWQUegHEZanXB-SdNI_wVGUc/edit?usp=sharing)


## 📐Test Scope

- [API Tests](project_root/tests/api/README.md)
- [Performance Tests](project_root/performance/README.md)
- [E2E Tests](project_root/tests/e2e/README.md)


## 🧱 Test Architecture (Optional)

- 테스트는 API, UI, Performance 레이어로 분리하여 설계되었습니다.
- 각 테스트는 독립적으로 실행 가능하도록 구성되었습니다.


## 📊Test Coverage

### ▪️API Domain Coverage
- Authentication & Token
- Home & Infra
- Compute (Virtual Machine)
- Network
- Block Storage
- Object Storage
- Parallel File System

### ▪️Performance Coverage
- Load Test (GET APIs)
- Spike Test (GET APIs)
- Soak Test (POST APIs)

    #### Performance Test Design Rationale
    API의 특성에 따라 성능 테스트 유형을 구분하여 설계하였습니다.

    - **GET API**는 조회 중심 요청으로, 사용자 트래픽 증가 및 순간적인 부하 변화에 대한
      처리 능력을 검증하기 위해 **Load Test**와 **Spike Test**를 수행하였습니다.
    - **POST API**는 리소스를 생성하는 상태 변경 요청으로,
      단기 고부하보다 장시간 실행 시 안정성과 리소스 관리 여부가 중요하다고 판단하여
      **Soak Test**를 중심으로 검증하였습니다.

    - POST API에 대해서는 비현실적인 트래픽 패턴과 과도한 리소스 소모를 방지하기 위해
      단기 고강도 Load/Spike 테스트를 의도적으로 제외하였습니다.

### ▪️E2E Coverage
- Virtual Machine creation user flow
- Resource CRUD lifecycle (Create → Update → Delete)

    #### E2E Test Execution Strategy
    - E2E 테스트는 실제 사용자 흐름과 리소스 생명주기를 검증하는 특성상,
    테스트 간 상태 공유 및 리소스 충돌 가능성이 존재합니다.
    - 이에 따라 테스트 안정성과 결과 신뢰도를 우선하여
    E2E 테스트는 병렬 실행에서 제외하고 순차 실행으로 설계하였습니다.


## 📈 Test Pass Criteria

### ▪️API Tests
- HTTP status code 및 response schema 검증을 기준으로 테스트 통과 여부를 판단합니다.

### ▪️E2E Tests
- 주요 사용자 흐름이 오류 없이 수행되고, 기대 결과가 화면에 정상적으로 반영되는 경우 통과로 판단합니다.

### ▪️Performance Tests
- CI와 연동된 성능 회귀 테스트로, 성능이 기준 수준으로 유지되는지 주기적으로 검증합니다.
- 부하 파라미터 표기 형식: **Threads / Ramp-up / Loop Count**

    #### **Load Level Definition**
    - 부하 최대 한계치(Stress): **1300 / 40 / 30**
    - 최대 처리 성능 상한 구간(Upper Bound): **1100 / 40 / 30**
    - 서비스 안정 구간(Stable Range): **800 / 30 / 10**

    #### **Pass / Fail Criteria**
    - Error Rate, Response Time, TPS 기준을 기반으로 성능 적합 여부를 판단합니다.
    - Soak Test의 경우 예외적으로 **Response Time Stdev(표준편차)** 기준을 포함합니다.



## ▶️How to Run

<details>
<summary>1️⃣ .env 파일 생성</summary>

아래 .env.sample에 따라 project_root 아래에 .env 파일을 생성해주세요.

[.env.samlpe](project_root/.env.sample)
</details>

<details>
<summary>2️⃣ venv 가상환경 실행</summary>

테스트의 일관성을 위해 venv 가상환경을 실행해주세요.  

```
.\.venv\Scripts\Activate.ps1
```
</details>

<details>
<summary>3️⃣ 필요 패키지 설치</summary>

requirements.txt 를 통해 필요 패키지를 설치해주세요.

```
pip install -r requirements.txt
```
</details>

<details>
<summary>4️⃣ API 토큰 발급</summary>

API 접속을 위한 토큰을 발급해주세요. (토큰 유효기간: 30분)
  
  ```
  python -m scripts.get_token
  ```
</details>


<details>
<summary>5️⃣ .env 파일 및 sh파일 확인</summary>

원활한 테스트 진행을 위해 .env파일과 sh파일의 줄바꿈형식을 **LF**로 변경 후 저장해주세요.
</details>


<details>
<summary>6️⃣ API 기능테스트 실행</summary>

로컬에서만 병렬 설정을 켜서 6개의 worker를 지정할 수 있도록 해당 명령어를 사용해주세요.

```
python -m pytest tests/api --local-parallel --workers 6
```
</details>

<details>
<summary>7️⃣ 성능 테스트 실행</summary>

성능 측정 후, 기준에 부합하는지 검증도 할 수 있도록 로컬에서는 해당 파일을 이용해주세요.

```
bash performance/scripts/run_all_on_local.sh
```
</details>

<details>
<summary>8️⃣ E2E 테스트 실행</summary>

E2E는 사용자흐름에 맞춰 진행하되, 병렬 실행에서 제외한 대신 headless모드로 진행해주세요.
현재 headless 모드가 기본으로 설정되어 있습니다.

```
python -m pytest tests/e2e
```
</details>

<details>
<summary>9️⃣ Jenkins 실행</summary>

직접 Jenkins UI에서 빌드 상황을 볼 수 있습니다. 계정 정보는 따로 연락부탁드립니다.

[GO Jenkins](http://61.107.202.228:8080/)
</details>


## 📄Test Results & Reporting

- CI(Jenkins) 환경에서 테스트 실행 결과는 **Allure Report**를 통해 확인할 수 있습니다.
- Allure 리포트를 통해 테스트 성공/실패 여부, 실패 사유 및 실행 히스토리를 시각적으로 제공합니다.
- Jenkins 빌드 실행 후 Allure 리포트를 통해 각 테스트 단계별 결과를 확인할 수 있습니다.
- 상세 실행 로그는 Jenkins Console Output 및 Allure 리포트를 통해 확인합니다.

## ⚠️ Known Limitations & Assumptions

- 테스트 코드는 크로스 플랫폼 실행을 고려하여 작성되었습니다.
- 하지만 팀 내 macOS 환경이 부재하여 macOS에서의 실제 실행 검증은 수행하지 못했습니다.
- 해당 환경에 대한 실행 가능성은 추가 검증이 필요합니다.
