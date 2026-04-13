# tests/test_media.py
import io
import pytest
from PIL import Image
from unittest.mock import patch

PROBLEMS_URL = "/api/v1/problems"
REGISTER_URL = "/api/v1/auth/register"

VALID_PROBLEM = {
    "title":        "Яма на дороге",
    "country":      "Kyrgyzstan",
    "city":         "Bishkek",
    "latitude":     42.8746,
    "longitude":    74.5698,
    "problem_type": "pothole",
    "nature":       "permanent",
}


# ── Хелперы для создания тестовых файлов ─────────────────

def make_jpeg_bytes(width: int = 100, height: int = 100) -> bytes:
    """Создаёт валидный JPEG файл в памяти без EXIF."""
    buf   = io.BytesIO()
    image = Image.new("RGB", (width, height), color=(255, 0, 0))
    image.save(buf, format="JPEG")
    return buf.getvalue()


def make_png_bytes() -> bytes:
    """Создаёт валидный PNG файл."""
    buf   = io.BytesIO()
    image = Image.new("RGB", (50, 50), color=(0, 255, 0))
    image.save(buf, format="PNG")
    return buf.getvalue()


def make_oversized_bytes(size_mb: int) -> bytes:
    """Создаёт файл больше лимита."""
    return b"x" * (size_mb * 1024 * 1024 + 1)


def media_url(problem_entity_id: int) -> str:
    return f"{PROBLEMS_URL}/{problem_entity_id}/media"


def media_item_url(problem_entity_id: int, media_entity_id: int) -> str:
    return f"{PROBLEMS_URL}/{problem_entity_id}/media/{media_entity_id}"


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
        "username": "uploader",
        "email":    "uploader@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_headers(second_user):
    return {"Authorization": f"Bearer {second_user['access_token']}"}


@pytest.fixture(autouse=True)
def mock_local_storage(tmp_path, monkeypatch):
    """
    Перенаправляем локальное хранилище во временную папку.
    tmp_path — pytest создаёт и удаляет автоматически.
    Каждый тест получает чистую папку.
    """
    monkeypatch.setattr("app.config.settings.MEDIA_LOCAL_DIR", str(tmp_path))
    monkeypatch.setattr(
        "app.config.settings.MEDIA_BASE_URL",
        "http://localhost:8000/media",
    )
    monkeypatch.setattr("app.config.settings.MEDIA_STORAGE", "local")


class TestUploadMedia:

    def test_upload_jpeg_success(self, client, created_problem, auth_headers):
        """Успешная загрузка JPEG фото."""
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        )
        assert response.status_code == 201
        data = response.json()

        assert data["media_type"]        == "photo"
        assert data["status"]            == "active"
        assert data["version"]           == 1
        assert data["is_current"]
        assert data["problem_entity_id"] == pid
        assert data["url"]               is not None
        assert data["file_size"]         > 0

    def test_upload_png_success(self, client, created_problem, auth_headers):
        """Успешная загрузка PNG фото."""
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files   = {"file": ("photo.png", make_png_bytes(), "image/png")},
            headers = auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["media_type"] == "photo"

    def test_upload_creates_thumbnail(
        self, client, created_problem, auth_headers
    ):
        """После загрузки фото создаётся thumbnail."""
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        )
        assert response.status_code == 201
        # Thumbnail создаётся для фото
        assert response.json()["thumbnail_url"] is not None

    def test_upload_unauthorized(self, client, created_problem):
        """Без токена — 401."""
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 401

    def test_upload_nonexistent_problem(self, client, auth_headers):
        """Загрузка к несуществующей проблеме — 404."""
        response = client.post(
            media_url(99999),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        )
        assert response.status_code == 404

    def test_upload_invalid_type(self, client, created_problem, auth_headers):
        """Неподдерживаемый тип файла — 415."""
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files   = {"file": ("doc.pdf", b"fake pdf content", "application/pdf")},
            headers = auth_headers,
        )
        assert response.status_code == 415

    def test_upload_oversized_image(
        self, client, created_problem, auth_headers, monkeypatch
    ):
        """
        Фото превышает MAX_IMAGE_SIZE_MB — 413.
        Устанавливаем лимит 1MB для теста.
        """
        monkeypatch.setattr("app.config.settings.MAX_IMAGE_SIZE_MB", 1)
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files   = {"file": ("big.jpg", make_oversized_bytes(2), "image/jpeg")},
            headers = auth_headers,
        )
        assert response.status_code == 413

    def test_upload_multiple_files(
        self, client, created_problem, auth_headers, second_headers
    ):
        """
        Можно загрузить несколько файлов к одной проблеме.
        Разные пользователи могут загружать.
        """
        pid = created_problem["entity_id"]

        # Первый файл — автор
        r1 = client.post(
            media_url(pid),
            files   = {"file": ("photo1.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        )
        assert r1.status_code == 201

        # Второй файл — другой пользователь
        r2 = client.post(
            media_url(pid),
            files   = {"file": ("photo2.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = second_headers,
        )
        assert r2.status_code == 201

        # Оба файла в списке
        media_list = client.get(media_url(pid)).json()
        assert len(media_list) == 2


class TestGetMedia:

    def test_get_empty(self, client, created_problem):
        """Пустой список если нет медиа."""
        pid      = created_problem["entity_id"]
        response = client.get(media_url(pid))

        assert response.status_code == 200
        assert response.json()      == []

    def test_get_after_upload(self, client, created_problem, auth_headers):
        """После загрузки — один элемент в списке."""
        pid = created_problem["entity_id"]

        client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        )

        response = client.get(media_url(pid))
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_unauthorized_allowed(self, client, created_problem):
        """Просмотр медиа доступен без авторизации."""
        pid      = created_problem["entity_id"]
        response = client.get(media_url(pid))
        assert response.status_code == 200

    def test_get_nonexistent_problem(self, client):
        """Медиа несуществующей проблемы — 404."""
        response = client.get(media_url(99999))
        assert response.status_code == 404

    def test_removed_media_not_shown(
        self, client, created_problem, auth_headers
    ):
        """
        Удалённые медиафайлы не показываются в списке.
        status=removed — скрыт публично.
        """
        pid = created_problem["entity_id"]

        # Загружаем
        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        ).json()

        # Удаляем
        client.delete(
            media_item_url(pid, upload["entity_id"]),
            headers=auth_headers,
        )

        # В списке пусто
        media_list = client.get(media_url(pid)).json()
        assert len(media_list) == 0


class TestDeleteMedia:

    def test_uploader_can_delete(
        self, client, created_problem, second_headers
    ):
        """Загрузивший пользователь может удалить свой файл."""
        pid = created_problem["entity_id"]

        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = second_headers,
        ).json()

        response = client.delete(
            media_item_url(pid, upload["entity_id"]),
            headers=second_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "removed"

    def test_problem_author_can_delete(
        self, client, created_problem, auth_headers, second_headers
    ):
        """Автор проблемы может удалить любой медиафайл к своей проблеме."""
        pid = created_problem["entity_id"]

        # Загружает второй пользователь
        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = second_headers,
        ).json()

        # Удаляет автор проблемы
        response = client.delete(
            media_item_url(pid, upload["entity_id"]),
            headers=auth_headers,   # автор проблемы
        )
        assert response.status_code == 200

    def test_admin_can_delete(
        self, client, created_problem, second_headers, admin_headers
    ):
        """Админ может удалить любой медиафайл."""
        pid = created_problem["entity_id"]

        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = second_headers,
        ).json()

        response = client.delete(
            media_item_url(pid, upload["entity_id"]),
            headers=admin_headers,
        )
        assert response.status_code == 200

    def test_stranger_cannot_delete(
        self, client, created_problem, auth_headers, second_headers
    ):
        """
        Чужой пользователь не может удалить медиафайл — 403.
        (не загрузивший, не автор проблемы, не модератор)
        """
        pid = created_problem["entity_id"]

        # Загружает автор проблемы
        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        ).json()

        # Пытается удалить второй пользователь — 403
        response = client.delete(
            media_item_url(pid, upload["entity_id"]),
            headers=second_headers,
        )
        assert response.status_code == 403

    def test_delete_unauthorized(self, client, created_problem, auth_headers):
        """Без токена — 401."""
        pid = created_problem["entity_id"]

        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        ).json()

        response = client.delete(
            media_item_url(pid, upload["entity_id"])
        )
        assert response.status_code == 401

    def test_delete_nonexistent(self, client, created_problem, auth_headers):
        """Несуществующий медиафайл — 404."""
        pid      = created_problem["entity_id"]
        response = client.delete(
            media_item_url(pid, 99999),
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_delete_creates_new_version(
        self, client, created_problem, auth_headers
    ):
        """
        Удаление = новая версия со status=removed.
        Данные не теряются — версионирование.
        """
        pid = created_problem["entity_id"]

        upload = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        ).json()

        deleted = client.delete(
            media_item_url(pid, upload["entity_id"]),
            headers=auth_headers,
        ).json()

        assert deleted["version"]      == 2       # новая версия
        assert deleted["status"]       == "removed"
        assert deleted["entity_id"]    == upload["entity_id"]  # тот же entity_id
        assert deleted["is_current"]


class TestExifValidation:

    def test_photo_without_exif_accepted(
        self, client, created_problem, auth_headers
    ):
        """
        Фото без EXIF принимается.
        Геопроверка пропускается если нет GPS данных.
        """
        pid      = created_problem["entity_id"]
        response = client.post(
            media_url(pid),
            files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers = auth_headers,
        )
        # Фото без EXIF — принимается
        assert response.status_code == 201
        data = response.json()
        assert data["exif_lat"] is None
        assert data["exif_lon"] is None

    def test_photo_with_wrong_location_rejected(
        self, client, created_problem, auth_headers
    ):
        """
        Фото с GPS далеко от проблемы — 422.
        Мокаем extract_exif чтобы вернуть координаты Москвы.
        Проблема в Бишкеке — расстояние > 1км.
        """
        pid = created_problem["entity_id"]

        # Мокаем EXIF — координаты Москвы (далеко от Бишкека)
        with patch("app.api.v1.media.extract_exif") as mock_exif:
            mock_exif.return_value = {
                "exif_lat":      55.7558,   # Москва
                "exif_lon":      37.6173,
                "exif_taken_at": None,
            }
            response = client.post(
                media_url(pid),
                files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
                headers = auth_headers,
            )

        assert response.status_code == 422
        assert "далеко" in response.json()["detail"]

    def test_photo_with_correct_location_accepted(
        self, client, created_problem, auth_headers
    ):
        """
        Фото с GPS рядом с проблемой — принимается.
        Мокаем EXIF с координатами рядом с проблемой (Бишкек).
        """
        pid = created_problem["entity_id"]

        with patch("app.api.v1.media.extract_exif") as mock_exif:
            mock_exif.return_value = {
                "exif_lat":      42.8748,   # ~20м от проблемы
                "exif_lon":      74.5700,
                "exif_taken_at": None,
            }
            response = client.post(
                media_url(pid),
                files   = {"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
                headers = auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["exif_lat"] == 42.8748
        assert data["exif_lon"] == 74.5700