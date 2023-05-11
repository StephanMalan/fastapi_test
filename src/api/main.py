import tomllib
from fastapi import FastAPI

from src.api import countours, points

DESCRIPTION = """
Test project for using popular Python libraries.

This project allows you to create, request, update, and delete points and contours.

This application uses FastAPI, SqlAlchemy, Alembic, and Postgres.
"""

tags_metadata = [
    {
        "name": "Points",
        "description": "A point represents a 2D coordinate which consists of an x and y value. "
        "These endpoints allow the user to retrieve, create, update, and delete points.",
    },
    {
        "name": "Contours",
        "description": "A contour represents a single closed curve which consists of multiple (more than 3) points. "
        "These endpoints allow the user to retrieve, create, update, and delete contours.",
    },
]

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

app = FastAPI(
    title="FastAPI interview",
    description=DESCRIPTION,
    version=data["tool"]["poetry"]["version"],
    openapi_tags=tags_metadata,
    redoc_url=None,
    contact={"name": "Stephan Malan", "email": "stephanmalan.rob@gmail.com"},
)

app.include_router(countours.router)
app.include_router(points.router)
