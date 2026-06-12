from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from routers import user, cities, scenery, food, culture, agent, advice
import settings

app = FastAPI(title="齐鲁途智 API", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"))

app.include_router(user.router)
app.include_router(cities.router)
app.include_router(scenery.router)
app.include_router(food.router)
app.include_router(culture.router)
app.include_router(agent.router)
app.include_router(advice.router)

# CORS 配置
origins = [
    settings.FRONTEND_URL,
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://cheerful-froyo-5276ea.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
