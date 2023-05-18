"""S3 Client Class"""
# pylint: disable=W0718, C0103
from enum import Enum, auto
from urllib.parse import urlparse

import requests


class RequestType(Enum):
    """Request type class"""
    GET = auto()
    PUT = auto()
    POST = auto()
    DELETE = auto()


class T2D2(object):
    """Main T2D2 Class"""
    base_url: str = "https://develop.t2d2.ai/api-v2/"
    headers: dict
    project: dict
    authToken: str
    s3_base_url: str
    aws_region: str = "us-east-1"
    bucket: str
    project_details: dict

    def __init__(self, credentials, base_url="https://develop.t2d2.ai/api-v2/"):
        """Initialize / login"""

        if not base_url.endswith("/"):
            base_url += "/"

        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.login(credentials)
        self.project = {}

    def request(
        self,
        url_suffix: str,
        req_type: RequestType = RequestType.GET,
        params=None,
        headers=None,
        data=None,
    ) -> dict:
        """Send a request and handle response"""

        url = self.base_url + url_suffix
        if not params:
            params = {}
        if not data:
            data = {}
        if not headers:
            headers = self.headers
        else:
            headers = self.headers.update(headers)

        if req_type == RequestType.GET:
            res = requests.get(
                url, headers=headers, params=params, timeout=30
            )
        elif req_type == RequestType.POST:
            res = requests.post(
                url, headers=headers, params=params, json=data, timeout=30
            )
        elif req_type == RequestType.PUT:
            res = requests.put(
                url, headers=headers, params=params, json=data, timeout=30
            )
        elif req_type == RequestType.DELETE:
            res = requests.delete(
                url, headers=headers, params=params, json=data, timeout=30
            )
        else:
            raise ValueError("Request type not yet supported.")

        if res.status_code == 200:
            try:
                return res.json()
            except Exception as err:
                print(f"Json conversion error: {err}")
                return {"content": res.content}
        else:
            print(f"URL: {req_type} {url}")
            print(f"HEADERS: {headers}")
            print(f"PARAMS: {params}")
            print(f"DATA: {data}")
            print(res.status_code, res.content)
            raise ValueError(f"Error code received: {res.status_code}")

    def login(self, credentials):
        """Login and update header with authorization credentials"""

        if "access_token" in credentials:
            # Directly use token
            self.authToken = credentials["access_token"]
            self.headers["Authorization"] = f"Bearer {self.authToken}"

        elif "password" in credentials:
            # Login
            url = "user/login"
            jsonData = self.request(url, RequestType.POST, data=credentials)
            self.authToken = jsonData["data"]["firebaseDetail"]["access_token"]
            self.headers["Authorization"] = f"Bearer {self.authToken}"

        elif "api_key" in credentials:
            self.api_key = credentials["api_key"]
            self.headers["x-api-key"] = self.api_key

        return

    def set_project(self, project_id):
        """Set project by project_id"""
        jsonData = self.request(f"project/{project_id}", RequestType.GET)
        p = jsonData["data"]
        self.project = p

        self.s3_base_url = p["config"]["s3_base_url"]
        self.aws_region = p["config"]["aws_region"]
        res = urlparse(self.s3_base_url)
        self.bucket = res.netloc.split(".")[0]

        return

    #########################################################
    # IMAGES
    #########################################################

    def get_images(self, region="", filter_id=None):
        """Return image list by region"""
        page, limit, count, total = 1, 100, 0, 100
        image_list = []
        project_id = self.project["id"]
        while count < total:
            params = {
                "search": region,
                "limit": limit,
                "page": page,
                "queryType": 1,
            }
            if filter_id:
                params["filter_id"] = filter_id
            jsonData = self.request(
                f"{project_id}/images", RequestType.GET, params=params
            )
            image_list += jsonData["data"]["image_list"]
            total = jsonData["data"]["total_images"]
            count = len(image_list)
            print(
                f"Storing {count} of {total}. Got {len(jsonData['data']['image_list'])} this round."
            )
            page += 1

        return image_list

    def get_image(self, image_id, drawing_id=None, filter_id=None):
        """Return image"""
        project_id = self.project["id"]
        params = {}
        if drawing_id:
            params["drawing_id"] = drawing_id
        if filter_id:
            params["filter_id"] = filter_id

        res = self.request(
            f"{project_id}/images/{image_id}", RequestType.GET, params=params
        )
        return res["data"]

    def get_drawings(self, filter_id=None):
        """Get all project drawings"""
        project_id = self.project["id"]
        params = {}
        if filter_id:
            params["filter_id"] = filter_id
        res = self.request(f"{project_id}/drawings", RequestType.GET, params=params)
        return res["data"]

    def get_drawing(self, drawing_id):
        """Get single drawing"""
        project_id = self.project["id"]
        res = self.request(f"{project_id}/drawings/{drawing_id}", RequestType.GET)
        return res["data"]

    def get_geotags(self, drawing_id):
        """Get all geotags of drawing"""
        project_id = self.project["id"]
        params = {"drawing_id": drawing_id}
        res = self.request(f"{project_id}/geotags", RequestType.GET, params=params)
        return res["data"]

    def get_filter(self, filter_id):
        """Get filter"""
        project_id = self.project["id"]
        jsonData = self.request(f"{project_id}/filters/{filter_id}", RequestType.GET)
        return jsonData["data"]

    #########################################################
    # REPORTS
    #########################################################
    def upload_report(self, data):
        """Report Upload"""
        project_id = self.project["id"]
        url = f"{project_id}/reports"
        res = self.request(url, RequestType.PUT, data=data)
        return res

    def get_regions(self):
        """Regions"""
        project_id = self.project["id"]
        url = f"{project_id}/categories/regions"
        res = self.request(url, RequestType.GET, params=self.project["id"])
        return res
