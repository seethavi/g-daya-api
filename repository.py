from typing import List, TypeVar, Generic, Type

from sqlmodel import Session, select, SQLModel, create_engine
from app import Donation, Donor

sqlite_file_name = "./database/dayadb.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

class Repository[T]:
   def __init__(self, model_class: Type[T]):
      self._mdl_class = model_class

   def create_one_item(self, item: T) -> T:
      with Session(engine) as session:
         session.add(item)
         session.commit()
         session.refresh(item)
      return item

   def get_one_item(self, id: int) -> T:
      with Session(engine) as session:
         return session.exec(select(self._mdl_class).where(self._mdl_class.id == id)).first()
      
   def get_many_items(self, item_ids: List[int]) -> List[T]:
      with Session(engine) as session:
         return session.exec(select(self._mdl_class).where(id in item_ids))
   
   def get_items(self, offset: int, limit: int, sort: str | None = None, order: str | None = None, q: str | None = None) -> List[T]:
      sort_attr = getattr(self._mdl_class, sort) if sort else self._mdl_class.id
      with Session(engine) as session:
         items = session.exec(select(self._mdl_class)
               .order_by(sort_attr.desc() if order == "DESC" else sort_attr.asc())
               .offset(offset)
               .limit(limit)).all()
         if q:
            filtered_items = [ item for item in items if item.matches(q)]
         else:
            filtered_items = items
         return filtered_items

   def get_all_items(self) -> List[T]:
      with Session(engine) as session:         
         return session.exec(select(self._mdl_class)).all()
      
class DonationRepository(Repository[Donation]):
   def __init__(self):
      super().__init__(Donation)

class DonorRepository(Repository[Donor]):
   def __init__(self):
      super().__init__(Donor)