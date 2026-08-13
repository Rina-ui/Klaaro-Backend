from contextlib import asynccontextmanager
from xml.etree.ElementInclude import include

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.routes.routes import api_router
from app.infrastructure.database import Base, engine
from app.infrastructure.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Action au démarrage de l'API
    start_scheduler()
    yield
    # Action à l'extinction de l'API
    shutdown_scheduler()

# On passe le lifespan à l'application FastAPI
app = FastAPI(
    title="Klaaro API",
    lifespan=lifespan
)

app = FastAPI(
    title="Klaaro API",
    description="la documentation de nos endpoints du backend",
    docs_url="/docs",
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

# creer automatiquement la db
Base.metadata.create_all(bind=engine)