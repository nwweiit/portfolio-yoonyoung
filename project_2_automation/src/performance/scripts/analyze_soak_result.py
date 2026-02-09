import csv
import sys
import logging
from statistics import mean, pstdev

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


STDEV_LIMIT = 500         
ERROR_RATE_LIMIT = 0.01  
P95_LIMIT = 2000          


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


def verify_jtl(jtl_path: str) -> None:
    elapsed_times = []
    total = 0
    failed = 0

    with open(jtl_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1

            success = row["success"].lower() == "true"
            if not success:
                failed += 1

            elapsed_times.append(int(row["elapsed"]))

    if total == 0:
        raise AssertionError("JTL file is empty")

    error_rate = failed / total
    avg = mean(elapsed_times)
    p95 = percentile(elapsed_times, 95)
    stdev = pstdev(elapsed_times)

    logger.info("====== SOAK TEST METRICS ======")
    logger.info("Total Requests        : %d", total)
    logger.info("Average Response(ms)  : %.2f", avg)
    logger.info("P95 Response(ms)      : %.2f (limit: %d)", p95, P95_LIMIT)
    logger.info("STDEV(ms)             : %.2f (limit: %d)", stdev, STDEV_LIMIT)
    logger.info("Error Rate            : %.4f (limit: %.2f)", error_rate, ERROR_RATE_LIMIT)
    logger.info("================================")


    assert error_rate < ERROR_RATE_LIMIT, (
        f"Error rate too high: {error_rate:.4f}")

    assert stdev < STDEV_LIMIT, (
        f"Response time variance too high (STDEV): {stdev:.2f}ms")

    assert p95 < P95_LIMIT, (
        f"P95 response time too high: {p95:.2f}ms")

    logger.info("✅ SOAK TEST PASSED")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python analyze_soak_result.py <result.jtl>")
        sys.exit(2)

    try:
        verify_jtl(sys.argv[1])
        sys.exit(0)
    except AssertionError as e:
        logger.error("❌ SOAK TEST FAILED: %s", e)
        sys.exit(1)
