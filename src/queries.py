from flask import jsonify, Response
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Session, Query
from models import User

# engine = create_engine("sqlite:///database.db")


def build_json_user(user):
    return jsonify(
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company_name": user.company_name,
            "city": user.city,
            "state": user.state,
            "zip": user.zip,
            "email": user.email,
            "web": user.web,
            "age": user.age,
        }
    )


def build_json_users(query: Query) -> Response:
    user_list = []
    for user in query:
        print(user)
        user_list.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company_name": user.company_name,
                "city": user.city,
                "state": user.state,
                "zip": user.zip,
                "email": user.email,
                "web": user.web,
                "age": user.age,
            }
        )
    return jsonify(user_list)


def search_users(
    session: Session, search: str = "", sort: str = "id", page: int = 1, limit: int = 5
) -> tuple[Response, int]:
    query = session.query(User)
    if not search == "":
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
            )
        )

    if sort.startswith("-"):
        sort = sort[1:]
        order = desc
    else:
        order = asc

    try:
        sort_column = getattr(User, sort)

    except AttributeError:
        print(f"Invalid sort field: '{sort}', using ID(ASC) instead.")
        sort_column = getattr(User, "id")
        order = asc

    query = query.order_by(order(sort_column))
    query = query.offset((page - 1) * limit).limit(limit)

    query.all()

    if query.count() == 0:
        return jsonify({"message": "No users found"}), 404

    return build_json_users(query), 200


def search_user_by_id(session: Session, id: int) -> tuple[Response, int]:
    query = session.query(User)
    query = query.filter(User.id == id).first()

    if not query:
        return jsonify({"message": "No users found"}), 404

    return build_json_user(query), 200
