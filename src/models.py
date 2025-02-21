from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine
import logging

# Set up basic configuration
logging.basicConfig(
    level=logging.DEBUG,  # available levels - info, debug, warning, error, critical
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of the log message
    filename="app.log",  # output to file
)


try:
    engine = create_engine("sqlite:///src/database.db")
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


def create_user(
    id_, first_name, last_name, company_name, city, state, zip_, email, web, age
):
    session = Session(engine)
    with session.begin():
        try:
            session.add(
                User(
                    id=id_,
                    first_name=first_name,
                    last_name=last_name,
                    company_name=company_name,
                    city=city,
                    state=state,
                    zip=zip_,
                    email=email,
                    web=web,
                    age=age,
                )
            )
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error:{e}")
            session.rollback()

        else:
            session.commit()

        finally:
            session.close()
            logging.info("Data with user id:{id} created.")
    return


def main():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error in initialising tables: {e}")
    else:
        logging.info("Tables initialized.")


if __name__ == "__main__":
    main()
