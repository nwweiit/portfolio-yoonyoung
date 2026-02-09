@pytest.mark.e2e
def test_sg_010_pip_view_edit_delete(logged_in_setup):
    driver = logged_in_setup
    page = BasePage(driver)
    pip_list = PublicIpListPage(driver)
    availability_zone = "gov-central-01-a"

    page.click(locator.NETWORK_BTN)
    page.click(locator.PIP_BTN)

    initial_count = pip_list.get_row_count(locator.ALL_IP_ROWS)

    page.click(locator.CREATE_PIP_BTN)
    page.click(locator.VC_AZ_DROPDOWN)
    page.click((By.XPATH, locator.VC_AZ_OPTION_XPATH.format(availability_zone)))
    page.click(locator.SUBMIT_BTN)

    page.wait.until(lambda d: page.get_row_count(locator.ALL_IP_ROWS) > initial_count)
    created_ip = page.get_last_row_ip(locator.LAST_IP_TEXT)

    pip_list.open_detail_by_ip(created_ip)

    page.click(locator.EDIT_BTN)
    page.click(locator.CANCEL_PIP_BTN)
    page.click(locator.DELETE_BTN)
    page.click(locator.DELETE_CONFIRM_BTN)
    
    WebDriverWait(driver, 10).until(
    lambda d: "/public_ip/" not in d.current_url or d.current_url.endswith("/public_ip"))

    WebDriverWait(driver, 10).until(
    lambda _: created_ip not in pip_list.get_all_public_ips())

    print(f"삭제 대상 IP: {created_ip}")
    
    WebDriverWait(driver, 10).until(
        lambda _: created_ip not in pip_list.get_all_public_ips())
    
    assert created_ip not in pip_list.get_all_public_ips(), \
        "⛔test_sg_013_pip_view_edit_delete, UI에서 삭제 확인 실패"
    
   
@pytest.mark.e2e
def test_sg_011_vnet_create_to_delete(logged_in_setup):
    driver = logged_in_setup
    page = BasePage(driver)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_vnet_name = f"vnet-team03-e2etest-{ts}"
    edited_vnet_name = target_vnet_name + "-edited"

    page.click(locator.NT_MENU)
    page.click(locator.vnet_menu)
    page.click(locator.VNET_CREATE_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.click(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, target_vnet_name)
    page.click(locator.SUBMIT_BTN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,f"//td[normalize-space()='{target_vnet_name}']")))

    created_vnet = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,f"//td[normalize-space()='{target_vnet_name}']")))
    created_vnet.click()
    page.wait_visibility_element(locator.EDIT_BTN)
    page.click(locator.EDIT_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.click(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, edited_vnet_name)
    page.click(locator.SAVE_SUBMIT_BTN)

    WebDriverWait(driver, 10).until(
    lambda d: d.find_element(*locator.DETAIL_NAME).text.strip() == edited_vnet_name)

    page.click(locator.DELETE_BTN)
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((
        By.XPATH, "//div[@role='dialog']")))
    page.click(locator.DELETE_CONFIRM_BTN)

    WebDriverWait(driver, 10).until_not(
    EC.presence_of_element_located((By.XPATH, f"//td[normalize-space()='{edited_vnet_name}']")))
    elements = driver.find_elements(By.XPATH, f"//td[normalize-space()='{edited_vnet_name}']")
    assert len(elements) == 0, "⛔test_sg_014_vnet_create_to_delete, 가상 네트워크 삭제 실패"
  

@pytest.mark.e2e    
def test_sg_012_subnet_create_to_delete(logged_in_setup):

    driver = logged_in_setup
    page = BasePage(driver)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_vnet_name = f"vnet-team03-e2etest-{ts}"
    target_subnet_name = f"subnet-team03-e2etest-{ts}"
    edited_subnet_name = target_subnet_name + "-edited"

    page.click(locator.NT_MENU)
    page.click(locator.vnet_menu)
    page.click(locator.VNET_CREATE_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.click(locator.NAME_INPUT)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, target_vnet_name)
    page.click(locator.SUBMIT_BTN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,f"//td[normalize-space()='{target_vnet_name}']")))

    created_vnet = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,f"//td[normalize-space()='{target_vnet_name}']")))

    page.click(locator.NETWORK_BTN)
    page.click(locator.SUBNET_BTN)
    page.click(locator.SUBNET_CREATE_BTN)

    page.wait_visibility_element(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, target_subnet_name)

    WebDriverWait(driver, 5).until(lambda d: d.find_element(*locator.NAME_INPUT)
                                   .get_attribute("value") == target_subnet_name)
    combo = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located(locator.VNET_COMBO_INPUT))
    combo.click()

    driver.execute_script("arguments[0].value = '';", combo)
    combo.click()
    combo.send_keys(target_vnet_name)

    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//li[@role='option' and contains(text(), '{target_vnet_name}')]")))
    option.click()
    form_title = driver.find_element(By.XPATH, "//h6[contains(text(), '서브넷 생성')]")
    form_title.click()

    WebDriverWait(driver, 10).until(lambda d: target_vnet_name in 
                                    d.find_element(*locator.VNET_COMBO_INPUT).get_attribute("value"))
    
    page.click(locator.SUBMIT_BTN)

    success_xpath = (By.XPATH, f"//tbody/tr/td[text()='{target_subnet_name}']")
    page.wait_visibility_element(success_xpath)

    created_subnet = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH,f"//td[normalize-space()='{target_subnet_name}']")))
    created_subnet.click()
    page.wait_visibility_element(locator.EDIT_BTN)
    page.click(locator.EDIT_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.click(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, edited_subnet_name)
    page.click(locator.SAVE_SUBMIT_BTN)

    WebDriverWait(driver, 10).until(
    lambda d: d.find_element(*locator.DETAIL_NAME).text.strip() == edited_subnet_name)

    page.click(locator.DELETE_BTN)
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((
        By.XPATH, "//div[@role='dialog']")))
    page.click(locator.DELETE_CONFIRM_BTN)

    WebDriverWait(driver, 10).until_not(
    EC.presence_of_element_located((By.XPATH, f"//td[normalize-space()='{edited_subnet_name}']")))
    elements = driver.find_elements(By.XPATH, f"//td[normalize-space()='{edited_subnet_name}']")
    assert len(elements) == 0, "⛔test_sg_015_subnet_edit_to_delete, 서브넷 삭제 실패"

    page.click(locator.vnet_menu)
    created_vnet = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH,f"//td[normalize-space()='{target_vnet_name}']")))
    created_vnet.click()
    page.click(locator.DELETE_BTN)
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((
        By.XPATH, "//div[@role='dialog']")))
    page.click(locator.DELETE_CONFIRM_BTN)    

    WebDriverWait(driver, 10).until_not(
    EC.presence_of_element_located((By.XPATH, f"//td[normalize-space()='{target_vnet_name}']")))
    elements = driver.find_elements(By.XPATH, f"//td[normalize-space()='{target_vnet_name}']")
    assert len(elements) == 0, "⛔test_sg_015_vnet_create_to_delete, 가상 네트워크 삭제 실패"


@pytest.mark.e2e
def test_sg_013_nic_create_to_delete(logged_in_setup):
    driver = logged_in_setup
    page = BasePage(driver)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_vnet_name = f"vnet-team03-e2etest-{ts}"
    target_subnet_name = f"subnet-team03-e2etest-{ts}"
    target_nic_name = f"nic-team03-e2etest-{ts}"
    edited_nic_name = f"{target_nic_name}-edited"

    page.click(locator.NT_MENU)
    page.click(locator.vnet_menu)
    page.click(locator.VNET_CREATE_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.click(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, target_vnet_name)
    page.click(locator.SUBMIT_BTN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,f"//td[normalize-space()='{target_vnet_name}']")))

    page.click(locator.NETWORK_BTN)
    page.click(locator.SUBNET_BTN)
    page.click(locator.SUBNET_CREATE_BTN)

    page.wait_visibility_element(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, target_subnet_name)
    WebDriverWait(driver, 5).until(lambda d: d.find_element(*locator.NAME_INPUT)
                                .get_attribute("value") == target_subnet_name)

    combo = page.wait_visibility_element(locator.VNET_COMBO_INPUT)
    combo.click()
    combo.send_keys(target_vnet_name)

    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH, f"//li[@role='option' and contains(., '{target_vnet_name}')]")))
    option.click()

    form_title = driver.find_element(By.XPATH, "//h6[contains(text(), '서브넷 생성')]")
    form_title.click()

    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(locator.SUBMIT_BTN))
    submit_btn.click()

    success_xpath = (By.XPATH, f"//tbody/tr/td[text()='{target_subnet_name}']")
    page.wait_visibility_element(success_xpath)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
    By.XPATH, f"//td[normalize-space()='{target_subnet_name}']")))
 
    page.click(locator.NIC_BTN)
    page.click(locator.NIC_CREATE_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, target_nic_name)
    WebDriverWait(driver, 5).until(lambda d: d.find_element(*locator.NAME_INPUT)
                                .get_attribute("value") == target_nic_name)

    select_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(locator.SUBNET_SELECT_VALUE))
    select_box.click()

    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH, f"//li[@role='option' and contains(., '{target_subnet_name}')]")))
    option.click()

    form_title = driver.find_element(By.XPATH, "//h6[contains(text(), '네트워크 인터페이스 생성')]")
    form_title.click()

    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(locator.SUBMIT_BTN))
    submit_btn.click()

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//td[normalize-space()='{target_nic_name}']")))

    driver.find_element(By.XPATH, f"//td[normalize-space()='{target_nic_name}']").click()
    page.wait_visibility_element(locator.EDIT_BTN)
    page.click(locator.EDIT_BTN)
    page.wait_visibility_element(locator.NAME_INPUT)
    page.click(locator.NAME_INPUT)
    page.clear_and_type(locator.NAME_INPUT, edited_nic_name)
    page.click(locator.SAVE_SUBMIT_BTN)

    WebDriverWait(driver, 15).until(
        lambda d: d.find_element(*locator.DETAIL_NAME).text.strip() == edited_nic_name)

    page.click(locator.DELETE_BTN)
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
    page.click(locator.DELETE_CONFIRM_BTN)

    WebDriverWait(driver, 15).until_not(
        EC.presence_of_element_located((By.XPATH, f"//td[normalize-space()='{edited_nic_name}']")))

    page.click(locator.SUBNET_BTN)
    subnet_row = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (By.XPATH, f"//td[normalize-space()='{target_subnet_name}']")))
    subnet_row.click()
    page.click(locator.DELETE_BTN)
    page.click(locator.DELETE_CONFIRM_BTN)

    WebDriverWait(driver, 15).until_not(
        EC.presence_of_element_located((
            By.XPATH, f"//td[normalize-space()='{target_subnet_name}']")))

    page.click(locator.vnet_menu)
    driver.find_element(By.XPATH, f"//td[normalize-space()='{target_vnet_name}']").click()
    page.click(locator.DELETE_BTN)
    page.click(locator.DELETE_CONFIRM_BTN)

    WebDriverWait(driver, 15).until_not(
        EC.presence_of_element_located((By.XPATH, f"//td[normalize-space()='{target_vnet_name}']")))
