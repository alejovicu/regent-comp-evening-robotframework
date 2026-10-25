"""Request and response schemas."""
from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class ProductIn(BaseModel):
    sku: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0, le=1_000_000)
    description: str = Field(default="", max_length=500)


class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0, le=1_000_000)
    description: str = Field(default="", max_length=500)


class Product(ProductIn):
    id: str


class CartItemIn(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartLine(BaseModel):
    product_id: str
    sku: str
    name: str
    price: float
    quantity: int
    line_total: float


class Cart(BaseModel):
    username: str
    items: list[CartLine]
    item_count: int
    total: float


class IngestionRequest(BaseModel):
    filename: str = "catalog.csv"
    replace: bool = False


class RowError(BaseModel):
    line: int
    error: str


class IngestionResult(BaseModel):
    filename: str
    replace: bool
    created: int
    updated: int
    deleted: int
    errors: list[RowError]
