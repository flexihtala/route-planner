from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathfinder import PathFinder


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/web/static", StaticFiles(directory="web/static"), name="web/static")


class Query(BaseModel):
    address: str
    radius: float
    place_type: list[str]


@app.post("/api/places/search/")
async def search_places(data: Query):
    print(data)
    pf = PathFinder.PathFinder(data.address, data.radius, data.place_type)
    test_path = pf.the_dumbest_greedy_algorithm()
    print(test_path)
    results = [{"name": place.__repr__(), "address": place.__repr__(), "coordinates":
        place.__repr__()} for place in test_path]

    return {"results": results}
