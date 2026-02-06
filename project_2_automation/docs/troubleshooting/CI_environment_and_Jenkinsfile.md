# CI 환경 구성 및 Jenkins 안정화 이슈

---

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

## 문제점

- `--user` 옵션으로 설치된 패키지의 경로가 불명확
- Jenkins 실행 계정 기준 PATH와 충돌
- pytest 실행 시 패키지 인식이 불안정

---


## 해결 전 코드 (시도 3)  
### 로그인 셸로 실행 환경 통일 (`bash -lc`)

### 의도
non-login shell 환경에서 가상환경 및 PATH가 제대로 반영되지 않는 문제를 의심하여
로그인 셸로 실행 환경을 통일하려고 시도함.

```
sh '''
bash -lc "
cd project_root
source .venv/bin/activate
pytest tests/api/blockstorage -v \
  --alluredir=allure-results/api_blockstorage
"
'''
```

## 문제점

- 일부 환경에서는 동작했으나 여전히 간헐적 실패 발생
- venv 활성화 여부와 실제 Python/PIP 경로 간 불일치 가능성 존재

---

## 해결 후 코드
### 전략 전환: 사전 구성된 가상환경 재사용

### 의도
여러 시도를 통해 문제의 원인이 특정 명령어나 Jenkins 문법이 아니라,
네트워크 제한 환경에서 매 빌드마다 의존성을 재설치하는 구조 자체에 있음을 인식

### VM 터미널에서 사전 환경 구성

```
# Python 버전 확인
python3 --version

# 프로젝트 디렉토리 이동
cd project_root

# 가상환경 생성
python3 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 프로젝트 의존성 설치
pip install -r requirements.txt

# Allure pytest 플러그인 설치
pip install allure-pytest
```

### Jenkinsfile 수정

- `cleanWs()` 단계 제거
- 가상환경 생성 및 패키지 설치 로직 제거
- Jenkins는 테스트 실행 및 리포트 생성만 담당

```
sh '''
cd project_root
. .venv/bin/activate
pytest tests/api/blockstorage -v \
  --alluredir=allure-results/api_blockstorage
'''
```

---

## 결과 검증
- pytest 테스트 정상 실행 확인
- Allure 리포트 정상 생성 및 Jenkins에서 확인 가능
- 빌드 성공 여부가 환경 상태에 영향을 받지 않고 안정적으로 유지됨
- 발표/시연 환경에서 반복 실행 시에도 동일한 결과 확인

---

## ✅최종 정리
- 매 빌드 초기화를 통한 이상적인 CI 설계는 환경 제약이 없는 경우에만 유효함
- 네트워크·권한이 제한된 환경에서는 의존성 재설치보다 실행 안정성을 우선하는 전략이 필요함
- 단기 시연 목적과 장기 CI 설계 목적을 구분하여 상황에 맞는 설계 결정을 내리는 것이 중요함을 배움

