from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from dependencies import password

engine = create_engine(f'postgresql+psycopg2://postgres:{password}@localhost:5432/movies_500')

class Base(DeclarativeBase):
    pass

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

class MovieORM(Base):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column('id', primary_key=True)
    title: Mapped[str] = mapped_column('title')
    original_title: Mapped[str] = mapped_column('original_title')
    year: Mapped[int] = mapped_column('year')
    desc: Mapped[str] = mapped_column('description')

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column('id', primary_key=True)
    email: Mapped[str] = mapped_column('email')
    username: Mapped[str] = mapped_column('username')
    password: Mapped[str] = mapped_column('password')