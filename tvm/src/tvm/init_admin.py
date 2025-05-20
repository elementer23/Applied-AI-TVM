from getpass import getpass

from authentication import get_password_hash, SessionLocal, User


def create_admin():
    db = SessionLocal()

    print("Create initial admin user")

    username = input("Enter admin username: ").strip()
    if db.query(User).filter(User.username == username).first():
        print("Username already exists.")
        db.close()
        return

    password = getpass("Enter admin password: ").strip()
    confirm_password = getpass("Confirm password: ").strip()

    if password != confirm_password:
        print("Passwords do not match.")
        db.close()
        return

    hashed_password = get_password_hash(password)
    admin_user = User(username=username, hashed_password=hashed_password, role="admin")
    db.add(admin_user)
    db.commit()
    db.close()
    print(f"Admin user '{username}' created successfully.")


if __name__ == "__main__":
    create_admin()
