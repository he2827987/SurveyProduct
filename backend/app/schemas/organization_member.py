# backend/app/schemas/organization_member.py

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

# Shared properties
class OrganizationMemberBase(BaseModel):
    organization_id: int
    user_id: int
    role: str = Field("member", min_length=1, max_length=50) # Default role is "member"

# Properties to receive on organization member creation
class OrganizationMemberCreate(OrganizationMemberBase):
    pass

# Properties to receive on organization member update
class OrganizationMemberUpdate(BaseModel):
    role: Optional[str] = Field(None, min_length=1, max_length=50)

# Properties shared by models stored in DB
class OrganizationMemberInDBBase(OrganizationMemberBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True # Use from_attributes instead of orm_mode for Pydantic v2

# Properties to return to client
class OrganizationMemberResponse(OrganizationMemberInDBBase):
    pass

# Properties stored in DB
class OrganizationMemberInDB(OrganizationMemberInDBBase):
    pass

