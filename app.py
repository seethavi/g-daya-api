from typing import Optional
from datetime import date

from sqlmodel import Field

from db import SQLModel, engine

class Entity(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    def matches(self, q: str) -> bool:
        return q in str(id)

class Donation(Entity, table=True):
    amount: float = Field(default=None, nullable=False)
    donation_date: date = Field(default=date.today, nullable=False)
    donor_id: Optional[int] = Field(default=None, foreign_key="donor.id")

    def matches(self, q: str) -> bool:
        if q in str(self.amount) or q in str(self.donation_date) or q in str(self.donor_id):
            return True
        return super().matches(q)

class Donor(Entity, table=True):
    first_name: str
    last_name: str
    email: str
    phone: str

    def matches(self, q: str) -> bool:
        if q in str(self.first_name) or q in str(self.last_name) or q in str(self.email) or q in str(self.phone):
            return True
        return super().matches(q)

# More code here later 👇