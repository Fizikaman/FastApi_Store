from fastapi import FastAPI
from routers import category, products

app = FastAPI()


@app.get("/")
async def welcome() -> dict:
    return {"message": "Fizik store fastapi app"}


app.include_router(category.router)
app.include_router(products.router)
