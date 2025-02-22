# imports for run.py
import logging
from flask import Flask, request, jsonify, session as flask_session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
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

# setting up swagger
# Swagger definition for the User schema
app.config["SWAGGER"] = {
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "User ID"},
                "first_name": {"type": "string", "description": "User first name"},
                "last_name": {"type": "string", "description": "User last name"},
                "company_name": {"type": "string", "description": "User company name"},
                "city": {"type": "string", "description": "User city"},
                "state": {"type": "string", "description": "User state"},
                "zip": {"type": "string", "description": "User zip code"},
                "email": {"type": "string", "description": "User email address"},
                "web": {"type": "string", "description": "User web address"},
                "age": {"type": "integer", "description": "User age"},
            },
            "required": [],  # You can add required fields here, e.g., ['first_name', 'last_name', 'email']
        }
    }
}
swagger = Swagger(app)


@app.route("/apidocs/")
def apidocs():
    """This endpoint is used to view the Swagger UI."""
    return "Swagger UI should be visible here"


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
    """End Point fetches our login status
    ---
    tags:
    - Auth
    summary: Get the login status of the user
    description: This endpoint checks whether the user is logged in or not.
    responses:
      200:
        description: The user is logged in and the welcome message is returned.
      401:
        description: User is not logged in, prompts to log in via POST to /login.
    """
    if not flask_session.get("logged_in"):  # check if logged in
        logging.info("[/] User is not logged in")
        return "You are not logged in. Please POST to /login to log in", 401

    return "Welcome!", 200


# Run to check JWT Auth
@app.route("/check_auth", methods=["GET"])
@limiter.limit("100 per hour")
def check_auth():
    """Endpoint to check JWT authentication status
    ---
    tags:
      - Auth
    summary: Check JWT authentication
    description: This endpoint verifies the validity of the JWT token passed in the Authorization header.
    parameters:
      - in: header
        name: Authorization
        required: true
        description: JWT token in the Authorization header to verify authentication.
        schema:
          type: string
    responses:
      200:
        description: The JWT token is valid, authentication is successful.
      401:
        description: Invalid or expired JWT token, authentication failed.
      400:
        description: Missing or improperly formatted JWT token in the Authorization header.
    """
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
    """
    Endpoint to fetch user records with support for pagination, sorting, and searching
    ---
    tags:
      - Users
    summary: Fetch user records
    description: This endpoint retrieves user records with options for pagination, sorting, and searching by first_name, last_name, or city.
    parameters:
      - in: query
        name: page
        required: false
        description: Page number for paginated results.
        schema:
          type: integer
          default: 1
      - in: query
        name: limit
        required: false
        description: Number of results per page.
        schema:
          type: integer
          default: 5
      - in: query
        name: sort
        required: false
        description: Field to sort by (can include "-" for descending order, e.g., "-age").
        schema:
          type: string
          default: "id"
      - in: query
        name: search
        required: false
        description: Partial text to search users by first_name, last_name, or city.
        schema:
          type: string
          default: ""
    responses:
      200:
        description: Users retrieved successfully
      400:
        description: Bad request due to missing or invalid parameters.
      500:
        description: Server error while retrieving users."""
    # Fetches all the rows from the "user" table from the database

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
    """
    Endpoint to create a new user record
    ---
    tags:
      - Users
    summary: Create a new user
    description: This endpoint allows the creation of new user records. The user data is passed in the body, and authorization is required through the Authorization header.
    parameters:
      - in: header
        name: Authorization
        required: true
        description: Authorization token for access control.
        schema:
          type: string
      - in: body
        name: user_data
        required: true
        description: List of user objects to create new users.
        schema:
          type: array
          items:
            $ref: '#/definitions/User'
    responses:
      200:
        description: User created successfully
        schema:
          type: array
          items:
            $ref: '#/definitions/User'
      400:
        description: Invalid user data (invalid JSON or missing fields).
      401:
        description: Unauthorized access due to invalid or missing token.
      500:
        description: Server error while creating the user."""

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
    return jsonify(result), code


# Fetch user with ID : id_
@app.route("/api/users/<int:id_>", methods=["GET"])
@limiter.limit("10 per hour")
def get_user(id_):
    """
    Fetches a user record by ID.
    ---
    tags:
      - Users
    description: Fetches a user record by ID.
    parameters:
      - name: id_
        in: path
        type: integer
        required: true
        description: ID of the user to retrieve.
      - name: Authorization
        in: header
        type: string
        required: true
        description: Authorization token for access control.
    responses:
      200:
        description: User retrieved successfully
        schema:
          $ref: '#/definitions/User'
      401:
        description: Unauthorized due to invalid token.
      404:
        description: User not found.
      500:
        description: Server error while retrieving user.
    """

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
    return jsonify(search), 200


# Update ALL the fields of a user with ID : id_
@app.route("/api/users/<int:id_>", methods=["PUT"])
def update_user(id_):
    """
    Updates an existing user by their ID.
    ---
    tags:
      - Users
    description: Updates an existing user record by their ID.
    parameters:
      - name: id_
        in: path
        type: integer
        required: true
        description: ID of the user to update.
      - name: Authorization
        in: header
        type: string
        required: true
        description: Authorization token for access control.
      - name: user_data
        in: body
        type: object
        required: true
        description: User data to update the existing user.
        schema:
          $ref: '#/definitions/User'
    responses:
      200:
        description: User updated successfully
        schema:
          $ref: '#/definitions/User'
      400:
        description: Invalid user data (invalid JSON or missing fields).
      401:
        description: Unauthorized access due to invalid or missing token.
      404:
        description: User not found.
      500:
        description: Server error while updating the user."""

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
    """
    Deletes a user record by ID.
    ---
    tags:
      - Users
    description: Deletes a user record by their ID.
    parameters:
      - name: id_
        in: path
        type: integer
        required: true
        description: ID of the user to delete.
      - name: Authorization
        in: header
        type: string
        required: true
        description: Authorization token for access control.
    responses:
      200:
        description: User deleted successfully
      401:
        description: Unauthorized access due to invalid or missing token.
      404:
        description: User not found.
      500:
        description: Server error while deleting the user.
    """
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
    """
    Updates specific fields of an existing user by their ID.
    ---
    tags:
      - Users
    description: Updates selected fields of a user record by their ID.
    parameters:
      - name: id_
        in: path
        type: integer
        required: true
        description: ID of the user to update.
      - name: Authorization
        in: header
        type: string
        required: true
        description: Authorization token for access control.
      - name: user_data
        in: body
        type: object
        required: true
        description: User data with the fields to be updated.
        schema:
          $ref: '#/definitions/User'
    responses:
      200:
        description: User updated successfully
        schema:
          $ref: '#/definitions/User'
      400:
        description: Invalid user data (invalid JSON or missing fields).
      401:
        description: Unauthorized access due to invalid or missing token.
      404:
        description: User not found.
      500:
        description: Server error while updating the user.
    """

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
    """
    Retrieves statistics about the users in the database.
    ---
    tags:
      - Users
    description: Fetches statistics for the users in the database, including data like average age, city and company counts, and age ranges.
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Authorization token for access control.
    responses:
      200:
        description: Statistics retrieved successfully
        schema:
          type: object
          properties:
            average_age:
              type: number
              description: The average age of the users.
            total_cities:
              type: integer
              description: Total number of unique cities.
            total_companies:
              type: integer
              description: Total number of unique companies.
            count_by_city:
              type: array
              items:
                type: object
                properties:
                  city:
                    type: string
                    description: The name of the city.
                  user_count:
                    type: integer
                    description: The count of users from that city.
            count_by_company:
              type: array
              items:
                type: object
                properties:
                  company:
                    type: string
                    description: The name of the company.
                  user_count:
                    type: integer
                    description: The count of users working at that company.
            age_ranges:
              type: array
              items:
                type: object
                properties:
                  age_range:
                    type: string
                    description: The age range.
                  user_count:
                    type: integer
                    description: The count of users within that age range.
      401:
        description: Unauthorized due to invalid token.
      500:
        description: Server error while fetching statistics.
    """

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
