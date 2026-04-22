from pydantic import BaseModel, Field


class BulkIdsRequest(BaseModel):
    ids: list[int] = Field(default_factory=list)


class BulkDeleteResponse(BaseModel):
    deleted: int
