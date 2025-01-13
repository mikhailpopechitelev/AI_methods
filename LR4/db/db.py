from typing import Optional
from annotated_types import Annotated, Ge, Le
from sqlmodel import Field, SQLModel, Session, create_engine, select
from sqlalchemy import Engine, String
from sqlalchemy.sql.schema import Column



class  Composition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    year: int
    details: str


class Compositionshelf(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userID: int
    compositionID: int
    score: Annotated[int, Ge(0), Le(10)]


def initDB(dsn: str) -> Engine:
    engine = create_engine(dsn)
    SQLModel.metadata.create_all(engine)
    
    return engine