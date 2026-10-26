"""Keywords that talk to the Demo Shop REST API directly.

Used for fast test setup (resetting data, seeding products) and for checks that
cannot be made through the UI, such as role enforcement on the API.
"""
import json
import urllib.error
import urllib.request

from robot.api import logger
from robot.api.deco import keyword, library


@library(scope="SUITE")
class CatalogApi:
    def __init__(self, base_url):
        self._api_url = base_url.rstrip("/") + "/api"
        self._token = None

    @keyword
    def authenticate_as(self, username, password):
        """Logs in through the API; later calls are sent with this user's token."""
        status, body = self._send("POST", "/auth/login", {"username": username, "password": password}, token=None)
        if status != 200:
            raise AssertionError(f"API login as '{username}' failed with status {status}: {body}")
        self._token = body["access_token"]

    @keyword
    def clear_authentication(self):
        """Sends later calls without a token."""
        self._token = None

    @keyword
    def reset_demo_data(self):
        """Restores the 6 sample products and empties all carts. Needs an admin token."""
        self._expect(200, "POST", "/admin/reset")

    @keyword
    def create_product(self, sku, name, price, description=""):
        body = {"sku": sku, "name": name, "price": float(price), "description": description}
        return self._expect(201, "POST", "/products", body)

    @keyword
    def get_product(self, sku):
        """Returns the product with `sku`, or fails if it does not exist."""
        product = self._find(sku)
        if product is None:
            raise AssertionError(f"Product {sku} does not exist")
        return product

    @keyword
    def product_should_not_exist(self, sku):
        if self._find(sku) is not None:
            raise AssertionError(f"Product {sku} exists but should not")

    @keyword
    def delete_product(self, sku):
        self._expect(204, "DELETE", f"/products/{self.get_product(sku)['id']}")

    @keyword
    def send_product_request(self, method, sku=None, body=None):
        """Sends `method` to /products (or /products/<id of sku>) and returns the status code.

        Does not fail on error responses, so tests can assert on 401/403/404.
        `body` can be a dictionary or a JSON string.
        """
        if isinstance(body, str):
            body = json.loads(body)
        path = "/products"
        if sku:
            path += f"/{self.get_product(sku)['id']}"
        status, _ = self._send(method.upper(), path, body)
        return status

    def _find(self, sku):
        products = self._expect(200, "GET", "/products")
        return next((p for p in products if p["sku"] == sku), None)

    def _expect(self, expected_status, method, path, body=None):
        status, data = self._send(method, path, body)
        if status != expected_status:
            raise AssertionError(f"{method} {path} returned {status}, expected {expected_status}: {data}")
        return data

    def _send(self, method, path, body=None, token=...):
        token = self._token if token is ... else token
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self._api_url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read()
        logger.debug(f"{method} {path} -> {status}")
        return status, json.loads(raw) if raw else None
