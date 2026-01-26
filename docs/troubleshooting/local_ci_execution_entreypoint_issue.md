# 로컬 / CI 실행 환경 차이로 인한 성능 테스트 자동화 스크립트 실행 이슈

---

## 문제 상황

성능 테스트 자동화를 위해 Jenkins CI 환경 기준으로 다음 스크립트들을 작성함.

- `run_jmeter.sh`  
  : JMeter 성능 테스트 실행 스크립트
- `analyze_result.py`  
  : JTL 결과 분석 및 SLA 검증용 스크립트

Jenkins CI 환경에서는 위 스크립트들이 정상 동작했으나, 로컬 환경에서 **전체 성능 테스트를 한 번에 실행하고 검증**하는 것이 어려움

→ 로컬 검증을 위해 `run_all_on_local.sh` 형태로 run_jmeter.sh로 jxm파일을 실행, analyze_result.py에서 그대로 나온 jtl파일을 분석실행을 시도
→ 그러나 다음과 같은 문제가 반복적으로 발생함

- Git Bash / PowerShell 환경에서 `python` 또는 `py: command not found` 오류 발생
- 가상환경(`.venv`)을 활성화해도 bash에서 Python 실행 명령어를 인식하지 못함
- 팀원마다 Python 실행 명령어가 서로 다름 (`python`, `python3`, `py`)
- PowerShell 전용 `.ps1` 스크립트를 작성해보았으나 경로 문제, 환경 변수 주입 문제, JMeter 실행 방식 차이로 인해 유지보수 리스크가 크다고 판단

결과적으로 **CI 기준으로 작성된 자동화 스크립트는 정상 동작** 했지만 **로컬 환경에서는 "Python 실행 방식 차이"로 인해 전체 실행 흐름이 안정적으로 동작하지 않는 상황.**

---

## 문제 발생 조건

- CI 환경(Jenkins 노드)에서는 Python 실행 명령어가 명확히 존재
- 로컬 환경에서는 OS 및 설치 방식에 따라 Python 호출 방식이 상이
  - `python`
  - `python3`
  - `py`
- Git Bash 환경에서는 가상환경 활성화 여부와 관계없이 `python` 명령어가 PATH에 존재하지 않을 수 있음
- PowerShell 환경은 bash 기반 스크립트 구조와 실행 방식이 상이
- bash 스크립트 내부에서 Python 실행 명령어를 `python`으로 고정한 것이 문제
- JMeter 실행(`run_jmeter.sh`)은 정상이나, 결과 분석 단계(`analyze_result.py`)에서 환경 의존성으로 실패

즉 **크로스 플랫폼을 고려하지 않은 실행 진입점(entry point) 가정**이 문제의 핵심 원인.

---

## 해결 전 접근 (시도)

### PowerShell 전용 스크립트 작성 시도

**의도**  
Windows 환경에 맞게 `.ps1` 스크립트를 별도로 작성하여 로컬 실행 문제를 해결하려고 시도.

**문제점**

- PowerShell 환경으로 전환해도 Python 실행 방식 차이로 인한 실행 실패가 완전히 해결되지 않음
- CI와 로컬 스크립트 구조가 분리됨
- 변수 전달 방식 및 경로 처리 방식 차이
- JMeter 실행 방식 차이로 디버깅 비용 증가
- 유지보수 관점에서 리스크가 크다고 판단

결과적으로 PowerShell 전용 스크립트는 **근본적인 실행 안정성 문제를 해결하지 못했고**, 동시에 유지보수 비용을 증가시키는 방향이라고 판단하여 채택하지 않음.


---

## 해결 후 코드
### 전략 전환: Python 실행 명령어 자동 감지

### 의도

문제의 원인이 Python 설치 여부가 아니라 **환경마다 다른 Python 실행 진입점에 있음을 인식**.

이에 따라
- 환경별 스크립트를 분리 폐기
- 실행 시점에 사용 가능한 Python 명령어를 자동으로 탐지해 하나의 실행 흐름으로 통합하는 전략을 선택.

### Python 실행 명령어 자동 감지 로직

```bash
if command -v python &> /dev/null; then
  PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
elif command -v py &> /dev/null; then
  PYTHON_CMD="py"
else
  echo "[ERROR] Python not found in PATH"
  PYTHON_CMD="winpty python"
fi
```

## 실행 흐름 안정화

- Python 분석 스크립트 실행 시 `${PYTHON_CMD}` 사용
- 일부 분석 단계 실패 시에도 전체 실행 흐름을 유지하기 위해 `|| true` 사용
- 로컬 환경에서는 로그 확인 목적
- CI 환경에서는 후속 단계까지 파이프라인 정상 진행 가능

---

## 결과 검증

- Jenkins CI 환경 기존 동작에 영향 없음
- 로컬 환경에서 단일 스크립트로 다음 작업 수행 가능
  - JMeter 성능 테스트 실행
  - 결과 분석 및 SLA 검증
- 팀원별 OS / Python 설치 방식 차이로 인한 실행 실패 제거
- PowerShell 전용 스크립트 의존성 제거로 유지보수성 향상

---

## ✅ 최종 정리

- CI 기준으로 작성된 자동화 스크립트는 로컬 환경에서 동일한 실행 진입점을 보장하지 않음.
- 크로스 플랫폼 자동화에서는 **“설치 여부”보다 “실행 방식 차이”가 더 큰 리스크 요인이 될 수 있음.**
- 환경별 스크립트를 늘리기보다 실행 시점에 환경 차이를 흡수하는 설계가 유지보수에 유리.
- 자동화 스크립트는 **CI와 로컬 환경을 모두 고려한 실행 흐름 설계가 필수적**.
