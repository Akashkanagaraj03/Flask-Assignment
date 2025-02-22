# imports for run.py
import logging
from flask import Flask, request, jsonify, session as flask_session, json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from queries import (
    search_users,
    search_user_by_id,
    update_user_by_id,
    delete_user_by_id,
    patch_user_by_id,
    get_user_statistics,
    create_users,
)
from flasgger import Swagger

# setting up logging
logging.basicConfig(
    level=logging.DEBUG,  # available levels - info, debug, warning, error, critical
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format of the log message
    filename="../app.log",  # output to file
)


# connecting to database.db and initialising an engine
try:
    engine = create_engine("sqlite:///../Database/database.db")
except Exception as e:
    logging.critical(f"[__main__] Database connection failed: {e}")
else:
    logging.info("[__main__] Database connection established")


# creating app instance
try:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"  # secret key for JWT
except Exception as e:
    logging.critical(e)
    raise e
else:
    logging.info("[__main__] Flask application initialized")


# setting up api call limits
limiter = Limiter(
    get_remote_address,
    app=app,
)


# setting up api doc
app.config["SWAGGER"] = {
    "title": "Your API Title",
    "uiversion": 3,
    "openapi": "3.0.0",  # Specify the OpenAPI version
    "url": "http://localhost:5000/api",
}

swagger = Swagger(app)


# Method to verify JWT token
def verify_token(token: str, api: str):
    if not token:
        logging.error(f"[{api}] [AUTH]: There is no token attached.")
        return {
            "Error": "Missing or improperly formatted JWT token in the Authorization header."
        }, 400

    # Fetch the token from the header
    token = token.split(" ")[1]  # Assuming it's in the format "Bearer <token>"

    # Decode the key
    try:
        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logging.info(f"[{api}] [AUTH]: Token has expired. Please login again.")
        return {"Error": "Provided Token has expired"}, 401
    except jwt.InvalidTokenError:
        logging.error(f"[{api}] [AUTH]: Provided Token is Invalid.")
        return {"Error": "Provided Token is Invalid"}, 401
    else:
        logging.info(f"[{api}] [AUTH]: Provided Token verified")
        return {"message": "Token is valid"}, 200


# Start of End Points
# default/home page
@app.route("/", methods=["GET"])
@limiter.limit("100 per hour")  # set limiter to 100 per hour
def my_first_app():
    if not flask_session.get("logged_in"):  # check if logged in
        logging.info("[/] User is not logged in")
        return "You are not logged in. Please POST to /login to log in", 401

    return "Welcome!", 200


@app.route("/api", methods=["GET"])
def openapi_spec():
    with open("../openapi3_0.json") as json_file:
        file = json.load(json_file)
    return file, 200


# Run to check JWT Auth
@app.route("/check_auth", methods=["GET"])
@limiter.limit("100 per hour")
def check_auth():
    # Extract JWT token from Authorization header and verify it
    return verify_token(request.headers.get("Authorization"), "/check_auth - GET")


# login page
@app.route("/login", methods=["POST"])
def login():
    payload = request.get_json()
    if payload.get("uid") == "admin" and payload.get("pass") == "1243":
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


# Fetch ALL the users with the specified args
@app.route("/api/users", methods=["GET"])  # to-do
@limiter.limit("10 per hour")
def fetch_users():
    # establish session with db
    session = Session(engine)

    # get args
    page = request.args.get(
        "page", 1, type=int
    )  # args to define the offset of results by page
    limit = request.args.get("limit", 5, type=int)  # limit the output
    sort = request.args.get(
        "sort", "id", type=str
    )  # sort the results based on the arg passed.
    search = request.args.get(
        "search", "", type=str
    )  # search the table using partial first_name, last_name, city

    # fetch user records
    result, code = search_users(session, search, sort, page, limit)
    if code == 200:
        logging.info("[/api/users - GET] Users retrieved successfully")
    else:
        logging.error(
            f"[/api/users - GET] Error while fetching users. Refer queries.py: {result}"
        )

    # close session and return results
    session.close()
    return result, code


# Add ALL the given users to the table
@app.route("/api/users", methods=["POST"])  # to-do
def add_users():
    response, code = verify_token(
        request.headers.get("Authorization"), "/api/users - GET/POST"
    )
    if not code == 200:
        return response, code

    # establish session
    session = Session(engine)

    # fetch the payload
    user_data = request.get_json()

    if user_data is None:
        logging.error("[/api/users - POST] Missing or improperly formatted payload.")
        return (
            jsonify({"error": "Invalid user data (invalid JSON or missing fields)."}),
            400,
        )

    result, code = create_users(user_data, session)

    if code == 200:
        logging.info("[/api/users - POST] Users created successfully")
    else:
        logging.error(
            f"[/api/users - POST] Error while adding users. Refer queries.py: {result}"
        )

    session.close()
    return result, code


# Fetch user with ID : id_
@app.route("/api/users/<int:id_>", methods=["GET"])
@limiter.limit("10 per hour")
def get_user(id_):
    session = Session(engine)
    search, code = search_user_by_id(session, id_)

    if code == 200:
        logging.info(f"[/api/users/{id_} - GET] User retrieved successfully")
    elif code == 404:
        logging.error(f"[/api/users/{id_} - GET] User not found, check your query")
        return jsonify({"error": "User not found."}), 404
    elif code == 500:
        logging.error(f"[/api/users/{id_} - GET] Error while fetching user")
        return jsonify({"error": "Server error while fetching user."}), 500
    else:
        logging.error(f"[/api/users/{id_} - GET] Unknown error code: {code}")
        return jsonify({"error": "Unknown error code"}), code

    session.close()
    return search, 200


# Update ALL the fields of a user with ID : id_
@app.route("/api/users/<int:id_>", methods=["PUT"])
def update_user(id_):
    response, code = verify_token(
        request.headers.get("Authorization"), f"/api/users/{id_} - PUT"
    )
    if not code == 200:
        return response, code

    session = Session(engine)
    user_data = request.get_json()

    if user_data is None:
        logging.error(
            "[/api/users/<id> - PUT] Missing or improperly formatted payload."
        )
        return (
            jsonify({"error": "Invalid user data (invalid JSON or missing fields)."}),
            400,
        )

    response, code = update_user_by_id(session, id_, user_data)

    if code == 200:
        logging.info("[/api/users/<id> - PUT] User updated successfully")
    else:
        logging.error(f"[/api/users/<id> - PUT] Error while updating user: {response}")

    session.close()
    return response, code


# Delete the user with ID : id_
@app.route("/api/users/<int:id_>", methods=["DELETE"])
def delete_user(id_):
    response, code = verify_token(
        request.headers.get("Authorization"), f"/api/users/{id_} - DELETE"
    )
    if not code == 200:
        return response, code

    session = Session(engine)
    result, code = delete_user_by_id(session, id_)
    logging.error("[/api/users/<id> - DELETE] Error while Deleting user")

    if code == 200:
        logging.info("[/api/users/<id> - DELETE] User deleted successfully")
    else:
        logging.error(f"[/api/users/<id> - DELETE] Error while deleting user: {result}")
    session.close()
    return result, code


# Update SOME of the fields of a user with ID : id_
@app.route("/api/users/<int:id_>", methods=["PATCH"])
def patch_user(id_):
    response, code = verify_token(
        request.headers.get("Authorization"), f"/api/users/{id_} - PATCH"
    )
    if not code == 200:
        return response, code

    user_data = request.get_json()

    if user_data is None:
        logging.error("[/api/users/{id} - PATCH] No payload provided")
        return jsonify({"error": "Invalid JSON"}), 400

    session = Session(engine)
    response, code = patch_user_by_id(session, id_, user_data)

    if code == 200:
        logging.info("[/api/users/<id> - PATCH] User updated successfully")

    else:
        logging.error(
            f"[/api/users/<id> - PATCH] Error while updating user: {response}"
        )

    session.close()
    return response, code


# Get summary/stats of the user table
@app.route("/api/summary", methods=["GET"])
@limiter.limit("5 per hour")
def get_statistics():
    if not verify_token(request.headers.get("Authorization"), "/api/summary - GET"):
        return "Invalid token", 401

    logging.info("[/api/summary - GET] Getting statistics for db.")
    session = Session(engine)
    result, code = get_user_statistics(session)
    if code == 200:
        logging.info("[/api/summary - GET] Getting statistics for db success.")
    else:
        logging.error(
            f"[/api/summary - GET] Error while getting statistics for db: {result}"
        )

    # stats fetched:
    # stats = {
    #     "average_age": avg_age,
    #     "total_cities": total_cities,
    #     "total_companies": total_companies,
    #     "count_by_city": [
    #         {"city": city, "user_count": count} for city, count in count_by_city
    #     ],
    #     "count_by_company": [
    #         {"company": company, "user_count": count}
    #         for company, count in count_by_company
    #     ],
    #     "age_ranges": [
    #         {"age_range": range, "user_count": count} for range, count in age_ranges
    #     ],
    # }
    session.close()
    return result, code
