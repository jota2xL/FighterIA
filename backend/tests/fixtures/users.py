"""
Shared user fixture data for tests.
"""

VALID_ALUMNO = {
    "email": "jane.doe@example.com",
    "username": "janedoe",
    "password": "SecurePass123!",
    "full_name": "Jane Doe",
    "account_type": "alumno",
}

VALID_INSTRUCTOR = {
    "email": "sensei.carlos@example.com",
    "username": "sensei_carlos",
    "password": "InstructorPass123!",
    "full_name": "Carlos Sensei",
    "account_type": "instructor",
}

INVALID_SHORT_PASSWORD = {
    "email": "short@example.com",
    "username": "shortpass",
    "password": "abc",
    "full_name": "Short Password",
    "account_type": "alumno",
}

INVALID_EMAIL_FORMAT = {
    "email": "not-an-email",
    "username": "bademail",
    "password": "ValidPass123!",
    "full_name": "Bad Email",
    "account_type": "alumno",
}

INVALID_ACCOUNT_TYPE = {
    "email": "super@example.com",
    "username": "superuser",
    "password": "ValidPass123!",
    "full_name": "Super User",
    "account_type": "superadmin",
}
