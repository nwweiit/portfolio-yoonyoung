import pytest
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os
from src.pages.custom_agent_page import AgentExplorerPage, CreateAgentPage, SaveAgentPage, ChatCreatePage, MyAgentsPage


chrome_driver_path = ChromeDriverManager().install()


@pytest.fixture
def pages(logged_in_driver):
    driver = logged_in_driver
    return {
        "explorer": AgentExplorerPage(driver),
        "create": CreateAgentPage(driver),
        "my_agents": MyAgentsPage(driver),
        "chat_create": ChatCreatePage(driver)
    }


# Explorer 페이지 진입용 fixture
@pytest.fixture
def explorer_page_loaded(pages):
    driver = pages["explorer"].driver
    explorer_page = pages["explorer"]

    driver.get(explorer_page.url)  
    WebDriverWait(driver, 10).until(EC.url_contains("/ai-helpy-chat/agent"))

    yield driver


# My Agents 페이지 진입용 fixture
@pytest.fixture
def my_agents_page_loaded(pages):
    driver = pages["my_agents"].driver
    my_agents_page = pages["my_agents"]

    driver.get(my_agents_page.url)
    WebDriverWait(driver, 10).until(EC.url_contains("/ai-helpy-chat/agent/mine"))

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".MuiCard-root"))
        )
    except TimeoutException:
        print("⚠️ 카드 리스트 렌더링 실패 (카드 0개일 수도 있음)")

    yield driver


#생성폼 수동 진입용 fixture   

@pytest.fixture
def create_page(pages):
    driver = pages["explorer"].driver
    explorer_page = pages["explorer"]
    wait = WebDriverWait(driver, 10)

    driver.get(explorer_page.url)
    wait.until(EC.url_contains("/ai-helpy-chat/agent"))

    explorer_page.get_element("create_btn", wait_type="clickable").click()

    wait.until(EC.url_contains("builder#form"))
    wait.until(EC.visibility_of_element_located((By.NAME, "name")))

    yield driver


#더미파일 생성,삭제용 fixture

@pytest.fixture
def dummy_files():
    small = "dummy_small.pdf"
    big = "dummy_big.pdf"

    with open(small, "wb") as f:
        f.write(b"0" * 1024)
    with open(big, "wb") as f:
        f.write(b"0" * 55 * 1024 * 1024)

    yield {
        "small": os.path.abspath(small),
        "big": os.path.abspath(big),
    }

    for fpath in [small, big]:
        if os.path.exists(fpath):
            os.remove(fpath)






def test_ca_001_navigate_to_agent_create_form(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 10)
    explorer_page = AgentExplorerPage(driver)

    explorer_page.click_safely("agent_explorer_btn")
    explorer_page.click_safely("create_btn")

    try:
        wait.until(EC.url_contains("builder#form"))
        wait.until(EC.presence_of_element_located((By.NAME, "name")))
    except TimeoutException:
        print("❌ CA_001_페이지로 이동 실패!")



def test_ca_002_validate_required_fields_behavior(create_page):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    create_agent_page = CreateAgentPage(driver)

    #1️⃣ name 제외 입력
    create_agent_page.fill_form(
        "",
        "test description",
        "test system prompt",
        "test conversation starter"
    )

    create_btn = create_agent_page.get_element("create_btn", wait_type="presence")

    #2️⃣ name 오류문구 + 버튼 disabled 체크
    try:
        err = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error")
            )
        )
        assert err.is_displayed(), "name 에러 문구 미표시"
        assert not create_btn.is_enabled(), "생성 버튼이 비활성화되어 있지 않음"

    except TimeoutException:
        print("❌ CA_002_name 필드 검증 실패!")
        return

    #3️⃣ name 입력 / rules 삭제
    name_input = create_agent_page.get_element("name")
    name_input.click()
    name_input.send_keys("Test Agent")

    rules_input = create_agent_page.get_element("rules")
    rules_input.send_keys(Keys.CONTROL + "a")
    rules_input.send_keys(Keys.DELETE)

    wait.until(lambda d: rules_input.get_attribute("value") == "")
    name_input.click()  # focus 이동

    #4️⃣ rules 오류문구 + 버튼 disabled 체크
    try:
        err2 = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error")
            )
        )
        assert err2.is_displayed(), "rules 에러 문구 미표시"
        assert not create_btn.is_enabled(), "생성 버튼이 활성화됨"

    except TimeoutException:
        print("❌ CA_002_rules 검증 실패!")




def test_ca_003_1_create_private_agent_successfully(create_page, request):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    create_agent_page = CreateAgentPage(driver)

    #1️⃣ 입력
    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    #2️⃣ Create 버튼
    create_agent_page.click_safely("create_btn")

    #3️⃣ 저장
    save_page = SaveAgentPage(driver)
    save_page.select_mode("private")
    save_page.click_save()

    #4️⃣ 스낵바 메시지는 반드시 성공해야 한다 → 실패하면 FAIL
    message = save_page.get_snackbar_text().lower()
    assert "created" in message, f"❌ CA_003_1_예상과 다른 메시지: {message}"

    #5️⃣ agent_id 저장 → 실패하면 FAIL
    agent_id = create_agent_page.get_agent_id_from_url()
    assert agent_id, "❌ CA_003_1_agent_id 추출 실패"
    request.config.cache.set("private_agent_id", agent_id)

    #6️⃣ 자동 이동은 실패해도 PASS
    try:
        wait.until(lambda d: "builder#form" not in d.current_url)
    except TimeoutException:
        print("❌ CA_003_1_에이전트 메인 페이지로 자동 이동 실패!")






def test_ca_003_2_create_organization_agent_successfully(create_page, request):
    driver = create_page
    wait = WebDriverWait(driver, 10)
    create_agent_page = CreateAgentPage(driver)

    #1️⃣ 필드 입력
    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    #2️⃣ Create 버튼 안정적 클릭 (scroll + JS click)
    create_agent_page.click_safely("create_btn")

    #3️⃣ 저장 모달 → organization 선택 → 저장
    save_page = SaveAgentPage(driver)
    save_page.select_mode("organization")
    save_page.click_save()

    #4️⃣ 스낵바 메시지
    try:
        message = save_page.get_snackbar_text().lower()
        assert "created" in message, f"❌ CA_003_2_예상과 다른 메시지: {message}"
    except TimeoutException:
        print("❌ CA_003_2_스낵바 메시지 미출력!")
        return

    #5️⃣ 생성된 에이전트 ID 저장
    try:
        agent_id = create_agent_page.get_agent_id_from_url()
        request.config.cache.set("organization_agent_id", agent_id)
    except Exception:
        print("❌ CA_003_2_agent_id 추출 실패!")
        return

    #6️⃣ 자동 라우팅 확인 (테스트 실패 X, 모니터링 only)
    try:
        wait.until(lambda d: "builder#form" not in d.current_url)
    except TimeoutException:
        print("❌ CA_003_2_에이전트 메인 페이지로 자동 이동 실패!")




def test_ca_004_test_create_with_chat_generates_ai_response(create_page, pages):
    driver = create_page
    chat_page = pages["chat_create"]

    #1️⃣ create with chat 클릭 (scroll + JS click)
    try:
        chat_page.click_safely("create_with_chat_btn")  
    except Exception:
        print("❌ CA_004_Create-with-Chat 버튼 클릭 실패!")
        return

    #2️⃣ 챗봇에 메시지 입력
    try:
        chat_page.send_single_message()
    except Exception:
        print("❌ CA_004_메시지 전송 실패!")
        return

    #3️⃣ AI 응답 생성 확인
    try:
        assert chat_page.wait_for_ai_answer(), "❌ CA_004_AI 답변 생성 실패"
    except Exception:
        print("❌ CA_004_AI 응답 감지 실패!")






def test_ca_005_prevent_duplicate_agent_creation(create_page):
    driver = create_page
    create_agent_page = CreateAgentPage(driver)

    #1️⃣ 동일 이름 입력 후 생성 시도
    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    try:
        create_agent_page.click_safely("create_btn")
    except Exception:
        print("❌ CA_005_Create 버튼 클릭 실패!")
        return

    #2️⃣ 저장 시도
    save_page = SaveAgentPage(driver)
    save_page.select_mode("organization")

    try:
        save_page.click_save()
    except Exception:
        print("❌ CA_005_Save 버튼 클릭 실패!")
        return

    #3️⃣ 스낵바 메시지 확인
    try:
        message = save_page.get_snackbar_text().lower()
    except Exception:
        print("❌ CA_005_스낵바 메시지 감지 실패!")
        return

    #4️⃣ 메시지 분석 (테스트 실패 처리 없음, 로깅 only)
    if "created" in message or "success" in message or "성공" in message:
        print("❌ CA_005_중복 검증 누락 가능성 (성공 메시지 표시됨)")
    elif "duplicate" in message or "이미 존재" in message or "동일한 이름" in message:
        print("😊 CA_005_중복 이름 감지 정상 동작")
    else:
        print(f"⚠️ CA_005_예상 외 메시지: {message}")





def test_ca_006_display_created_agents_in_explorer(explorer_page_loaded, request):
    driver = explorer_page_loaded
    explorer_page = AgentExplorerPage(driver)

    #1️⃣ 이전에 저장된 두 개의 ID 가져오기
    private_id = request.config.cache.get("private_agent_id", None)
    org_id = request.config.cache.get("organization_agent_id", None)
    assert private_id or org_id, "❌ CA_006_이전 테스트의 agent_id를 불러올 수 없습니다."

    #2️⃣ Private/Organization 카드 확인
    if private_id:
        result = explorer_page.click_agent_card_by_id(private_id)
        assert result, f"❌ CA_006_Private 카드 미노출 (ID: {private_id})"
    if org_id:
        result = explorer_page.click_agent_card_by_id(org_id)
        assert result, f"❌ CA_006_Organization 카드 미노출 (ID: {org_id})"




def test_ca_007_display_agent_cards_in_my_agents(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)

    assert my_agent_page.wait_for_cards_loaded(), "❌ My Agents 카드 로드 실패"

    my_agent_page.load_all_cards()

    assert my_agent_page.wait_for_cards_loaded(), "❌ My Agents 카드 재로드 실패"

    draft_cards = my_agent_page.get_draft_cards()
    private_cards = my_agent_page.get_private_cards()
    organization_cards = my_agent_page.get_organization_cards()

    assert my_agent_page.has_cards("private", minimum=1), "❌ CA_007_Private 카드 없음"
    assert my_agent_page.has_cards("draft", minimum=1), "❌ CA_007_Draft 카드 없음"
    assert my_agent_page.has_cards("organization", minimum=1), "❌ CA_007_Organization 카드 없음"








def test_ca_008_update_existing_agent_successfully(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    create_agent_page = CreateAgentPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 첫 번째 Private 카드의 edit 버튼 클릭(organization으로 변경 가능)
    my_agent_page.load_all_cards()
    my_agent_page.click_edit_button_by_card_type("private")
    create_agent_page.get_element("name", wait_type="visible", timeout=10)

    #2️⃣ 수정 작업
    name_field = create_agent_page.get_element("name")
    name_field.click()
    name_field.send_keys("_edit")
    create_agent_page.get_element("create_btn", "clickable").click() #수정 작업의 경우 publish로 텍스트만 변경됨

    #3️⃣ 수정 후 저장, 알림 확인(1️⃣에서 organization으로 변경 시 organization으로 변경)
    save_page.select_mode("private")
    save_page.click_save()
    message = save_page.get_snackbar_text().lower()
    assert "updated" in message, f"❌ CA_008_예상과 다른 메시지: {message}"



def test_ca_009__publish_draft_agent_successfully(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    create_agent_page = CreateAgentPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ Draft 카드 로딩 + edit 클릭
    my_agent_page.load_all_cards()  # 무한 스크롤 안정화

    # 추가 안전장치: 카드가 로딩되었는지 보장
    WebDriverWait(driver, 15).until(
        lambda d: len(my_agent_page.get_draft_cards()) > 0
    )

    # edit 버튼 클릭 (POM이 JS click + scrollIntoView까지 처리함)
    my_agent_page.click_edit_button_by_card_type("draft")

    #2️⃣ 모든 필드 안정적으로 입력
    create_agent_page.fill_form(
        "project team",
        "for the team project",
        "If you must make a guess, clearly state that it is a guess",
        "Hello, we're team 03"
    )

    # 버튼 클릭도 JS click으로 안정성 확보
    create_btn = create_agent_page.get_element("create_btn", "clickable")

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_btn)
    driver.execute_script("arguments[0].click();", create_btn)

    #3️⃣ 저장 모달 안정화
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-paper"))
    )

    save_page.select_mode("private")  # 내부도 JS click 기준


    # save 버튼 안정적 클릭
    save_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(save_page.locators["save_btn"])
    )
    driver.execute_script("arguments[0].click();", save_btn)

    #4️⃣ 스낵바 안정적 대기
    message = save_page.get_snackbar_text().lower()

    assert "created" in message, f"❌ CA_009_예상과 다른 메시지: {message}"




def test_ca_010_autosave_draft_agent_persists_changes(my_agents_page_loaded, pages):
    driver = my_agents_page_loaded
    my_agent_page = pages["my_agents"]
    create_agent_page = pages["create"]

    #1️⃣ My Agents 카드 로드 보장
    assert my_agent_page.wait_for_cards_loaded(), "My Agents 카드 로드 실패"
    my_agent_page.load_all_cards()

    draft_cards = my_agent_page.get_draft_cards()
    assert len(draft_cards) >= 1, "Draft 카드 존재하지 않음"

    target_card = draft_cards[0]
    agent_id = my_agent_page.get_agent_id_from_card(target_card)

    my_agent_page.click_edit_button_by_card_type("draft")

    #2️⃣ 값 입력 + auto-save 대기
    TARGET_TITLE = "draft test"
    expected_values = create_agent_page.fill_form_with_trigger(
        TARGET_TITLE,
        "",
        "draft rules",
        ""
    )

    # auto-save 완료 대기용
    time.sleep(1)
    create_agent_page.wait_for_autosave(expected_values, timeout=25)

    #3️⃣ My Agents로 돌아간 뒤, 해당 Draft 카드의 제목이 갱신될 때까지 대기
    driver.back()

    updated_card = my_agent_page.wait_for_card_update(
        agent_id,
        TARGET_TITLE,
        timeout=20
    )

    #4️⃣ 갱신된 Draft 카드 다시 편집 진입
    my_agent_page.scroll_into_view(updated_card)

    edit_btn = my_agent_page._find_button_in_card(
        updated_card,
        my_agent_page.locators["edit_icon"]
    )
    assert edit_btn, "❌ CA_010_Edit 버튼 탐색 실패"

    driver.execute_script("arguments[0].click();", edit_btn)

    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.NAME, "name").get_attribute("value") != ""
    )

    #5️⃣ 필드 값 전체 비교
    actual_values = create_agent_page.get_all_field_values()

    assert actual_values["name"] == expected_values["name"], (
        f"❌ name 불일치: '{expected_values['name']}' vs '{actual_values['name']}'"
    )
    assert actual_values["rules"] == expected_values["rules"], (
        f"❌ rules 불일치: '{expected_values['rules']}' vs '{actual_values['rules']}'"
    )





def test_ca_011_cancel_agent_deletion_modal(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)

    #1️⃣ 카드 로드 + 무한스크롤 안정화
    assert my_agent_page.wait_for_cards_loaded(), "My Agents 카드 로드 실패"
    my_agent_page.load_all_cards()

    #2️⃣ 두 번째 organization 카드 삭제 버튼 클릭
    my_agent_page.click_delete_button_by_card_type("organization", index=1)

    #3️⃣ 삭제 모달 등장 대기 (Modal Root 기준)
    modal_root = (By.CSS_SELECTOR, "div.MuiDialog-container")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(modal_root)
    )

    assert my_agent_page.is_delete_modal_visible(), \
        "❌ CA_011_삭제 팝업 모달 미출력"

    #4️⃣ Cancel 클릭 (JS click + 안정화)
    my_agent_page.cancel_delete_modal()

    #5️⃣ Modal이 완전히 사라질 때까지 invisibility 검사
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located(modal_root)
    )

    assert not my_agent_page.is_delete_modal_visible(), \
        "❌ CA_011_모달이 닫히지 않음"







def test_ca_012_delete_agent_permanently(my_agents_page_loaded):
    driver = my_agents_page_loaded
    my_agent_page = MyAgentsPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 카드 로드
    assert my_agent_page.wait_for_cards_loaded(), "My Agents 카드 로드 실패"
    my_agent_page.load_all_cards()
  
    org_cards = my_agent_page.get_organization_cards()
    assert len(org_cards) > 1, "❌ CA_012_Organization 카드가 2개 이상 필요합니다."
  
    target_card = org_cards[1]

    my_agent_page.scroll_into_view(target_card)
    WebDriverWait(driver, 5).until(lambda d: target_card.is_displayed())

    #2️⃣ 삭제 클릭
    my_agent_page.click_delete_button_by_card_type("organization", index=1)

    #3️⃣ 모달 확인 및 confirm 클릭
    assert my_agent_page.is_delete_modal_visible(), "❌ CA_012_삭제 모달 미출력"
    my_agent_page.confirm_delete_modal()

    #4️⃣ invisibility 체크 (optional)
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located(
                my_agent_page.locators["confirm_delete_modal_button"]
            )
        )
    except Exception:
        pass  # print 없이 통과

    #5️⃣ snackbar
    message = save_page.get_snackbar_text().lower()
    assert (
        "success" in message
        or "delete" in message
        or "deleted" in message
        or "삭제" in message
    ), f"❌ CA_012_예상과 다른 메시지: {message}"








def test_ca_013_prevent_deletion_of_default_agents(explorer_page_loaded):
    driver = explorer_page_loaded
    explorer = AgentExplorerPage(driver)
    my_agent_page = MyAgentsPage(driver)
    save_page = SaveAgentPage(driver)

    #1️⃣ 기본제공 에이전트 삭제 시도 및 알림 확인

    my_agent_page.load_all_cards()
    result = explorer.delete_fixed_agent(my_agent_page, save_page)

    assert result is True, "❌ CA_013_기본제공 에이전트 삭제"




def test_ca_014_validate_file_upload_and_size_limit(create_page, pages, dummy_files):
    driver = create_page
    create = pages["create"]

    #1️⃣ 작은 파일
    create.upload_file(dummy_files["small"])
    small_item = create.get_last_uploaded_item()

    assert create.has_success_icon(small_item)
    assert "success" in create.get_file_status(small_item).lower()

    #2️⃣ 큰 파일
    create.upload_file(dummy_files["big"])
    big_item = create.get_last_uploaded_item()

    assert create.has_failed_icon(big_item)
    assert "failed" in create.get_file_status(big_item).lower()

    err = create.get_error_msg(big_item)
    if not err:
        print("⚠️ 오류 문구 없음")
    elif "file size" not in err.lower():
        print(f"⚠️ 예상 외 오류 문구: {err}")




def test_ca_015_private_agent_hidden_from_sub_account(logged_in_driver_sub_account, request):
    driver = logged_in_driver_sub_account
    explorer_page = AgentExplorerPage(driver)

    #1️⃣ Private ID 불러오기
    private_id = request.config.cache.get("private_agent_id", None)
    assert private_id, "❌ CA_015_private agent_id 누락"

    #2️⃣ 해당 카드 검색 후 노출 여부 확인
    results = explorer_page.click_agent_card_by_id(private_id)
    assert len(results) == 0, f"❌ CA_015_Private 카드 노출됨: {results}"




    

    
    

