import csv
import sys
import os
import logging
from statistics import mean


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


ERROR_RATE_THRESHOLD = 0.02
MAX_MS_THRESHOLD = 5000
TOTAL_TPS_THRESHOLD = 10      ##로그 출력용 기준값
GET_TPS_THRESHOLD = 50

REQUIRE_GET = os.getenv("REQUIRE_GET", "false").lower() == "true"


def percentile(values, percent):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * (percent / 100)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[int(k)]
    return values[f] + (values[c] - values[f]) * (k - f)


def is_empty_list_response(response: str) -> bool:
    if not response:
        return False
    response = response.strip()
    return response in ("[]", '{"items":[]}', '{"items": []}')


def verify_jtl(jtl_path: str) -> None:

    elapsed_times = []
    timestamps = []
    total = 0
    failed = 0
    empty_count = 0
    get_count = 0

    with open(jtl_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1

            success = row["success"].lower() == "true"
            if not success:
                failed += 1

            elapsed_times.append(int(row["elapsed"]))
            timestamps.append(int(row["timeStamp"]))

            label = row.get("label", "")
            if label.startswith("GET_"):
                get_count += 1

            response = row.get("responseData", "") or row.get("responseMessage", "")
            if is_empty_list_response(response):
                empty_count += 1

    if total == 0:
        raise AssertionError("JTL file is empty")

    error_rate = failed / total
    avg = mean(elapsed_times)
    p95 = percentile(elapsed_times, 95)
    max_v = max(elapsed_times)

    duration_sec = (max(timestamps) - min(timestamps)) / 1000
    total_tps = total / duration_sec if duration_sec > 0 else 0
    empty_rate = (empty_count / total) * 100

    get_tps = (
        get_count / duration_sec
        if REQUIRE_GET and duration_sec > 0
        else None
    )

    logger.info("====== Performance Metrics ======")
    logger.info("Total Requests        : %d", total)
    logger.info(
        "Total TPS             : %.2f (threshold: %d)",
        total_tps,
        TOTAL_TPS_THRESHOLD,
    )
    logger.info("Average Response(ms)  : %.2f", avg)
    logger.info("P95 Response(ms)      : %.2f", p95)
    logger.info("Max Response(ms)      : %.2f", max_v)
    logger.info("Error Rate            : %.4f", error_rate)
    logger.info(
        "Empty Response Rate   : %.2f%% (%d/%d)",
        empty_rate,
        empty_count,
        total,
    )

    if REQUIRE_GET:
        logger.info("GET Requests          : %d", get_count)
        logger.info(
            "GET TPS               : %.2f (threshold: %d)",
            get_tps,
            GET_TPS_THRESHOLD,
        )

    logger.info("================================")


    assert error_rate < ERROR_RATE_THRESHOLD, f"Error rate too high: {error_rate:.4f}"
    assert max_v < MAX_MS_THRESHOLD, f"Max response time too high: {max_v:.2f}ms"

    if REQUIRE_GET:
        if get_count == 0:
            raise AssertionError("GET validation enabled, but no GET requests found")
        assert get_tps >= GET_TPS_THRESHOLD, f"GET TPS too low: {get_tps:.2f}"

    logger.info("✅ Performance SLA PASSED")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python verify_jtl.py <result.jtl>")
        sys.exit(2)

    try:
        verify_jtl(sys.argv[1])
        sys.exit(0)
    except AssertionError as e:
        logger.error("❌ Performance SLA FAILED: %s", e)
        sys.exit(1)
