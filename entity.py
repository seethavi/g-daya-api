from typing import List, Optional
from datetime import date

from sqlmodel import Field, Relationship

from db import SQLModel, engine

import inspect

class Entity(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    def matches(self, q: str) -> bool:
        members = filter(lambda member: not member[0].startswith('_') and not inspect.ismethod(member[1]), inspect.getmembers(self))

        for _, val in members:
            if q in str(val):
                return True
        return False

class Donation(Entity, table=True):
    amount: float = Field(default=None, nullable=False)
    donation_date: date = Field(default=date.today(), nullable=False)
    donor_id: Optional[int] = Field(default=None, foreign_key="donor.id")
    def __init__(self, amount: float, donor_id: int, donation_date: str | None = None, id: int | None = None):
        self.amount = amount
        self.donation_date = date.fromisoformat(donation_date) if donation_date else date.today()
        self.donor_id = donor_id


class Donor(Entity, table=True):
    first_name: str = Field(default=None, nullable=False)
    last_name: str = Field(default=None, nullable=False)
    email: str = Field(default=None, nullable=False)
    phone: str = Field(nullable=True)
    

# More code here later 