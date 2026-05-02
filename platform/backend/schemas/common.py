from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class PageOut(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class BulkIdsRequest(BaseModel):
    ids: list[int] = Field(default_factory=list)


class BulkDeleteResponse(BaseModel):
    deleted: int
