import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Column
from pgvector.sqlalchemy import Vector

class Restaurant(SQLModel, table=True):
    __tablename__ = "restaurants"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    phone_number: str = Field(unique=True, index=True)
    zip_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Deal(SQLModel, table=True):
    __tablename__ = "deals"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    restaurant_id: uuid.UUID = Field(foreign_key="restaurants.id", ondelete="CASCADE")
    item_name: str
    price: float
    image_url: Optional[str] = None
    embedding: Optional[list[float]] = Field(sa_column=Column(Vector(768)))
    expires_at: datetime
    start_at: Optional[datetime] = None
    is_weekly: bool = Field(default=False)
    recurrence_day: Optional[int] = None
    cuisine_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
