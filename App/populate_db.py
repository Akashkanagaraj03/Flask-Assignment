import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import logging
from models import User


try:
    engine = create_engine("sqlite:///../Database/database.db")
    session = Session(engine)
except Exception as e:
    logging.critical(f"[__main__] Database connection failed: {e}")
else:
    logging.info("[__main__] Database connection established")


def main():
    with open("../Database/Sources/users.json") as file:
        users = json.load(file)
        for user in users:
            create_user(
                session,
                user["id"],
                user["first_name"],
                user["last_name"],
                user["company_name"],
                user["city"],
                user["state"],
                user["zip"],
                user["email"],
                user["web"],
                user["age"],
            )


def create_user(
    session,
    id_,
    first_name,
    last_name,
    company_name,
    city,
    state,
    zip_,
    email,
    web,
    age,
):
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
            session.commit()
        except Exception as e:
            logging.error(f"Error: {e}")
            session.rollback()

        else:
            logging.info("Data with user id:{id} created.")

        finally:
            session.close()

    return


if __name__ == "__main__":
    main()
