import os

from sqlalchemy import Integer, String, JSON, ARRAY
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column

POSTGRES_USER = os.getenv("POSTGRES_USER", "swapi")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "swapi")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
)

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class SwapiPeople(Base):
    __tablename__ = 'swapi_people_all'
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    birth_year: MappedColumn[str] = mapped_column(String)
    eye_color: MappedColumn[str] = mapped_column(String)
    films: MappedColumn[list[str] | None] = mapped_column(ARRAY(String))
    gender: MappedColumn[str] = mapped_column(String)
    hair_color: MappedColumn[str] = mapped_column(String)
    height: MappedColumn[str] = mapped_column(String)
    homeworld: MappedColumn[str] = mapped_column(String)
    mass: MappedColumn[str] = mapped_column(String)
    name: MappedColumn[str] = mapped_column(String)
    skin_color: MappedColumn[str] = mapped_column(String)
    species: MappedColumn[list[str] | None] = mapped_column(ARRAY(String))
    starships: MappedColumn[list[str] | None] = mapped_column(ARRAY(String))
    vehicles: MappedColumn[list[str] | None] = mapped_column(ARRAY(String))

async def drop_db_table():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

async def init_orm():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()