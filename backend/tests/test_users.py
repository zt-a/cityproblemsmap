USERS_URL = "/api/v1/users"


def assert_user_public_fields(data, expected_user=None):
    if expected_user:
        assert data["entity_id"] == expected_user["user"]["entity_id"]
        assert data["username"]  == expected_user["user"]["username"]
        assert data["city"]      == expected_user["user"]["city"]
    for field in ["role", "status", "reputation", "is_verified"]:
        assert field in data


class TestUsersMe:

    def test_get_me_success(self, client, auth_headers, registered_user):
        response = client.get(f'{USERS_URL}/me', headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert_user_public_fields(data, registered_user)

    def test_get_me_unauthorized(self, client):
        response = client.get(f'{USERS_URL}/me')
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid.token"}
        response = client.get(f'{USERS_URL}/me', headers=headers)
        assert response.status_code == 401


class TestGetUser:

    def test_get_user_success(self, client, registered_user):
        response = client.get(f'{USERS_URL}/{registered_user["user"]["entity_id"]}')
        assert response.status_code == 200
        data = response.json()
        assert_user_public_fields(data, registered_user)

    def test_get_user_not_found(self, client):
        nonexistent_id = 999_999
        response = client.get(f'{USERS_URL}/{nonexistent_id}')
        assert response.status_code == 404



class TestUpdateProfile:

    def test_update_username_success(self, client, auth_headers):
        """Успешная смена username."""
        response = client.patch(
            "/api/v1/users/me/profile",
            json    = {"username": "newusername"},
            headers = auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"
        assert response.json()["version"]  == 2

    def test_update_username_same(self, client, registered_user, auth_headers):
        """Тот же username — 400."""
        response = client.patch(
            "/api/v1/users/me/profile",
            json    = {"username": registered_user["user"]["username"]},
            headers = auth_headers,
        )
        assert response.status_code == 400

    def test_update_username_taken(self, client, auth_headers):
        """Занятый username — 409."""
        # Регистрируем второго пользователя
        client.post("/api/v1/auth/register", json={
            "username": "takenuser",
            "email":    "taken@test.com",
            "password": "password123",
        })
        response = client.patch(
            "/api/v1/users/me/profile",
            json    = {"username": "takenuser"},
            headers = auth_headers,
        )
        assert response.status_code == 409

    def test_update_username_short(self, client, auth_headers):
        """Слишком короткий username — 422."""
        response = client.patch(
            "/api/v1/users/me/profile",
            json    = {"username": "ab"},
            headers = auth_headers,
        )
        assert response.status_code == 422

    def test_update_username_unauthorized(self, client):
        """Без токена — 401."""
        response = client.patch(
            "/api/v1/users/me/profile",
            json = {"username": "newname"},
        )
        assert response.status_code == 401


class TestUpdateEmail:

    def test_update_email_success(self, client, auth_headers):
        """Успешная смена email."""
        response = client.patch(
            "/api/v1/users/me/email",
            json = {
                "new_email": "newemail@test.com",
                "password":  "password123",
            },
            headers = auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["email"]   == "newemail@test.com"
        assert response.json()["version"] == 2

    def test_update_email_wrong_password(self, client, auth_headers):
        """Неверный пароль — 400."""
        response = client.patch(
            "/api/v1/users/me/email",
            json = {
                "new_email": "newemail@test.com",
                "password":  "wrongpassword",
            },
            headers = auth_headers,
        )
        assert response.status_code == 400

    def test_update_email_same(self, client, registered_user, auth_headers):
        """Тот же email — 400."""
        response = client.patch(
            "/api/v1/users/me/email",
            json = {
                "new_email": registered_user["user"]["email"],
                "password":  "password123",
            },
            headers = auth_headers,
        )
        assert response.status_code == 400

    def test_update_email_taken(self, client, auth_headers):
        """Занятый email — 409."""
        client.post("/api/v1/auth/register", json={
            "username": "otheruser",
            "email":    "other@test.com",
            "password": "password123",
        })
        response = client.patch(
            "/api/v1/users/me/email",
            json = {
                "new_email": "other@test.com",
                "password":  "password123",
            },
            headers = auth_headers,
        )
        assert response.status_code == 409

    def test_update_email_unauthorized(self, client):
        """Без токена — 401."""
        response = client.patch(
            "/api/v1/users/me/email",
            json = {
                "new_email": "new@test.com",
                "password":  "password123",
            },
        )
        assert response.status_code == 401


class TestMyProblems:

    def test_my_problems_empty(self, client, auth_headers):
        """Нет проблем — пустой список."""
        response = client.get(
            "/api/v1/users/me/problems",
            headers = auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_my_problems_with_data(self, client, auth_headers):
        """После создания проблемы — она в списке."""
        client.post("/api/v1/problems/", json={
            "title":        "Моя проблема",
            "country":      "Kyrgyzstan",
            "city":         "Bishkek",
            "latitude":     42.8746,
            "longitude":    74.5698,
            "problem_type": "pothole",
            "nature":       "permanent",
        }, headers=auth_headers)

        response = client.get(
            "/api/v1/users/me/problems",
            headers = auth_headers,
        )
        assert response.json()["total"] == 1

    def test_my_problems_filter_by_status(self, client, auth_headers):
        """Фильтр по статусу."""
        client.post("/api/v1/problems/", json={
            "title":        "Проблема",
            "country":      "Kyrgyzstan",
            "city":         "Bishkek",
            "latitude":     42.8746,
            "longitude":    74.5698,
            "problem_type": "pothole",
            "nature":       "permanent",
        }, headers=auth_headers)

        response = client.get(
            "/api/v1/users/me/problems",
            params  = {"status": "open"},
            headers = auth_headers,
        )
        assert response.json()["total"] == 1

        response = client.get(
            "/api/v1/users/me/problems",
            params  = {"status": "solved"},
            headers = auth_headers,
        )
        assert response.json()["total"] == 0

    def test_my_problems_unauthorized(self, client):
        """Без токена — 401."""
        response = client.get("/api/v1/users/me/problems")
        assert response.status_code == 401


class TestMyVotes:

    def test_my_votes_empty(self, client, auth_headers):
        """Нет голосов — пустой список."""
        response = client.get(
            "/api/v1/users/me/votes",
            headers = auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_my_votes_after_voting(self, client, auth_headers):
        """После голосования — голос в списке."""
        # Создаём проблему вторым пользователем
        second = client.post("/api/v1/auth/register", json={
            "username": "problemowner",
            "email":    "owner@test.com",
            "password": "password123",
            "city":     "Bishkek",
        }).json()
        second_headers = {"Authorization": f"Bearer {second['access_token']}"}

        problem = client.post("/api/v1/problems/", json={
            "title":        "Чужая проблема",
            "country":      "Kyrgyzstan",
            "city":         "Bishkek",
            "latitude":     42.8746,
            "longitude":    74.5698,
            "problem_type": "pothole",
            "nature":       "permanent",
        }, headers=second_headers).json()

        # Голосуем
        client.post(
            f"/api/v1/problems/{problem['entity_id']}/votes",
            json    = {"urgency": 4, "is_true": True},
            headers = auth_headers,
        )

        response = client.get(
            "/api/v1/users/me/votes",
            headers = auth_headers,
        )
        assert len(response.json()) == 1

    def test_my_votes_unauthorized(self, client):
        """Без токена — 401."""
        response = client.get("/api/v1/users/me/votes")
        assert response.status_code == 401


class TestMyComments:

    def test_my_comments_empty(self, client, auth_headers):
        """Нет комментариев — пустой список."""
        response = client.get(
            "/api/v1/users/me/comments",
            headers = auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_my_comments_unauthorized(self, client):
        """Без токена — 401."""
        response = client.get("/api/v1/users/me/comments")
        assert response.status_code == 401


class TestMyReputation:

    def test_reputation_empty(self, client, auth_headers):
        """Нет изменений репутации — пустая история."""
        response = client.get(
            "/api/v1/users/me/reputation",
            headers = auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_reputation"] == 0.0
        assert data["logs"]               == []

    def test_reputation_unauthorized(self, client):
        """Без токена — 401."""
        response = client.get("/api/v1/users/me/reputation")
        assert response.status_code == 401


class TestUserProblems:

    def test_user_problems_public(self, client, auth_headers, registered_user):
        """Публичные проблемы пользователя — без авторизации."""
        entity_id = registered_user["user"]["entity_id"]
        response  = client.get(f"/api/v1/users/{entity_id}/problems")
        assert response.status_code == 200

    def test_user_problems_not_found(self, client):
        """Несуществующий пользователь — 404."""
        response = client.get("/api/v1/users/99999/problems")
        assert response.status_code == 404