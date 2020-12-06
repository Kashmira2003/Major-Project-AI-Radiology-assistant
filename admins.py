from radiology_assistant import create_app
from radiology_assistant import db
from radiology_assistant.models import User
import argparse


if __name__ == "__main__":
    app = create_app()
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add_admin", required=False, type=str, help="Add a user as an admin. Ex: --add_admin {username}")
    parser.add_argument("-r", "--remove_admin", required=False, type=str, help="Remove a user as an admin. Ex: --remove_admin {username}")
    args = parser.parse_args()

    if args.add_admin:
        with app.app_context():
            user = User.query.filter_by(username=args.add_admin).first()
            if user:
                user.admin = True
                db.session.commit()
                print(f"User {user.username} added as admin.")
            else:
                print(f"Could not find user {user.username}.")
    elif args.remove_admin:
        with app.app_context():
            user = User.query.filter_by(username=args.remove_admin).first()
            if user:
                user.admin = False
                db.session.commit()
                print(f"User {user.username} removed as admin.")
            else:
                print(f"Could not find user {user.username}.")
    else:
        print("Error: No arguments provided. Please provide one of the two options.")
