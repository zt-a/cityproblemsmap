# tests/test_auth.py

from unittest.mock import patch


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL    = "/api/v1/auth/login"
REFRESH_URL  = "/api/v1/auth/refresh"

VALID_USER = {
    "username": "zhyrgal",
    "email":    "zt20061113@gmail.com",
    "password": "password123",
    "city":     "Bishkek",
}


class TestRegister:

    def test_register_success(self, client):
        """Успешная регистрация возвращает токены и данные юзера."""
        response = client.post(REGISTER_URL, json=VALID_USER)

        assert response.status_code == 201
        data = response.json()

        assert "access_token"  in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == VALID_USER["username"]
        assert data["user"]["city"]     == VALID_USER["city"]

    def test_register_duplicate_email(self, client):
        """Повторная регистрация с тем же email — 409."""
        client.post(REGISTER_URL, json=VALID_USER)
        response = client.post(REGISTER_URL, json=VALID_USER)

        assert response.status_code == 409
        assert "Email" in response.json()["detail"]

    def test_register_duplicate_username(self, client):
        """Повторный username — 409."""
        client.post(REGISTER_URL, json=VALID_USER)
        response = client.post(REGISTER_URL, json={
            **VALID_USER,
            "email": "other@test.com",   # другой email но тот же username
        })
        assert response.status_code == 409

    def test_register_short_password(self, client):
        """Пароль меньше 8 символов — 422."""
        response = client.post(REGISTER_URL, json={
            **VALID_USER,
            "password": "123",
        })
        assert response.status_code == 422

    def test_register_short_username(self, client):
        """Username меньше 3 символов — 422."""
        response = client.post(REGISTER_URL, json={
            **VALID_USER,
            "username": "ab",
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Невалидный email — 422."""
        response = client.post(REGISTER_URL, json={
            **VALID_USER,
            "email": "notanemail",
        })
        assert response.status_code == 422


class TestLogin:

    def test_login_success(self, client):
        """Успешный логин возвращает токены."""
        client.post(REGISTER_URL, json=VALID_USER)
        response = client.post(LOGIN_URL, json={
            "email":    VALID_USER["email"],
            "password": VALID_USER["password"],
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token"  in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client):
        """Неверный пароль — 401."""
        client.post(REGISTER_URL, json=VALID_USER)
        response = client.post(LOGIN_URL, json={
            "email":    VALID_USER["email"],
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_email(self, client):
        """Несуществующий email — 401."""
        response = client.post(LOGIN_URL, json={
            "email":    "nobody@test.com",
            "password": "password123",
        })
        assert response.status_code == 401


class TestRefresh:

    def test_refresh_success(self, client):
        """Обновление access токена через refresh токен."""
        reg = client.post(REGISTER_URL, json=VALID_USER).json()
        response = client.post(REFRESH_URL, json={
            "refresh_token": reg["refresh_token"]
        })

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_invalid_token(self, client):
        """Невалидный refresh токен — 401."""
        response = client.post(REFRESH_URL, json={
            "refresh_token": "invalid.token.here"
        })
        assert response.status_code == 401

    def test_refresh_with_access_token(self, client):
        """Access токен не работает как refresh — 401."""
        reg = client.post(REGISTER_URL, json=VALID_USER).json()
        response = client.post(REFRESH_URL, json={
            "refresh_token": reg["access_token"]  # намеренно передаём access
        })
        assert response.status_code == 401

class TestLogout:

    def test_logout_success(self, client):
        """Успешный logout инвалидирует refresh токен."""
        reg = client.post(REGISTER_URL, json=VALID_USER).json()

        response = client.post("/api/v1/auth/logout", json={
            "refresh_token": reg["refresh_token"]
        })
        assert response.status_code == 200
        assert "Выход" in response.json()["message"]

    def test_logout_blacklists_token(self, client):
        """
        После logout refresh токен не работает.
        Попытка refresh — 401.
        """
        reg = client.post(REGISTER_URL, json=VALID_USER).json()

        # Logout
        client.post("/api/v1/auth/logout", json={
            "refresh_token": reg["refresh_token"]
        })

        # Попытка использовать тот же токен
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": reg["refresh_token"]
        })
        assert response.status_code == 401

    def test_logout_invalid_token(self, client):
        """Невалидный токен при logout — 200 (не раскрываем ошибку)."""
        response = client.post("/api/v1/auth/logout", json={
            "refresh_token": "invalid.token.here"
        })
        assert response.status_code == 200


class TestChangePassword:

    def test_change_password_success(self, client, registered_user, auth_headers):
        """Успешная смена пароля."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "password123",
                "new_password": "newpassword456",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "изменён" in response.json()["message"]

    def test_change_password_wrong_old(self, client, auth_headers):
        """Неверный старый пароль — 400."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword456",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_change_password_same(self, client, auth_headers):
        """Новый пароль совпадает со старым — 400."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "password123",
                "new_password": "password123",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_change_password_unauthorized(self, client):
        """Без токена — 401."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "password123",
                "new_password": "newpassword456",
            },
        )
        assert response.status_code == 401

    def test_change_password_short_new(self, client, auth_headers):
        """Новый пароль меньше 8 символов — 422."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "password123",
                "new_password": "123",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_new_password_works_for_login(self, client, registered_user):
        """После смены пароля — логин работает с новым паролем."""
        # Смена пароля
        client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "password123",
                "new_password": "newpassword456",
            },
            headers={'Authorization': f'Bearer {registered_user["access_token"]}'},
        )

        # Логин с новым паролем
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["user"]["email"],
            "password": "newpassword456",
        })
        assert response.status_code == 200

        # Логин со старым паролем — 401
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["user"]["email"],
            "password": "password123",
        })
        assert response.status_code == 401

class TestForgotPassword:

    def test_forgot_password_existing_email(self, client, registered_user):
        """
        Запрос сброса для существующего email.
        Всегда 200 — не раскрываем существует ли email.
        Email отправка замокана.
        """
        user_email = registered_user["user"]["email"]  # используем реальный email из fixture

        with patch("app.api.v1.auth.send_reset_password_email") as mock_email:
            response = client.post("/api/v1/auth/forgot-password", json={
                "email": user_email
            })
            assert response.status_code == 200
            # Email был отправлен
            mock_email.assert_called_once()

    def test_forgot_password_nonexistent_email(self, client):
        """
        Запрос сброса для несуществующего email.
        Тоже 200 — безопасность.
        """
        with patch("app.api.v1.auth.send_reset_password_email") as mock_email:
            response = client.post("/api/v1/auth/forgot-password", json={
                "email": "nobody@nowhere.com"
            })
            assert response.status_code == 200
            # Email НЕ отправлялся
            mock_email.assert_not_called()

    def test_forgot_password_invalid_email(self, client):
        """Невалидный email — 422."""
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": "notanemail"
        })
        assert response.status_code == 422


class TestResetPassword:

    def test_reset_password_success(self, client, registered_user):
        """Успешный сброс пароля через токен."""
        user_email = registered_user["user"]["email"]  # email реального пользователя из fixture

        # Мокаем отправку письма, чтобы не отправлялся настоящий email
        with patch("app.api.v1.auth.send_reset_password_email"):
            client.post("/api/v1/auth/forgot-password", json={
                "email": user_email
            })

        # Достаём токен напрямую из Redis
        from app.services.redis_client import redis_client
        keys = redis_client.keys("reset_password:*")
        assert len(keys) == 1
        token = keys[0].split("reset_password:")[1]

        # Сбрасываем пароль
        response = client.post("/api/v1/auth/reset-password", json={
            "token": token,
            "new_password": "resetpassword789",
        })
        assert response.status_code == 200

        # Логин с новым паролем работает
        login = client.post("/api/v1/auth/login", json={
            "email": user_email,
            "password": "resetpassword789",
        })
        assert login.status_code == 200

    def test_reset_password_invalid_token(self, client):
        """Невалидный токен — 400."""
        response = client.post("/api/v1/auth/reset-password", json={
            "token":        "invalid-token-here",
            "new_password": "newpassword123",
        })
        assert response.status_code == 400

    def test_reset_token_one_time_use(self, client, registered_user):
        """Токен одноразовый — повторное использование — 400."""
        user_email = registered_user["user"]["email"]  # берем email реально зарегистрированного пользователя

        # Мокаем отправку письма
        with patch("app.api.v1.auth.send_reset_password_email"):
            client.post("/api/v1/auth/forgot-password", json={
                "email": user_email
            })

        # Получаем токен из Redis
        from app.services.redis_client import redis_client
        keys = redis_client.keys("reset_password:*")
        assert len(keys) == 1
        token = keys[0].split("reset_password:")[1]

        # Первый сброс — успех
        client.post("/api/v1/auth/reset-password", json={
            "token": token,
            "new_password": "firstreset123",
        })

        # Второй сброс тем же токеном — 400
        response = client.post("/api/v1/auth/reset-password", json={
            "token": token,
            "new_password": "secondreset456",
        })
        assert response.status_code == 400

    def test_reset_password_short(self, client):
        """Новый пароль меньше 8 символов — 422."""
        response = client.post("/api/v1/auth/reset-password", json={
            "token":        "sometoken",
            "new_password": "123",
        })
        assert response.status_code == 422