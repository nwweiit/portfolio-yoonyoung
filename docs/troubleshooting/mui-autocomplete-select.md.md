## 1️⃣ MUI Autocomplete - 값 입력 및 선택 문제

### 문제 상황
- 드롭다운 input에 값을 입력하고 Arrow Down + Enter를 눌렀지만 옵션이 선택되지 않음
- `send_keys()`로 입력한 값이 화면에는 보이지만, 폼 validation이 인식하지 못하고 "생성" 버튼이 활성화되지 않음

### 문제 발생 조건
- MUI Autocomplete로 `<input role="combobox">`를 사용 
- 일반 `send_keys()`로는 React의 `onChange` 이벤트가 트리거되지 않음
- 드롭다운 옵션(`li[role='option']`)이 DOM에 렌더링되기 전에 키 입력하면 무시됨
- 옵션 선택 후 포커스가 그대로 input에 남아있어서 blur 이벤트가 발생하지 않음

### 해결 전 코드

```python
# Subnet 생성 시 가상네트워크 콤보 클릭(Autocomplete 방식)
combo = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator.VNET_COMBO_INPUT))
combo.click()

# Ctrl+A + Backspace로 삭제 시도
combo.send_keys(Keys.CONTROL, "a")
combo.send_keys(Keys.BACKSPACE)

combo.send_keys(target_vnet_name)

# 드롭다운 열림 대기
WebDriverWait(driver, 10).until(
    lambda d: combo.get_attribute("aria-expanded") == "true")

# Arrow Down + Enter 시도 (작동 안 함)
combo.send_keys(Keys.ARROW_DOWN)
combo.send_keys(Keys.ENTER)

# 버튼 클릭에서 활성화가 안되어서 실패

base.click(locator.SUBMIT_BTN)

# 추가 시도했으나 실패한 방법들:

# 1. JavaScript 클릭 시도했으나 실패
driver.execute_script("arguments[0].click();", combo)

driver.execute_script("arguments[0].click();", submit_btn)

# 2. TAB을 통해 해당 콤보박스까지 이동시켜 해결해보려 했으나 실패
combo.send_keys(Keys.TAB)
combo.send_keys(Keys.TAB)

# 3. 붙여넣기 동작을 넣어 시도해보려 했으나 실패
import pyperclip
pyperclip.copy(target_vnet_name)
combo.send_keys(Keys.CONTROL + "v")

# 4. 드롭다운 화살표 직접 클릭을 통해 해결하려 했으나 실패
dropdown_arrow = driver.find_element(By.CSS_SELECTOR, "button.MuiAutocomplete-popupIndicator")
dropdown_arrow.click()
combo.send_keys(target_vnet_name)
option.click()
```

### 해결 후 코드

```python
# Subnet 생성 시 가상네트워크 콤보 클릭
combo = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator.VNET_COMBO_INPUT))
combo.click()
combo.send_keys(target_vnet_name)

# 드롭다운 옵션이 나타날 때까지 명시적 대기
option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, f"//li[@role='option' and contains(., '{target_vnet_name}')]")))
option.click()

# 폼 헤더 클릭으로 blur 이벤트 발생시키기 
form_title = driver.find_element(By.XPATH, "//h6[contains(text(), '서브넷 생성')]")
form_title.click()

# 버튼 활성화 대기 후 클릭
submit_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(locator.SUBMIT_BTN))
submit_btn.click()
```

### 결과 검증
- 옵션 클릭 후 input의 `value` 속성에 선택한 값이 포함되는지 확인
- 헤더 클릭 후 "생성" 버튼이 `element_to_be_clickable` 상태가 되는지 확인 
---

## 2️⃣ MUI Select - 클릭 전용 드롭다운

### 문제 상황
- 조금전 서브넷 생성단계였던 Autocomplete와 동일한 방식(`send_keys()`)으로 처리했지만 작동하지 않음
- `locator.COMBOBOX`로 input을 찾으려 했지만 실제로는 div 요소임
- 값 선택 후 폼이 여전히 선택을 인식하지 못함

### 문제 발생 조건
- locator를 잘못 잡고 있었음
- MUI Select는 `<div role="combobox">`를 사용하며 **타이핑 불가** 
- `id="mui-component-select-*"` 패턴을 가진 요소는 Select 컴포넌트
- `input` 태그가 아닌 `div` 태그이므로 `send_keys()` 불가능
- 옵션 선택 후에 blur 처리가 필요함 

### 해결 전 코드

```python
# NIC 생성 시 서브넷 콤보 클릭(Select방식)
combo = base.wait_visibility_element(locator.COMBOBOX)  
combo.click()

# send_keys 시도 (작동 안 함 - div는 입력 불가)
combo.send_keys(target_subnet_name)

option = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, f"//li[@role='option' and contains(., '{target_subnet_name}')]")))
option.click()

# value 확인 시도 
WebDriverWait(driver, 10).until(
    lambda d: target_subnet_name in 
    d.find_element(*locator.SUBNET_SELECT_VALUE).get_attribute("value"))

base.click(locator.SUBMIT_BTN)
```
### 해결 후 코드

```python
# NIC 생성 - Select
# Select div 클릭 (타이핑 없이 클릭만 시도)
select_box = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(locator.SUBNET_SELECT_VALUE)
)
select_box.click()

# 드롭다운 옵션 클릭
option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((
        By.XPATH, f"//li[@role='option' and contains(., '{target_subnet_name}')]")))
option.click()

# 폼 헤더 클릭으로 blur 이벤트 발생 (validation 트리거)
form_title = driver.find_element(By.XPATH, "//h6[contains(text(), '네트워크 인터페이스 생성')]")
form_title.click()

# 버튼 활성화 대기 후 클릭
submit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator.SUBMIT_BTN))
submit_btn.click()
```


### 결과 검증
- Select div의 텍스트 내용이 선택한 옵션으로 변경되는지 확인
- `aria-expanded` 속성이 `false`로 변경되는지 확인 (드롭다운 닫힘) 
- 헤더 클릭 후 버튼이 활성화되는지 확인


## ✅ 최종 정리

- React 기반 MUI 컴포넌트는 **겉모습이 아닌 DOM 구조(`input` vs `div`)와 `role` 속성 기준으로 판단해야 한다.**

- 자동화 전략
  - **Autocomplete** → 타이핑 + 옵션 클릭
  - **Select** → 드롭다운 열기 + 옵션 클릭

- 다양한 접근 방식을 **가설 → 검증 방식으로 하나씩 제거하며 문제를 해결하는 것이 효과적이었다.**
