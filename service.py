from typing import List, TypeVar, Generic, Type
from fastapi import FastAPI, APIRouter
from datetime import date
import json
import copy

from sqlmodel import Session, select, update, delete, SQLModel, create_engine
from entity import Entity, Donation, Donor
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

sqlite_file_name = "./database/dayadb.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

class Service[T: Entity]:
   def __init__(self, model_class: Type[T], path: str):

      async def create_item(item: T):
         created_item = self._create_item(item)
         json_content = {"id": created_item.id}
         return JSONResponse(content = json_content)
      
      async def get_item(id: int):
         searched_item = self._get_item(id)
         json_content = jsonable_encoder(searched_item)
         return JSONResponse(content = json_content)
      
      async def update_item(id: int, item: T):
         updated_item = self._update_item(id, item) # sqlmodel uses the same syntax for update/create
         json_content = jsonable_encoder(updated_item)
         return JSONResponse(content = json_content)
      
      async def delete_item(id: int):
         deleted_item = self._delete_ite(id)
         json_content = jsonable_encoder(deleted_item)
         return JSONResponse(content = json_content)
      
      async def update_many_items(json: dict): # receives a json with ids of items to be updated and the values to be updated
         ids = json["ids"]
         values = json.values
         self._update_many_items(ids, values)
         return JSONResponse(content = ids)
      
      async def delete_many_items(json: dict): # receives a json with ids of items to be deleted 
         ids = json["ids"]
         self._delete_many_items(ids)
         return JSONResponse(content = ids)
      
      #query format for retrieving a list of items
      #sort: ['title', 'ASC'],
      #range: [0, 4],
      #filter: { author_id: 12 }

      async def get_items(sort: str | None = '["id", "ASC"]', range: str | None = '[0, 9]', filter: str | None = None):
         rangeJson = json.loads(range)
         offset = rangeJson[0]
         limit = rangeJson[1] + 1      
         sortJson = json.loads(sort)
         sort = sortJson[0]
         order = sortJson[1] 
         filterJson = json.loads(filter) if filter else None      
         results = self._get_items(offset = offset, limit = limit, sort = sort, order = order, filter = filterJson)     
         headers = {"Content-Range": path.replace('/', '') + ' ' + str(offset + 1) + '-' 
                     + str(limit if limit < len(results) else len(results)) + '/' + str(len(results))}
         json_content = jsonable_encoder(results)
         return JSONResponse(content = json_content, headers = headers)      
   
      self.path = path
      self.router = APIRouter()
      self._mdl_class = model_class
      create_item.__annotations__["item"] = model_class
      update_item.__annotations__["item"] = model_class
      self.router.add_api_route(self.path, get_items, methods=["GET"])
      self.router.add_api_route(self.path + "{id}", get_item, methods=["GET"])
      self.router.add_api_route(self.path + "{id}", update_item, methods=["PUT"])
      self.router.add_api_route(self.path, create_item, methods=["POST"])
      self.router.add_api_route(self.path + "{id}", delete_item, methods=["DELETE"])
      self.router.add_api_route(self.path, delete_many_items, methods=["DELETE"])
         
   def _create_item(self, item: T) -> T:
      with Session(engine) as session:
         session.add(item)
         session.commit()
         session.refresh(item)
      return item

   def _update_item(self, id: int, item: T) -> T:
      item_json = jsonable_encoder(item)
      with Session(engine) as session:
         statement = update(self._mdl_class).where(self._mdl_class.id == id).values(item_json)
         session.exec(statement)
         session.commit()
      return item
         
   def _update_many_items(self, item_ids: List[int], item_values: dict) -> List[int]:
      with Session(engine) as session:
         statement = update(self._mdl_class).where(self._mdl_class.id.in_(item_ids)).values(item_values)
         session.exec(statement)
         session.commit()
      return item_ids

   def _delete_item(self, id: int) -> T:
      with Session(engine) as session:
         statement = delete(self._mdl_class).where(self._mdl_class.id == id)
         item = session.exec(statement).first()
         session.commit()
      return item

   def _delete_many_items(self, item_ids: List[int]) -> T:
      with Session(engine) as session:
         statement = delete(self._mdl_class).where(self._mdl_class.id.in_(item_ids))
         session.exec(statement)
         session.commit()
      return item_ids

   def _get_item(self, id: int) -> T:
      with Session(engine) as session:
         return session.exec(select(self._mdl_class).where(self._mdl_class.id == id)).first()
      
   def _get_many_items(self, item_ids: List[int]) -> List[T]:
      with Session(engine) as session:
         return session.exec(select(self._mdl_class).filter(self._mdl_class.id.in_(item_ids))).all()
   
   def _get_items(self, offset: int, limit: int, sort: str | None = None, order: str | None = None, filter: dict | None = None) -> List[T]:
      sort_attr = getattr(self._mdl_class, sort) if sort else self._mdl_class.id
      filter_expressions = []
      q = None
      for attr in filter.keys():
         if attr == 'q': # if it is a query across all fields then get the query value
            q = filter[attr]
         elif attr == 'id': # if filter is based on a list of ids
            return self._get_many_items(filter[attr])
         else: # else create a binary expression to be used in where clause
            binary_expr = (getattr(self._mdl_class, attr) == filter[attr])
            filter_expressions.append(binary_expr)
      
      with Session(engine) as session:
         items = session.exec(select(self._mdl_class)
               .where(*filter_expressions)
               .order_by(sort_attr.desc() if order == "DESC" else sort_attr.asc())
               .offset(offset)
               .limit(limit)).all()
         if q:
            filtered_items = [ item for item in items if item.matches(q)]
         else:
            filtered_items = items
         return filtered_items