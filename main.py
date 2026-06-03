from xml.etree.ElementInclude import include

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.routes.routes import api_router

app = FastAPI(
    title="Klaaro API",
    description="le backend",
    docs_url="/",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "good"}

# routes
app.include_router(api_router)