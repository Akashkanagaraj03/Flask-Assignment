from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine
import logging


try:
    engine = create_engine("sqlite:///database.db")
except Exception as e:
    logging.critical(f"Error: {e}")
else:
    logging.info("Database connection established")


class Base(DeclarativeBase):
    logging.info("Base model initialised")


# Model for user table
class User(Base):
    logging.info("User model initialised")
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


def main():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error in initialising tables: {e}")
    else:
        logging.info("Tables initialized.")


if __name__ == "__main__":
    main()
