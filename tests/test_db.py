from dataclasses import asdict

from sqlalchemy import select

from api.models import User


def test_model_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Maria Eduarda', email='ms.mariasilva@gmail.com', password='123456'
        )

        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'Maria Eduarda'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Maria Eduarda',
        'email': 'ms.mariasilva@gmail.com',
        'password': '123456',
        'created_at': time,
        'update_at': time,
    }
