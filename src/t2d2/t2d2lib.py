"""T2D2 SDK Library"""
# pylint: disable=W0718

import requests


class RESTClient(object):
    """REST API helper"""

    base_url: str
    headers: dict = {"Content-Type": "application/json"}
    timeout = 30

    def __init__(self, base_url):
        """Constructor"""
        self.base_url = base_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

    def request(self, url, method="GET", params=None, data=None):
        """Request and return response"""
        url = self.base_url + url
        res = requests.request(
            method,
            url=url,
            params=params,
            json=data,
            headers=self.headers,
            timeout=self.timeout,
        )

        try:
            return res.json()
        except Exception as err:
            print(f"Json conversion error: {err}")
            return {"content": res.content}


class T2D2(object):
    """Main T2D2 Class"""

    rest: RESTClient
    user: None
    project: None
    organization: None

    def __init__(self, credentials, base_url="https://app.t2d2.ai/api-v2/"):
        """Initialize and authenticate"""
        self.rest = RESTClient(base_url)

        self.login(credentials)

    def login(self, credentials):
        """Login and update header with authorization credentials"""

        if "password" in credentials:
            # Login with email/password
            url = "user/login"
            json_data = self.rest.request(url, "POST", data=credentials)
            access_token = json_data["data"]["firebaseDetail"]["access_token"]
            self.rest.headers["Authorization"] = f"Bearer {access_token}"
            self.user = json_data["data"]["user"]

        elif "access_token" in credentials:
            # Directly use token
            access_token = credentials["access_token"]
            self.rest.headers["Authorization"] = f"Bearer {access_token}"

        elif "api_key" in credentials:
            # Login with api_key
            self.rest.headers["x-api-key"] = credentials["api_key"]

        return

    def set_user(self, user_id):
        """Set current user"""
        json_data = self.rest.request(f"user/{user_id}")
        self.user = json_data["data"]
        return

    def set_organization(self, organization_id):
        """Set current organization"""
        json_data = self.rest.request(f"organization/{organization_id}")
        self.organization = json_data["data"]
        return

    def set_project(self, project_id):
        """Set current project"""
        json_data = self.rest.request(f"project/{project_id}")
        self.project = json_data["data"]
        return

    def get_images(self, options=None):
        """Get images from current project"""
        if options is None:
            options = {}

        params = {
            "project_id": self.project["id"],
            "image_ids": options.get("image_ids", []),
            "filter_id": options.get("filter_id", None),
        }
        json_data = self.rest.request("images", params=params)

        return json_data["data"]

    def add_images(self, payload):
        """Add images to current project"""
        return self.rest.request("images", "POST", data=payload)
        


"""
upload_images
add_images
delete_images
update_images
"""
