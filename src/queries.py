from flask import jsonify, Response
from sqlalchemy import or_, asc, desc, func, case
from sqlalchemy.orm import Session, Query
from models import User
import logging

# Set up basic configuration
logging.basicConfig(
    level=logging.DEBUG,  # available levels - info, debug, warning, error, critical
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of the log message
    filename="queries.log",  # output to file
)


def build_json_user(user):
    json = jsonify({})
    try:
        json = jsonify(
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

    except Exception as e:
        logging.error(f"Error when building json for single user: {e}")
    else:
        logging.info(f"Successfully built json for single user: {user.id}")
    finally:
        return json


def build_json_users(query: Query) -> Response:
    user_list = []
    json = jsonify({})
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

    try:
        json = jsonify(user_list)
    except Exception as e:
        logging.error(f"Error when building json for users: {e}")

    else:
        logging.info(f"Successfully built json for users: {len(user_list)}")

    finally:
        return json


def search_users(
    session: Session, search: str = "", sort: str = "id", page: int = 1, limit: int = 5
) -> tuple[Response, int]:
    logging.info("Searching users")
    query = session.query(User)
    if not search == "":
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.city.ilike(f"%{search}%"),
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
        logging.info(f"Invalid sort field: '{sort}', using ID(ASC) instead.")
        sort_column = getattr(User, "id")
        order = asc

    query = query.order_by(order(sort_column))
    query = query.offset((page - 1) * limit).limit(limit)

    query.all()

    if query.count() == 0:
        logging.info("No users found.")
        return jsonify({"message": "No users found"}), 404

    logging.info(f"Found {query.count()} users")
    return build_json_users(query), 200


def search_user_by_id(session: Session, id: int) -> tuple[Response, int]:
    query = session.query(User)
    query = query.filter(User.id == id).first()

    if not query:
        logging.info(f"No user with id {id} found.")
        return jsonify({"message": "No users found"}), 404

    logging.info(f"User with id {id} found.")
    return build_json_user(query), 200


def update_user_by_id(
    session: Session, id: int, new_user: dict
) -> tuple[Response, int]:
    old_user = session.query(User).filter(User.id == id).first()

    if not old_user:
        logging.info(f"No user with id {id} found.")
        return (
            jsonify(
                {
                    "message": "No users found with the given id. Try creating a new user instead."
                }
            ),
            404,
        )

    try:
        old_user.first_name = new_user.get("first_name")
        old_user.last_name = new_user.get("last_name")
        old_user.company_name = new_user.get("company_name")
        old_user.city = new_user.get("city")
        old_user.state = new_user.get("state")
        old_user.zip = new_user.get("zip")
        old_user.email = new_user.get("email")
        old_user.web = new_user.get("web")
        old_user.age = new_user.get("age")

    except Exception as e:
        logging.error(f"Error when updating user: {e}")
        return jsonify({"message": f"Error: {e}"}), 404

    else:
        session.add(old_user)
        session.commit()
        logging.info(f"Successfully updated user: {old_user.id}")
        return build_json_user(old_user), 200


def delete_user_by_id(session: Session, id: int) -> tuple[Response, int]:
    try:
        query = session.query(User)
        if not query:
            raise Exception("No users found with the given id.")
        query = query.filter(User.id == id).first()
        session.delete(query)

    except Exception as e:
        logging.error(f"Error when deleting user: {e}")
        return jsonify({"message": f"Error when Deleting: {e}"}), 404

    else:
        session.commit()
        logging.info(f"Successfully deleted user: {id}")

    return jsonify({"message": "User successfully deleted."}), 200


def patch_user_by_id(session: Session, id: int, new_user: dict) -> tuple[Response, int]:
    old_user = session.query(User).filter(User.id == id).first()

    if not old_user:
        logging.info(f"No user with id {id} found.")
        return (
            jsonify(
                {
                    "message": "No users found with the given id. Try creating a new user instead."
                }
            ),
            404,
        )

    try:
        if "first_name" in new_user:
            old_user.first_name = new_user.get("first_name")
        if "last_name" in new_user:
            old_user.last_name = new_user.get("last_name")
        if "company_name" in new_user:
            old_user.company_name = new_user.get("company_name")
        if "city" in new_user:
            old_user.city = new_user.get("city")
        if "state" in new_user:
            old_user.state = new_user.get("state")
        if "zip" in new_user:
            old_user.zip = new_user.get("zip")
        if "email" in new_user:
            old_user.email = new_user.get("email")
        if "web" in new_user:
            old_user.web = new_user.get("web")
        if "age" in new_user:
            old_user.age = new_user.get("age")

    except Exception as e:
        logging.error(f"Error when patching user: {e}")
        return jsonify({"message": f"Error: {e}"}), 404

    else:
        session.add(old_user)
        session.commit()
        logging.info(f"Successfully updated user: {old_user.id}")
        return build_json_user(old_user), 200


def get_user_statistics(session: Session) -> tuple[Response, int]:
    count_by_city = (
        session.query(User.city, func.count(User.id).label("user_count"))
        .group_by(User.city)
        .all()
    )

    count_by_company = (
        session.query(User.company_name, func.count(User.id).label("user_count"))
        .group_by(User.company_name)
        .all()
    )

    avg_age = session.query(func.avg(User.age)).scalar()

    total_cities = session.query(func.count(func.distinct(User.city))).scalar()

    total_companies = session.query(
        func.count(func.distinct(User.company_name))
    ).scalar()

    age_ranges = (
        session.query(
            case(
                (User.age.between(0, 18), "0-18"),
                (User.age.between(19, 30), "19-30"),
                (User.age.between(31, 45), "31-45"),
                (User.age.between(46, 60), "46-60"),
                (User.age > 60, "60+"),
                else_="Unknown",
            ).label("age_range"),
            func.count(User.id).label("user_count"),
        )
        .group_by("age_range")
        .all()
    )

    stats = {
        "average_age": avg_age,
        "total_cities": total_cities,
        "total_companies": total_companies,
        "count_by_city": [
            {"city": city, "user_count": count} for city, count in count_by_city
        ],
        "count_by_company": [
            {"company": company, "user_count": count}
            for company, count in count_by_company
        ],
        "age_ranges": [
            {"age_range": range, "user_count": count} for range, count in age_ranges
        ],
    }

    logging.info("Statistics fetched.")
    return jsonify(stats), 200
