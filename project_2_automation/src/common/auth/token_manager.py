import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from src.pages.login_page import LoginPage
from src.utils.exceptions import UiCredentialNotProvidedError, UiTokenExtractionError
import logging


logger = logging.getLogger(__name__)


class UiTokenManager:
    MAX_SESSION_RETRY = 5
    MAX_CLICK_RETRY = 10  

    def __init__(self):
        load_dotenv()
        self.username = os.getenv("ECI_USERNAME")
        self.password = os.getenv("ECI_PASSWORD")

        if not self.username or not self.password:
            raise UiCredentialNotProvidedError("ECI_USERNAME / ECI_PASSWORD 없음")


    def _create_driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        return webdriver.Chrome(options=options)
    

    def _try_login_once(self, session_idx: int) -> str:
        driver = self._create_driver()

        try:
            driver.get("https://example/eci/home")

            logger.info("[SESSION %d] Initial login input", session_idx)
            LoginPage(driver).login(self.username, self.password)


            for click_idx in range(1, self.MAX_CLICK_RETRY + 1):
                try:
                    logger.info(
                        "[SESSION %d] Login button click retry (%d/%d)",
                        session_idx, click_idx, self.MAX_CLICK_RETRY)

                    WebDriverWait(driver, 5).until(
                        lambda d: d.execute_script(
                            "return window.localStorage.getItem('accessToken') !== null;"))

                    token = driver.execute_script(
                        "return window.localStorage.getItem('accessToken');")

                    if token:
                        logger.info(
                            "[SESSION %d] Token extracted successfully",session_idx)
                        return token

                except Exception as e:
                    logger.warning(
                        "[SESSION %d] Login button retry failed (%d/%d): %s",
                        session_idx, click_idx, self.MAX_CLICK_RETRY, e)

            raise UiTokenExtractionError(
                f"Login button retry exceeded ({self.MAX_CLICK_RETRY})")

        finally:
            driver.quit()


    def login_and_get_token(self) -> str:
        last_exception = None

        for session_idx in range(1, self.MAX_SESSION_RETRY + 1):
            try:
                logger.info(
                    "=== UI TOKEN SESSION RETRY %d/%d ===",session_idx,self.MAX_SESSION_RETRY)

                return self._try_login_once(session_idx)

            except Exception as e:
                last_exception = e
                logger.error("[SESSION %d] Session failed: %s",session_idx,e)

        raise UiTokenExtractionError(
            f"토큰 발급 실패 (세션 재시도 {self.MAX_SESSION_RETRY}회)"
        ) from last_exception
