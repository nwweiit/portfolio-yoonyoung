class APIClient:
    def __init__(self, access_token: str | None):
        self.session = create_session()
        self.access_token = access_token

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Host": "portal.gov.example.cloud"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def request(self, method, url, **kwargs):
        return self.session.request(
            method, url, headers=self._headers(), **kwargs
        )
    
    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, json=None, **kwargs):
        return self.request("POST", url, json=json, **kwargs)

    def patch(self, url, json=None, **kwargs):
        return self.request("PATCH", url, json=json, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)
