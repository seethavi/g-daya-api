from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from data import donor_list, donation_list
from repository import DonationRepository, DonorRepository
from app import Donation, Donor
from fastapi.encoders import jsonable_encoder


app = FastAPI()

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8080",
    "https://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-total-count"]
)

@app.post("/donations/")
async def create_donation(donation: Donation):
    print(donation)
    
    repository = DonationRepository()
    created_item = repository.create_one_item(donation)
    json_content = {"id": created_item.id}
    return JSONResponse(content = json_content)
    

@app.post("/donors/")
async def create_donor(donor: Donor):
    repository = DonorRepository()
    created_item = repository.create_one_item(donor)
    json_content = {"id": created_item.id}
    return JSONResponse(content = json_content)

@app.get("/donations/{id}")
async def get_donation(id: int):
    repository = DonationRepository()
    searched_item = repository.get_one_item(id)
    json_content = jsonable_encoder(searched_item)
    return JSONResponse(content = json_content)

@app.get("/donors/{id}")
async def get_donor(id: int):
    repository = DonorRepository()
    searched_item = repository.get_one_item(id)
    json_content = jsonable_encoder(searched_item)
    print(json_content)
    return JSONResponse(content = json_content)

@app.get("/donors/")
async def donors(_start: int | None = 0, _end: int | None = 10, _sort: str | None = None, _order: str | None = None, q: str | None = None):
    repository = DonorRepository()
    results = repository.get_items(offset = _start, limit = _end - _start + 1, sort = _sort, order = _order, q = q)
    headers = {"x-total-count": str(len(results))}
    json_content = jsonable_encoder(results)
    return JSONResponse(content = json_content, headers = headers)

@app.get("/donations/")
async def donations(_start: int | None = 0, _end: int | None = 10, _sort: str | None = None, _order: str | None = None, q: str | None = None):
    repository = DonationRepository()
    results = repository.get_items(offset = _start, limit = _end - _start + 1, sort = _sort, order = _order, q = q)
    headers = {"x-total-count": str(len(results))}
    json_content = jsonable_encoder(results)
    return JSONResponse(content = json_content, headers = headers)