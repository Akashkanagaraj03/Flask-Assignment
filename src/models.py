from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    company_name: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    zip: Mapped[int] = mapped_column()
    email: Mapped[str] = mapped_column()
    web: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()


engine = create_engine("sqlite:///database.db", echo=True)
Base.metadata.create_all(engine)
