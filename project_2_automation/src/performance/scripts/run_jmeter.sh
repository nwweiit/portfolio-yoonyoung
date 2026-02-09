#!/bin/bash
set -e


if [ "$1" = "--glob" ]; then
  PATTERN="$2"
  SUFFIX="$3"

  if [ -z "$PATTERN" ] || [ -z "$SUFFIX" ]; then
    echo "Usage: bash run_jmeter.sh --glob '<pattern>' <suffix>"
    exit 1
  fi

  if [ -f ".env" ]; then
    set -a
    source .env
    set +a
  else
    echo "[INFO] .env not found, using environment variables"
  fi

  export PYTHONPATH="$(pwd)"

  mapfile -t JMX_FILES < <(find performance/jmx -type f -name "$PATTERN" | sort)

  for JMX_PATH in "${JMX_FILES[@]}"; do
    REL_PATH="${JMX_PATH#performance/jmx/}"
    JMX_NAME="${REL_PATH%.jmx}"

    SAFE_NAME="${JMX_NAME//\//_}"
    RESULT_JTL="performance/result/${SAFE_NAME}${SUFFIX}.jtl"
    REPORT_DIR="performance/report/${SAFE_NAME}${SUFFIX}"

    rm -rf "$RESULT_JTL" "$REPORT_DIR"

    echo "[INFO] Running JMeter: ${SAFE_NAME}${SUFFIX}"

    if [[ "$JMETER_BIN" == *.bat ]]; then
      echo "[INFO] Detected Windows JMeter (.bat)"
      if ! cmd.exe /c "$JMETER_BIN" -n \
        -t "performance/jmx/${JMX_NAME}.jmx" \
        -l "$RESULT_JTL" \
        -e -o "$REPORT_DIR" \
        -JECI_ACCESS_TOKEN="$ECI_ACCESS_TOKEN" \
        -JBUILD_ID="$BUILD_ID"
      then
        echo "❌ JMX FAILED (SKIPPED): ${JMX_NAME}"
      fi
    else
      echo "[INFO] Detected Unix-like JMeter"
      if ! "$JMETER_BIN" -n \
        -t "performance/jmx/${JMX_NAME}.jmx" \
        -l "$RESULT_JTL" \
        -e -o "$REPORT_DIR" \
        -JECI_ACCESS_TOKEN="$ECI_ACCESS_TOKEN" \
        -JBUILD_ID="$BUILD_ID"
      then
        echo "❌ JMX FAILED (SKIPPED): ${JMX_NAME}"
      fi
    fi
  done

  exit 0
fi


##수동 사용용도로 남겨둠

if [ -z "$1" ]; then
  echo "Usage: bash run_jmeter.sh <jmx_name1> [jmx_name2 ...] <suffix>"
  exit 1
fi

SUFFIX="${@: -1}"
JMX_NAMES=("${@:1:$#-1}")

if [ -f ".env" ]; then
  set -a
  source .env
  set +a
else
  echo "[INFO] .env not found, using environment variables"
fi

export PYTHONPATH="$(pwd)"

for JMX_NAME in "${JMX_NAMES[@]}"; do
  SAFE_NAME="${JMX_NAME//\//_}"

  RESULT_JTL="performance/result/${SAFE_NAME}${SUFFIX}.jtl"
  REPORT_DIR="performance/report/${SAFE_NAME}${SUFFIX}"

  rm -rf "$RESULT_JTL"
  rm -rf "$REPORT_DIR"

  echo "[INFO] Running JMeter: ${SAFE_NAME}${SUFFIX}"

  if [[ "$JMETER_BIN" == *.bat ]]; then
    echo "[INFO] Detected Windows JMeter (.bat)"
    cmd.exe /c "$JMETER_BIN" -n \
      -t "performance/jmx/${JMX_NAME}.jmx" \
      -l "$RESULT_JTL" \
      -e -o "$REPORT_DIR" \
      -JECI_ACCESS_TOKEN="$ECI_ACCESS_TOKEN" \
      -JBUILD_ID="$BUILD_ID"
  else
    echo "[INFO] Detected Unix-like JMeter"
    "$JMETER_BIN" -n \
      -t "performance/jmx/${JMX_NAME}.jmx" \
      -l "$RESULT_JTL" \
      -e -o "$REPORT_DIR" \
      -JECI_ACCESS_TOKEN="$ECI_ACCESS_TOKEN" \
      -JBUILD_ID="$BUILD_ID"
  fi
done
