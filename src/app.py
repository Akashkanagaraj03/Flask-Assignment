# imports
from flask import Flask, request, jsonify, session as flask_session
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import create_user
from queries import (
    search_users,
    search_user_by_id,
    update_user_by_id,
    delete_user_by_id,
    patch_user_by_id,
    get_user_statistics,
)
import logging

# Set up basic configuration
logging.basicConfig(
    level=logging.DEBUG,  # available levels - info, debug, warning, error, critical
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of the log message
    filename="app.log",  # output to file
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
    app.config["SECRET_KEY"] = "secret"
except Exception as e:
    logging.error(e)
    raise e
else:
    logging.info("[__main__] Flask application initialized")


# default page
@app.route("/", methods=["GET"])
def my_first_app():
    if not flask_session.get("logged_in"):
        logging.info("[/] User not logged in")
        return "POST to /login to log in", 401

    return "Logged in", 200


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.args.get("uid") == "admin" and request.args.get("pass") == "1243":
        flask_session["logged_in"] = True
        token = jwt.encode(
            {"user": request.args.get("uid")},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        logging.info("[/login] Logged in")
        return jsonify({"token": token})

    else:
        flask_session["logged_in"] = False
        logging.info("[/login] Failed to log in, check credentials")
        return "Failed to log in", 401


# Method to verify JWT token
def verify_token(token: str, api: str):
    if not token:
        logging.error(f"[{api}] [AUTH]: Token not found")
        return False

    token = token.split(" ")[1]  # Assuming it's in the format "Bearer <token>"

    try:
        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logging.error(f"[{api}] [AUTH]: Expired Token")
        return False
    except jwt.InvalidTokenError:
        logging.error(f"[{api}] [AUTH]: Invalid Token")
        return False
    else:
        logging.info(f"[{api}] [AUTH]: Token verified")
        return True


# dummy api to check JWT auth
@app.route("/check_auth", methods=["GET", "POST"])
def check_auth():
    # Extract token from Authorization header
    if verify_token(request.headers.get("Authorization"), "/check_auth - GET/POST"):
        return "Success", 200
    else:
        return "Invalid token", 401


# API for fetching/creating user records
@app.route("/api/users", methods=["GET", "POST"])
def users():
    if not verify_token(request.headers.get("Authorization"), "/api/users - GET/POST"):
        return "Invalid token", 401

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
def get_user(id):
    if not verify_token(request.headers.get("Authorization"), f"/api/users/{id} - GET"):
        return "Invalid token", 401

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
                f"f[/api/users/<id> - GET] Error while fetching user. Check queries.py : {search}"
            )
        return search, code


@app.route("/api/users/<int:id>", methods=["PUT"])
def update_user(id):
    if not verify_token(request.headers.get("Authorization"), f"/api/users/{id} - PUT"):
        return "Invalid token", 401

    user_data = request.get_json()

    if user_data is None:
        logging.error("[/api/users/{id} - [PUT] No payload provided")
        return jsonify({"error": "Invalid JSON"}), 400

    response, code = update_user_by_id(session, id, user_data)

    if code == 200:
        logging.info("[/api/users/<id> - PUT] User updated successfully")
        return response, code
    else:
        logging.error(f"[/api/users/<id> - PUT] Error while updating user: {response}")
        return response, code


@app.route("/api/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    if not verify_token(
        request.headers.get("Authorization"), f"/api/users/{id} - DELETE"
    ):
        return "Invalid token", 401

    try:
        result, code = delete_user_by_id(session, id)

    except Exception as e:
        logging.error(f"[/api/users/<id> - DELETE] Error while Deleting user: {e}")
        return jsonify({"Error": "Something went wrong, refer logs"}), 500

    else:
        if code == 200:
            logging.info("[/api/users/<id> - DELETE] User deleted successfully")
            return result, code
        else:
            logging.error(
                f"[/api/users/<id> - DELETE] Error while deleting user: {result}"
            )
            return result, code


@app.route("/api/users/<int:id>", methods=["PATCH"])
def patch_user(id):
    if not verify_token(
        request.headers.get("Authorization"), f"/api/users/{id} - PATCH"
    ):
        return "Invalid token", 401

    user_data = request.get_json()

    if user_data is None:
        logging.error("[/api/users/{id} - PATCH] No payload provided")
        return jsonify({"error": "Invalid JSON"}), 400

    response, code = patch_user_by_id(session, id, user_data)

    if code == 200:
        logging.info("[/api/users/<id> - PATCH] User updated successfully")
        return response, code
    else:
        logging.error(
            f"[/api/users/<id> - PATCH] Error while updating user: {response}"
        )
        return response, code


@app.route("/api/summary", methods=["GET"])
def get_statistics():
    if not verify_token(request.headers.get("Authorization"), "/api/summary - GET"):
        return "Invalid token", 401

    logging.info("[/api/summary - GET] Getting statistics for db.")
    return get_user_statistics(session)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
