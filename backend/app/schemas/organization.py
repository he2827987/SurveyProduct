# backend/app/schemas/organization.py

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

# Shared properties
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

# Properties to receive on organization creation
class OrganizationCreate(OrganizationBase):
    # owner_id will be set by the API based on the current user
    pass

# Properties to receive on organization update
class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)

# Properties shared by models stored in DB
class OrganizationInDBBase(OrganizationBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True # Use from_attributes instead of orm_mode for Pydantic v2

# Properties to return to client
class OrganizationResponse(OrganizationInDBBase):
    pass

# Properties stored in DB
class OrganizationInDB(OrganizationInDBBase):
    pass

