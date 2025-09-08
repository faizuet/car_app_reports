from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CarBase(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    category: Optional[str] = None
    make_id: Optional[int] = None
    car_model_id: Optional[int] = None
    car_model_name: Optional[str] = None


class CarCreate(CarBase):
    name: str = Field(..., description="Car name")
    year: int = Field(..., ge=1990, le=2026, description="Year of the car")
    make_id: int = Field(..., description="ID of the car make")
    car_model_id: Optional[int] = Field(None, description="Existing CarModel ID (optional)")
    car_model_name: Optional[str] = Field(None, description="New CarModel name (optional)")


class CarUpdate(CarBase):
    """Allow partial updates."""
    pass


class MakeRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CarModelRead(BaseModel):
    id: int
    name: str
    make: MakeRead

    class Config:
        orm_mode = True


class CarRead(BaseModel):
    id: int
    name: str
    year: int
    category: Optional[str] = None
    car_model: CarModelRead
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

    @property
    def full_name(self) -> str:
        """Return full car name: Make + Model + Year"""
        make_name = self.car_model.make.name if self.car_model and self.car_model.make else ""
        model_name = self.car_model.name if self.car_model else ""
        return f"{make_name} {model_name} {self.year}"


class CarSimplifiedRead(BaseModel):
    id: int
    name: str
    year: int
    make: str
    model: str
    category: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PaginatedCars(BaseModel):
    total: int
    items: List[CarRead]


class PaginatedCarsSimplified(BaseModel):
    total: int
    items: List[CarSimplifiedRead]

