from faker import Faker

from app.core.database import SessionLocal
from app.users.models import User
from app.tasks.models import TaskModel

faker = Faker()

def main():
    """
    Generates one fake user and ten fake tasks, and inserts them into the database.

    Steps:
        1. Creates a fake user with a random username and a hashed password.
        2. Generates ten fake tasks associated with that user.
        3. Saves the data to the database using a SQLAlchemy session.

    Notes:
        - The password is securely hashed using the `set_password` method.
        - Tasks have randomly generated titles, descriptions, and completion states.
    """
    db = SessionLocal()

    try:
        user = User(
            username=faker.user_name(),
        )
        user.set_password("test1234")  
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"User created: {user.username}")

        tasks = []
        for _ in range(10):
            task = TaskModel(
                user_id=user.id,
                title=faker.sentence(nb_words=4),
                description=faker.text(max_nb_chars=200),
                is_completed=faker.boolean(chance_of_getting_true=30),
            )
            tasks.append(task)

        db.add_all(tasks)
        db.commit()
        print(f"{len(tasks)} tasks created for user {user.username}")

    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
