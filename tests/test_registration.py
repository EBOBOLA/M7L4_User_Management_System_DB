import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

def test_successful_authentication(setup_database, connection):
    test_username = "auth_user"
    test_email = "auth@example.com"
    test_password = "secure_password"
    
    add_user(test_username, test_email, test_password)
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (test_username,))
    user_exists = cursor.fetchone()
    assert user_exists is not None
    
    auth_result = authenticate_user(test_username, test_password)
    
    assert auth_result is True

def test_failed_authentication_wrong_password(setup_database):
    """Тест неудачной аутентификации с неправильным паролем"""
    test_username = "auth_user2"
    test_password = "right_password"
    wrong_password = "wrong_password"
    
    add_user(test_username, "auth2@example.com", test_password)
    
    auth_result = authenticate_user(test_username, wrong_password)
    assert auth_result is False

def test_authentication_nonexistent_user(setup_database, connection):
    """Тест аутентификации несуществующего пользователя"""
    non_existent_user = "ghost_user"
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (non_existent_user,))
    assert cursor.fetchone() is None
    
    auth_result = authenticate_user(non_existent_user, "any_password")
    
    assert auth_result is False
    
    cursor.execute("SELECT * FROM users WHERE username=?", (non_existent_user,))
    assert cursor.fetchone() is None


@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."



# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""