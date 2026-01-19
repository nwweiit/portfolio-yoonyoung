# CI 환경 구성 및 Jenkins 안정화 이슈

## 문제 상황

Jenkins 기반 CI 환경에서 `pytest` 실행 및 `Allure` 리포트 자동 생성을 구성하던 중,  
빌드가 초기에는 정상 동작하다가 특정 시점부터 **간헐적으로 실패**하는 문제가 발생했다.

특히 Python 가상환경(.venv)과 의존성 설치 단계에서  
- 어떤 날은 정상적으로 빌드가 완료되지만  
- 어떤 날은 패키지를 인식하지 못하거나 설치 단계에서 실패하는 등  
빌드 결과가 환경 상태에 따라 달라지는 현상이 나타났다.

---

## 문제 발생 조건

- `cleanWs()`를 사용하여 매 빌드마다 workspace를 초기화
- 매 빌드마다 `.venv`를 새로 생성하고 `pip install -r requirements.txt` 수행
- 외부 네트워크 접근이 제한된 CI 환경
- Jenkins 실행 계정과 SSH 접속 계정이 분리된 구조
- Jenkins `sh` 스텝은 기본적으로 non-login shell로 실행됨

이로 인해 **이상적인 CI 설계(매 빌드 초기화)** 와  
**운영 환경의 제약(네트워크·권한)** 이 충돌하는 상황이 발생했다.

---

## 해결 전 코드 (시도 1)  
### cleanWs + 매 빌드 가상환경 재생성 (초기 설계)

**의도**  
이전 빌드의 오염이나 환경 변수 간섭 없이  
항상 동일한 조건에서 테스트를 실행하기 위함.

```
stage('Clean Workspace (Before)') {
    steps {
        cleanWs()
    }
}

stage('Prepare Python Environment') {
    steps {
        sh '''
        cd project_root
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install allure-pytest
        '''
    }
}
```

## 문제점

- `cleanWs()`로 인해 `.venv`가 매 빌드마다 삭제됨  
- 네트워크 제한 환경에서 `pip install`이 간헐적으로 실패  
- 빌드 성공 여부가 환경 상태에 의존하게 됨  

---

## 해결 전 코드 (시도 2)  
### Jenkinsfile 내부에서 강제 설치 시도

### 의도
웹 콘솔 접속이 불가능한 상황에서  
Jenkins 내부에서라도 필요한 패키지를 설치해 빌드를 유지하려고 시도함.

```
python3 -m ensurepip --upgrade || true
python3 -m pip install --user allure-pytest || true
.venv/bin/python -m pytest tests/api/blockstorage -v \
  --alluredir=allure-results
```
