from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine

engine = create_engine("sqlite:///database.db")


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


def create_user(
    id, first_name, last_name, company_name, city, state, zip, email, web, age
):
    session = Session(engine)
    with session.begin():
        try:
            session.add(
                User(
                    id=id,
                    first_name=first_name,
                    last_name=last_name,
                    company_name=company_name,
                    city=city,
                    state=state,
                    zip=zip,
                    email=email,
                    web=web,
                    age=age,
                )
            )
        except Exception as e:
            print(f"Error:{e}")
            session.rollback()

        else:
            session.commit()
            print(f"Data with user id:{id} created.")

        finally:
            session.close()
    return


def main():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
