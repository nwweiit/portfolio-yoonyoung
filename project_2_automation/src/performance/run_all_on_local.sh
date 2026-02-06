#!/bin/bash
set -e


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

echo "[INFO] Using Python command: $PYTHON_CMD"

TOTAL_START=$(date +%s)
TOTAL_START_HUMAN=$(date "+%Y-%m-%d %H:%M:%S")

echo "===================================="
echo "🚀 PERFORMANCE TEST START"
echo "Start Time: $TOTAL_START_HUMAN"
echo "===================================="


LOAD_START=$(date +%s)
echo "=== RUN LOAD (INITIAL) ==="
bash performance/scripts/run_jmeter.sh --glob "*_load.jmx" _local
LOAD_END=$(date +%s)



SPIKE_START=$(date +%s)
echo "=== RUN SPIKE ==="
bash performance/scripts/run_jmeter.sh --glob "*_spike.jmx" _local
SPIKE_END=$(date +%s)



RECOVERY_START=$(date +%s)
echo "=== RUN LOAD (RECOVERY) ==="
bash performance/scripts/run_jmeter.sh --glob "*_load.jmx" _local_recovery
RECOVERY_END=$(date +%s)


SOAK_START=$(date +%s)
echo "=== RUN SOAK ==="
bash performance/scripts/run_jmeter.sh --glob "*_soak.jmx" _local
SOAK_END=$(date +%s)


echo "=== RUN CLEANUP (SAFETY NET) ==="
$PYTHON_CMD performance/cleanup/cleanup_entry.py || true


echo "=== VERIFY NON-GET (ETC) ==="
export REQUIRE_GET=false

shopt -s nullglob
FILES=(performance/result/*_nonget_*.jtl)

if [ ${#FILES[@]} -eq 0 ]; then
  echo "[SKIP] No NON-GET test results found"
else
  for f in "${FILES[@]}"; do
    $PYTHON_CMD performance/scripts/analyze_result.py "$f" || true
  done
fi

echo "=== VERIFY LOAD (GET) ==="
export REQUIRE_GET=true

for f in performance/result/*_load_local.jtl performance/result/*_load_local_recovery.jtl; do
  [ -f "$f" ] || continue

  echo "------------------------------------"
  echo "▶ VERIFY FILE: $(basename "$f")"
  echo "------------------------------------"

  $PYTHON_CMD performance/scripts/analyze_result.py "$f" || true
done


echo "=== VERIFY SPIKE (GET) ==="
for f in performance/result/*_spike_local.jtl; do
  [ -f "$f" ] || continue

  echo "------------------------------------"
  echo "▶ VERIFY SPIKE FILE: $(basename "$f")"
  echo "------------------------------------"

  $PYTHON_CMD performance/scripts/analyze_spike_result.py "$f" || true
done



echo "=== VERIFY SOAK ==="
for f in performance/result/*_soak_local.jtl; do
  [ -f "$f" ] || continue

  echo "------------------------------------"
  echo "▶ VERIFY SOAK FILE: $(basename "$f")"
  echo "------------------------------------"

  $PYTHON_CMD performance/scripts/analyze_soak_result.py "$f" || true
done



TOTAL_END=$(date +%s)
TOTAL_END_HUMAN=$(date "+%Y-%m-%d %H:%M:%S")

echo "===================================="
echo "⏱ TIME SUMMARY"

printf "LOAD Time     : %02d:%02d:%02d\n" \
  $(((LOAD_END-LOAD_START)/3600)) \
  $((((LOAD_END-LOAD_START)%3600)/60)) \
  $(((LOAD_END-LOAD_START)%60))

printf "SPIKE Time    : %02d:%02d:%02d\n" \
  $(((SPIKE_END-SPIKE_START)/3600)) \
  $((((SPIKE_END-SPIKE_START)%3600)/60)) \
  $(((SPIKE_END-SPIKE_START)%60))

printf "RECOVERY Time : %02d:%02d:%02d\n" \
  $(((RECOVERY_END-RECOVERY_START)/3600)) \
  $((((RECOVERY_END-RECOVERY_START)%3600)/60)) \
  $(((RECOVERY_END-RECOVERY_START)%60))

printf "SOAK Time     : %02d:%02d:%02d\n" \
  $(((SOAK_END-SOAK_START)/3600)) \
  $((((SOAK_END-SOAK_START)%3600)/60)) \
  $(((SOAK_END-SOAK_START)%60))

echo "------------------------------------"

printf "TOTAL Time    : %02d:%02d:%02d\n" \
  $(((TOTAL_END-TOTAL_START)/3600)) \
  $((((TOTAL_END-TOTAL_START)%3600)/60)) \
  $(((TOTAL_END-TOTAL_START)%60))

echo "End Time: $TOTAL_END_HUMAN"
echo "===================================="
