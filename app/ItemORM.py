from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column

engine = create_engine('sqlite:///500database.db')

class Base(DeclarativeBase):
    pass

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

class MoviesORM(Base):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column('id', primary_key=True)
    title: Mapped[str] = mapped_column('title')
    original_title: Mapped[str] = mapped_column('original_title')
    year: Mapped[int] = mapped_column('year')
    desc: Mapped[str] = mapped_column('desc')