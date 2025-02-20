import json
from models import create_user


def main():
    with open("users.json") as file:
        users = json.load(file)
        for user in users:
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


if __name__ == "__main__":
    main()
