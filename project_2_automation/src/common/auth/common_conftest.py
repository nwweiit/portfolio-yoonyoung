@pytest.fixture(scope="session")
def api_client():
    token = os.getenv("ECI_ACCESS_TOKEN")
    if not token:
        raise TokenNotProvidedError("ECI_ACCESS_TOKEN 없음")

    return APIClient(token)
