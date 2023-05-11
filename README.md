# FastAPI test

In this project, I used FastAPI for the API and Postgres for the database.
Other Python modules I used include Pydantic for validation, Alembic as a database migration tool, Shapely for polygon calculations, SQLAlchemy for connection to the
database.
I also added static type analysis with Mypy and Ruff and Pylint for linting.
Black was used for formatting.
For testing, I used Pytest for creating the unit tests and Coverage to generate the code coverage.

#
To run the application and test it manually, run the following command:
```
make run_dev
```
You can view the documentation at: http://127.0.0.1:8000/docs

#
To run the tests and view the code coverage, run the following command:
```
make run_test
```