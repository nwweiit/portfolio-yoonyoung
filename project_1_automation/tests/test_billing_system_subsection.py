import pytest
from src.pages.billing_page import BillingPage, PaymentMethodsPage, DanalCardPage, UsagePage


@pytest.fixture
def usage_page_loaded(logged_in_driver):
    driver = logged_in_driver
    driver.get("https://qaproject.elice.io/cloud/usage")
    return UsagePage(driver)


def test_bu_003_click_usage_history(logged_in_driver):
    driver = logged_in_driver
    usage_page = UsagePage(driver)

    usage_page.usage_history_click()

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])

    assert usage_page.is_usage_history_page(), "❌ Usage History 페이지로 이동 실패"


def test_bu_004_click_ml_api(usage_page_loaded):
    page = usage_page_loaded
    page.click_ml_api_tab()
    assert page.is_ml_api_selected()

def test_bu_005_click_severless_status(usage_page_loaded):
    page = usage_page_loaded
    page.click_serverless_status()
    assert page.is_serverless_status_page()


def test_bu_006_click_api_key_manage(usage_page_loaded):
    page = usage_page_loaded
    page.click_api_key_manage()
    assert page.is_api_key_manage_page()
