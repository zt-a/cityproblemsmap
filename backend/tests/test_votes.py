# tests/test_votes.py
import pytest

PROBLEMS_URL = "/api/v1/problems"
REGISTER_URL = "/api/v1/auth/register"

VALID_PROBLEM = {
    "title":        "Яма на дороге",
    "description":  "Большая яма",
    "country":      "Kyrgyzstan",
    "city":         "Bishkek",
    "latitude":     42.8746,
    "longitude":    74.5698,
    "problem_type": "pothole",
    "nature":       "permanent",
}


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def created_problem(client, auth_headers):
    response = client.post(
        PROBLEMS_URL + "/",
        json=VALID_PROBLEM,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_user(client):
    response = client.post(REGISTER_URL, json={
        "username": "voter",
        "email":    "voter@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_headers(second_user):
    return {"Authorization": f"Bearer {second_user['access_token']}"}


@pytest.fixture
def third_user(client):
    response = client.post(REGISTER_URL, json={
        "username": "voter2",
        "email":    "voter2@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def third_headers(third_user):
    return {"Authorization": f"Bearer {third_user['access_token']}"}


def vote_url(problem_entity_id: int) -> str:
    return f"{PROBLEMS_URL}/{problem_entity_id}/votes"


class TestCastVote:

    def test_vote_success(self, client, created_problem, second_headers):
        """Успешное голосование по всем четырём осям."""
        pid      = created_problem["entity_id"]
        response = client.post(
            vote_url(pid),
            json={
                "is_true":      True,
                "urgency":      4,
                "impact":       3,
                "inconvenience": 5,
            },
            headers=second_headers,
        )
        assert response.status_code == 201
        data = response.json()

        assert data["is_true"]
        assert data["urgency"]      == 4
        assert data["impact"]       == 3
        assert data["inconvenience"] == 5
        assert data["version"]      == 1
        assert data["is_current"]
        assert data["weight"]       >= 1.0   # минимальный вес

    def test_vote_partial(self, client, created_problem, second_headers):
        """
        Можно голосовать только по одной оси.
        Остальные поля остаются None.
        """
        pid      = created_problem["entity_id"]
        response = client.post(
            vote_url(pid),
            json={"is_true": False},  # только правдивость
            headers=second_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert not data["is_true"]
        assert data["urgency"]  is None
        assert data["impact"]   is None

    def test_vote_empty_fails(self, client, created_problem, second_headers):
        """Пустой голос (все поля None) — 400."""
        pid      = created_problem["entity_id"]
        response = client.post(
            vote_url(pid),
            json={},
            headers=second_headers,
        )
        assert response.status_code == 400

    def test_author_cannot_vote(self, client, created_problem, auth_headers):
        """Автор не может голосовать за свою проблему — 403."""
        pid      = created_problem["entity_id"]
        response = client.post(
            vote_url(pid),
            json={"urgency": 5},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_vote_unauthorized(self, client, created_problem):
        """Без токена — 401."""
        pid      = created_problem["entity_id"]
        response = client.post(
            vote_url(pid),
            json={"urgency": 3},
        )
        assert response.status_code == 401

    def test_vote_nonexistent_problem(self, client, second_headers):
        """Голос за несуществующую проблему — 404."""
        response = client.post(
            vote_url(99999),
            json={"urgency": 3},
            headers=second_headers,
        )
        assert response.status_code == 404

    def test_vote_invalid_scale(self, client, created_problem, second_headers):
        """Оценка вне диапазона 1–5 — 422."""
        pid      = created_problem["entity_id"]
        response = client.post(
            vote_url(pid),
            json={"urgency": 10},  # максимум 5
            headers=second_headers,
        )
        assert response.status_code == 422


class TestChangeVote:

    def test_change_vote_creates_new_version(
        self, client, created_problem, second_headers
    ):
        """
        Изменение голоса создаёт новую версию.
        Старая версия помечается is_current=False.
        version увеличивается.
        """
        pid = created_problem["entity_id"]

        # Первый голос
        first = client.post(
            vote_url(pid),
            json={"urgency": 2},
            headers=second_headers,
        ).json()
        assert first["version"] == 1

        # Меняем голос
        second = client.post(
            vote_url(pid),
            json={"urgency": 5},
            headers=second_headers,
        ).json()
        assert second["version"]    == 2
        assert second["urgency"]    == 5
        assert second["is_current"]

    def test_change_vote_merges_fields(
        self, client, created_problem, second_headers
    ):
        """
        При изменении голоса незаполненные поля берутся из предыдущей версии.
        Пользователь проголосовал urgency=3, потом меняет только impact=4.
        urgency должен остаться 3.
        """
        pid = created_problem["entity_id"]

        # Первый голос — только urgency
        client.post(
            vote_url(pid),
            json={"urgency": 3},
            headers=second_headers,
        )

        # Меняем — только impact
        updated = client.post(
            vote_url(pid),
            json={"impact": 4},
            headers=second_headers,
        ).json()

        # urgency должен сохраниться из первой версии
        assert updated["urgency"] == 3
        assert updated["impact"]  == 4


class TestVoteScores:

    def test_scores_updated_after_vote(
        self, client, created_problem, second_headers
    ):
        """
        После голосования scores проблемы обновляются.
        До голоса все scores = 0.0.
        После голоса urgency_score > 0.
        """
        pid = created_problem["entity_id"]

        # До голоса
        before = client.get(f"{PROBLEMS_URL}/{pid}").json()
        assert before["urgency_score"] == 0.0

        # Голосуем
        client.post(
            vote_url(pid),
            json={"urgency": 5, "is_true": True},
            headers=second_headers,
        )

        # После голоса
        after = client.get(f"{PROBLEMS_URL}/{pid}").json()
        assert after["urgency_score"]  > 0.0
        assert after["truth_score"]    > 0.0
        assert after["vote_count"]     == 1

    def test_multiple_votes_affect_scores(
        self, client, created_problem,
        second_headers, third_headers
    ):
        """
        Несколько голосов правильно агрегируются.
        Два голоса is_true=True → truth_score = 1.0.
        """
        pid = created_problem["entity_id"]

        client.post(
            vote_url(pid),
            json={"is_true": True, "urgency": 4},
            headers=second_headers,
        )
        client.post(
            vote_url(pid),
            json={"is_true": True, "urgency": 2},
            headers=third_headers,
        )

        problem = client.get(f"{PROBLEMS_URL}/{pid}").json()
        assert problem["truth_score"]  == 1.0   # оба True
        assert problem["vote_count"]   == 2
        assert problem["urgency_score"] > 0.0

    def test_fake_votes_lower_truth_score(
        self, client, created_problem,
        second_headers, third_headers
    ):
        """
        Голос is_true=False снижает truth_score.
        Один True + один False → truth_score = 0.5.
        """
        pid = created_problem["entity_id"]

        client.post(
            vote_url(pid),
            json={"is_true": True},
            headers=second_headers,
        )
        client.post(
            vote_url(pid),
            json={"is_true": False},
            headers=third_headers,
        )

        problem = client.get(f"{PROBLEMS_URL}/{pid}").json()
        assert problem["truth_score"] == 0.5


class TestGetMyVote:

    def test_get_my_vote_success(
        self, client, created_problem, second_headers
    ):
        """Получить свой текущий голос."""
        pid = created_problem["entity_id"]

        client.post(
            vote_url(pid),
            json={"urgency": 3, "is_true": True},
            headers=second_headers,
        )

        response = client.get(
            f"{vote_url(pid)}/my",
            headers=second_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["urgency"]  == 3
        assert data["is_true"]

    def test_get_my_vote_not_voted(
        self, client, created_problem, second_headers
    ):
        """Если ещё не голосовал — 404."""
        pid      = created_problem["entity_id"]
        response = client.get(
            f"{vote_url(pid)}/my",
            headers=second_headers,
        )
        assert response.status_code == 404

    def test_get_my_vote_unauthorized(self, client, created_problem):
        """Без токена — 401."""
        pid      = created_problem["entity_id"]
        response = client.get(f"{vote_url(pid)}/my")
        assert response.status_code == 401


class TestVoteStats:

    def test_stats_empty(self, client, created_problem):
        """Статистика без голосов — все нули."""
        pid      = created_problem["entity_id"]
        response = client.get(f"{vote_url(pid)}/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_votes"]   == 0
        assert data["true_count"]    == 0
        assert data["fake_count"]    == 0
        assert data["truth_score"]   == 0.0
        assert data["urgency_score"] == 0.0

    def test_stats_after_votes(
        self, client, created_problem,
        second_headers, third_headers
    ):
        """Статистика после двух голосов."""
        pid = created_problem["entity_id"]

        client.post(
            vote_url(pid),
            json={"is_true": True,  "urgency": 5},
            headers=second_headers,
        )
        client.post(
            vote_url(pid),
            json={"is_true": False, "urgency": 3},
            headers=third_headers,
        )

        response = client.get(f"{vote_url(pid)}/stats")
        data     = response.json()

        assert data["total_votes"] == 2
        assert data["true_count"]  == 1
        assert data["fake_count"]  == 1
        assert data["truth_score"] == 0.5


class TestVoteHistory:

    def test_history_shows_all_versions(
        self, client, created_problem, second_headers
    ):
        """
        История голосов показывает все версии включая изменённые.
        После изменения голоса в истории 2 записи.
        """
        pid = created_problem["entity_id"]

        # Первый голос
        client.post(
            vote_url(pid),
            json={"urgency": 2},
            headers=second_headers,
        )

        # Меняем
        client.post(
            vote_url(pid),
            json={"urgency": 5},
            headers=second_headers,
        )

        response = client.get(f"{vote_url(pid)}/history")
        assert response.status_code == 200
        history  = response.json()

        assert len(history)          == 2
        assert history[0]["version"] == 1
        assert history[0]["urgency"] == 2
        assert history[1]["version"] == 2
        assert history[1]["urgency"] == 5