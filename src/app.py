# imports
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import create_user
from queries import search_users, search_user_by_id
import logging

# Set up basic configuration
logging.basicConfig(
    level=logging.DEBUG,  # available levels - info, debug, warning, error, critical
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of the log message
)

# connecting to database.db and creating a session
try:
    engine = create_engine("sqlite:///src/database.db")
    session = Session(engine)
except Exception as e:
    logging.critical(f"[__main__] Database connection failed: {e}")
else:
    logging.info("[__main__] Database connection established")


# create app instance
# to-do add commits
try:
    app = Flask(__name__)
except Exception as e:
    logging.error(e)
    raise e
else:
    logging.info("[__main__] Flask application initialized")


# default page
@app.route("/", methods=["GET"])
def my_first_app():
    return "Application is running"


# API for fetching/creating user records
@app.route("/api/users", methods=["GET", "POST"])
def users():
    if request.method == "GET":  # log
        # get args
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 5, type=int)
        sort = request.args.get("sort", "id", type=str)
        search = request.args.get("search", "", type=str)

        with session.begin():
            try:
                # fetch user records
                users, code = search_users(session, search, sort, page, limit)

            except Exception as e:
                logging.error(f"[/api/users - GET] Error while fetching users: {e}")
                session.rollback()
                return jsonify({"Error": "Something went wrong, refer logs"}), 500

            else:
                if code == 200:
                    logging.info("[/api/users - GET] Users retrieved successfully")
                else:
                    logging.error(
                        "[/api/users - GET] Error while fetching users. Refer queries.py"
                    )
                return users, code

    elif request.method == "POST":  # to-do implement if user already exists
        user_data = request.get_json()

        if user_data is None:
            logging.error("[/api/users - POST] No user data provided")
            return jsonify({"error": "Invalid JSON"}), 400

        try:
            for user in user_data:
                create_user(
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
        except Exception as e:
            logging.error(f"[/api/users - POST] Error while creating user: {e}")
            return jsonify({"Error": "Something went wrong, refer logs"}), 500
        else:
            logging.info("[/api/users - POST] User created successfully")
            return jsonify({"message": "Data received successfully!"}), 200


@app.route("/api/users/<int:id>", methods=["GET"])
def get_user_by_id(id):
    try:
        search, code = search_user_by_id(session, id)
    except Exception as e:
        logging.error(f"[/api/users/<id> - GET] Error while fetching user: {e}")
        return jsonify({"Error": "Something went wrong, refer logs"}), 500
    else:
        if code == 200:
            logging.info("[/api/users/<id> - GET] User retrieved successfully")
        else:
            logging.error(
                "[/api/users/<id> - GET] Error while fetching user. Check queries.py"
            )
        return search, code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
