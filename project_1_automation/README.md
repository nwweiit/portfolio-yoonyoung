# Project 1 — UI Test Automation in Selenium

## 📌 프로젝트 개요

본 프로젝트는 웹 서비스의 주요 사용자 기능을 대상으로  
Selenium 기반 UI 테스트 자동화를 구현한 프로젝트입니다.

테스트 코드는 **Page Object Model(POM)** 구조를 적용하여  
UI 요소 접근 로직과 테스트 로직을 분리하였으며,  
동적 UI 환경에서도 안정적으로 동작하도록 설계되었습니다.

부트캠프 초기 프로젝트로 UI 기반 자동화 테스트 구조를 설계하고 구현하는 것을 목표로 진행되었습니다.
본 리포지토리에는 **실제 프로젝트에서 제가 단독 또는 주도적으로 작성한 코드만 선별하여 포함**했습니다.
🔗 [Original Repository](https://github.com/minojj/Elice-BugsHunters.git)


---

## 🎯 프로젝트 목표

- Selenium 기반 UI 테스트 자동화 구현
- Page Object Model(POM)을 통한 테스트 구조 설계
- 동적 UI 환경에서도 안정적으로 동작하는 테스트 작성
- pytest 기반 테스트 실행 환경 구성

---

## 🧠 My Role & Key Contributions

- Page Object Model 기반 UI 테스트 구조 구현
- 테스트 구조 설계 (BasePage 클래스, conftest.py)
- Custom Agent/Billing system 도메인 테스트 구현
- pytest 기반 테스트 환경 구성

---

## 🛠 사용 기술

| 구분 | 기술 |
|-----|-----|
| Language | Python |
| Test Framework | pytest |
| UI Automation | Selenium WebDriver |
| Test Structure | Page Object Model |
| Collaboration | Jira |
---

## 🧱 테스트 구조

본 프로젝트는 **Page Object Model(POM)** 구조를 기반으로 구성되었습니다.

### BasePage

모든 페이지 클래스가 공통적으로 사용하는 기능을 제공하는 베이스 클래스입니다.

주요 기능

- Selenium WebDriverWait 기반 안정적인 element 접근
- 공통 element 탐색 메서드 제공
- 안정적인 클릭 동작 처리

```python
get_element()
get_elements()
click_safely()
```

이를 통해 테스트 코드에서 UI 요소 접근 방식을 표준화하고
코드 재사용성을 높였습니다.
---

# 🧩 Page Object

각 페이지의 UI 요소와 동작을 **Page 클래스**에서 관리합니다.

### 예시
- Agent Explorer 페이지  
- Agent 생성 페이지  
- Agent 관리 페이지  

### Page 클래스에서는
- locator 정의  
- 페이지 동작 메서드 구현  
- UI 상태 검증 로직  

---

# 🧪 Tests

`tests` 폴더에서는 실제 테스트 시나리오를 작성합니다.  
각 테스트는 Page Object를 사용하여 **사용자 흐름 기반 동작을 검증**합니다.

### 예시
- Agent 생성 기능 테스트  
- Agent 삭제 기능 테스트  
- Agent 관리 기능 테스트  

---

# ⚙ 테스트 환경 구성

`pytest` 기반 테스트 환경을 구성하기 위해  
`conftest.py`를 사용하여 **공통 테스트 설정**을 관리했습니다.

### 예시
- WebDriver 초기화  
- 테스트 환경 설정  
- 공통 fixture 제공  

이를 통해 테스트 코드에서 반복되는 환경 설정을 제거했습니다.

---

# 🔎 테스트 안정성 고려 사항

UI 자동화 테스트의 특성상 동적 UI 동작으로 인해 테스트가 불안정해질 수 있습니다.  
다음과 같은 방법으로 이를 해결했습니다.

### ✅ Explicit Wait 활용
- `WebDriverWait` 및 `ExpectedConditions` 사용  
- UI 렌더링 완료 후 테스트가 실행되도록 대기 로직 적용  

### ✅ Scroll 기반 요소 탐색
- 카드 목록처럼 스크롤 기반 로딩 구조를 가진 UI에서  
  모든 요소를 탐색할 수 있도록 `scroll` 로직 구현  

### ✅ JavaScript 기반 클릭 처리
- Selenium의 기본 `click()`으로 동작하지 않는 일부 UI 요소에 대해  
  JavaScript를 활용한 클릭 로직으로 안정성 확보  

---

# 📈 프로젝트를 통해 얻은 경험

이 프로젝트를 통해 다음과 같은 경험을 얻었습니다.

- Selenium 기반 UI 테스트 자동화 구현 경험  
- Page Object Model 구조 설계 경험  
- 동적 UI 환경 대응 테스트 작성  
- pytest 기반 테스트 실행 환경 구성  

---

# 💡 회고 (Reflection)

본 프로젝트에서는 **Selenium 기반 UI 자동화를 처음 구조화**하면서  
Page Object Model 기반 테스트 구조를 설계했습니다.  
이를 통해 테스트 코드의 재사용성과 유지보수성을 개선할 수 있었습니다.

다만 일부 테스트는 **UI 상태나 실행 순서에 영향을 받는 구조**가 발생하기도 했습니다.  
이 경험을 통해 이후 프로젝트에서는 다음의 중요성을 인식하게 되었습니다.

- 테스트 독립성 확보  
- API 기반 테스트 활용  
- 테스트 환경 관리  

이러한 경험은 이후 진행한 **API 및 성능 테스트 자동화 프로젝트 (Project 2)** 설계에 큰 영향을 주었습니다.


