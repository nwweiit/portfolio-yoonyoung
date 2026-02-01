# OAuth 기반 인증 구조에서 API 토큰 자동화 전략 전환 이슈

---

## 문제 상황 (1차 인지: 테스트 불안정)

API 기능 테스트 자동화를 진행하던 중 테스트 결과가 일관되지 않게 나타나는 현상을 발견함.

- API 테스트 실행 중 Selenium 기반 재로그인이 **간헐적으로 발생**
- 일부 테스트에서 `failed`가 아닌 `error` 발생
- 재로그인 이후 동일 테스트가 통과하는 경우가 있어 **로직 검증 실패가 아닌 구조적 문제**를 의심
- 토큰 재로그인 이후 “우연히 통과한 것처럼 보이는” 결과가 반복됨
- 추후 `xdist` 병렬 실행을 고려하던 중 `.env` 파일에 토큰을 기록·공유하는 구조가 **프로세스 간 충돌을 유발할 수 있음**을 인지

→ API 테스트가 UI 인증 흐름에 종속되어 있으며 **인증 수단과 테스트 대상이 분리되지 않은 구조**가 문제의 근본 원인일 가능성이 높다고 판단함.

---

## 문제 상황 (2차 시도: API 중심 테스트 구조 설계)

위 문제를 해결하기 위해 API 기능 테스트 자동화를 설계하면서 UI 테스트와 API 테스트의 의존성을 완전히 분리하는 것을 목표로 함.

- API 기능 테스트에서는 Selenium 및 UI 상태에 의존하지 않도록
  - API 기반 로그인으로 토큰을 발급/재갱신받아 사용하려는 전략을 수립
  - UI 자동화는 배제하고, API 테스트 내부에서 토큰을 자체적으로 관리하려고 시도

이에 따라 API 로그인 기반 토큰 관리 로직을 먼저 구현함.

그러나 실제 코드 구현 및 테스트 과정에서 **API 기반 로그인 및 토큰 발급이 전면 실패**하는 문제가 발생함.

---

## 문제 발생 조건

### 1. 인증 구조에 대한 초기 가정 오류

- API 기반 로그인 엔드포인트(`/api/auth/login`)가 존재한다고 가정
- API 요청만으로 access token 발급 및 재갱신이 가능할 것으로 예상

### 2. 실제 인증 구조 분석 결과

- 로그인 과정에서 네트워크 트래픽을 분석한 결과 인증 구조가 OAuth 기반 UI 로그인 흐름임을 확인
- 로그인 엔드포인트는 `/oauth/callback` 형태로 **UI 흐름 내부에서만 토큰이 발급**
- API는 인증 이후의 **검증자 역할**만 수행

즉
- API 단독으로는 로그인 및 토큰 발급이 구조적으로 불가능
- UI를 완전히 분리한 경우 자동 토큰 발급/재갱신 자체가 성립되지 않음

### 3. 토큰 구조상의 제약

- 토큰이 JWT 형식이 아님
- 만료 시간(exp) 파싱 불가
- Refresh Token을 발급하는 API 엔드포인트 미제공

→ 일반적인 access / refresh token 기반 자동 재갱신 전략을 적용할 수 없는 구조임을 확인

---

## 해결 전 코드 (시도 1)
### UI 기반 토큰 자동 발급 + 자동 재갱신 전략 (기존 방식)

#### 의도

- Selenium을 통해 UI 로그인을 수행
- UI에서 발급된 토큰을 API 테스트에서 사용
- 토큰 만료 시 UI 자동화를 통해 재발급하도록 설계

#### 기존 방식 요약

```
UI 자동화로 로그인
→ access token 추출
→ .env에 저장
→ API 테스트에서 사용
→ 토큰 만료 시 UI 재로그인으로 자동 갱신
```

#### 문제점
- Selenium 의존성으로 API 테스트 안정성이 UI 상태에 종속됨
- 병렬 실행 불가능
- 실행 환경(브라우저, 타이밍, 네트워크)에 따른 변수가 큼
- API 테스트의 본질과 무관한 UI 요소가 실패 원인이 될 수 있음

---

## 해결 전 코드 (시도 2)
### API 기반 토큰 발급 및 재갱신 시도

#### 의도

- API 테스트 내부에서 완전한 자율 토큰 관리를 구현하려는 시도
  - UI 자동화 제거
  - API 요청만으로 토큰을 발급/관리

```python
class ApiTokenManager:
    def _login(self):
        resp = requests.post(
            "https://portal.gov.elice.cloud/api/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
        )
        resp.raise_for_status()
        return resp.json()["accessToken"]
```

#### 문제점
- API 기반 로그인 엔드포인트 자체가 존재하지 않음
- 모든 요청이 인증 실패로 반환
- API 단독 로그인 방식은 구조적으로 불가능함을 확인

---

## 해결 후 코드
### 전략 전환: UI 1회 토큰 발급 + API 테스트 완전 분리

#### 전략 결정 배경
- 시스템 구조상 API 단독 토큰 자동화는 불가능하다는 점을 인정
- “완전 자동화”보다 테스트 안정성/병렬 실행 가능성/책임 분리를 우선하는 방향으로 전략 전환

#### 해결 전략
1. UI 자동화를 통해 토큰을 1회 발급
2. 발급된 토큰을 .env 파일에 저장하여 공유
3. 이후 모든 API 기능 테스트는 추가 로그인 과정 없이 API 요청만 수행


#### UI 기반 토큰 발급 전용 스크립트
```python
class UiTokenManager:
    def login_and_get_token(self) -> str:
        driver = self._create_driver()
        try:
            driver.get("https://qatrack.elice.io/eci/home")
            LoginPage(driver).login(self.username, self.password)

            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script(
                    "return window.localStorage.getItem('accessToken') !== null;"
                )
            )

            token = driver.execute_script(
                "return window.localStorage.getItem('accessToken');"
            )

            if not token:
                raise UiTokenExtractionError("accessToken 추출 실패")

            return token
        finally:
            driver.quit()
```

#### 토큰 저장 스크립트 (`get_token.py`)
```python
def main():
    manager = UiTokenManager()
    token = manager.login_and_get_token()
    set_key(Path(".env"), "ECI_ACCESS_TOKEN", token)
```

#### 실행 흐름
```
python -m scripts.get_token
pytest -n auto --dist loadfile tests/api
```

---
## 결과 검증
- UI 테스트와 API 테스트의 책임 완전 분리
- API 기능 테스트에서 Selenium 의존성 제거
- 병렬 실행 안정성 확보
- 테스트 환경 변수 감소로 실패 원인 축소
- 인증 구조 변경 없이도 안정적인 테스트 흐름 유지

---
## ✅최종 정리
- 인증 구조를 정확히 이해하지 못한 상태에서의 자동화는 실패로 이어질 수 있음
- 시스템 구조상 불가능한 자동화를 억지로 구현하기보다 **현실적인 한계를 인정하고 전략을 전환하는 판단**이 중요
- 테스트 자동화에서 “완전 자동화”보다 **안정성, 책임 분리, 병렬 실행 가능성이 더 중요한 경우**가 존재
- 사이트의 인증 구조와 명세를 먼저 분석한 뒤 자동화 가능 영역과 불가능 영역을 구분하는 것이 유지보수 가능한 테스트 설계의 핵심임을 학습
