# main.py
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository
from services.user_service import UserService  # ← Changed from business to services

def main():
    # 1️⃣ Initialize DB connection
    db = DatabaseConnection()
    connection = db.connect()

    if not connection:
        print("Cannot proceed without DB connection.")
        return

    # 2️⃣ Initialize Repositories
    user_repo = UserRepository(connection)

    # 3️⃣ Initialize Services
    user_service = UserService(user_repo)

    # 4️⃣ Test creating a user
    try:
        new_user = user_service.add_user(
            name="Ali Shahzad",
            email="ali@example.com",
            phone="03001234567",
            location="Karachi",
            latitude=24.8607,
            longitude=67.0011,
            language="en",
            role="Volunteer",
            password_hash="hashed_password"
        )
        print("✅ User added successfully")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 5️⃣ Fetch all users
    users = user_service.list_users()
    print("All Users in DB:")
    for u in users:
        print(u)

    # 6️⃣ Close DB connection
    db.close()

if __name__ == "__main__":
    main()