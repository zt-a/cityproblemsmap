# tests/test_two_factor.py
import pytest
from unittest.mock import patch


def test_2fa_status_disabled(client, auth_headers):
    """Проверка статуса 2FA когда отключена"""
    response = client.get("/api/v1/2fa/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is False
    assert data["backup_codes_count"] == 0


def test_2fa_setup(client, auth_headers):
    """Настройка 2FA"""
    response = client.post("/api/v1/2fa/setup", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "secret" in data
    assert "qr_uri" in data
    assert "backup_codes" in data
    assert len(data["backup_codes"]) == 10
    assert "otpauth://" in data["qr_uri"]


def test_2fa_setup_already_enabled(client, auth_headers):
    """Попытка настройки когда 2FA уже включена"""
    # Сначала настраиваем и включаем
    setup_resp = client.post("/api/v1/2fa/setup", headers=auth_headers)
    assert setup_resp.status_code == 200

    # Включаем с мокированием кода
    with patch("app.api.v1.two_factor.verify_totp_code", return_value=True):
        enable_resp = client.post(
            "/api/v1/2fa/enable",
            json={"code": "123456"},
            headers=auth_headers
        )
        assert enable_resp.status_code == 200

    # Пытаемся настроить снова
    response = client.post("/api/v1/2fa/setup", headers=auth_headers)
    assert response.status_code == 400
    assert "уже включена" in response.json()["detail"]


@patch("app.api.v1.two_factor.verify_totp_code")
def test_2fa_enable_success(mock_verify, client, auth_headers):
    """Успешное включение 2FA"""
    # Настраиваем
    setup_resp = client.post("/api/v1/2fa/setup", headers=auth_headers)
    assert setup_resp.status_code == 200

    # Включаем с правильным кодом
    mock_verify.return_value = True
    response = client.post(
        "/api/v1/2fa/enable",
        json={"code": "123456"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "успешно включена" in response.json()["message"]

    # Проверяем статус
    status_resp = client.get("/api/v1/2fa/status", headers=auth_headers)
    assert status_resp.json()["enabled"] is True


@patch("app.api.v1.two_factor.verify_totp_code")
def test_2fa_enable_wrong_code(mock_verify, client, auth_headers):
    """Включение 2FA с неверным кодом"""
    # Настраиваем
    client.post("/api/v1/2fa/setup", headers=auth_headers)

    # Пытаемся включить с неверным кодом
    mock_verify.return_value = False
    response = client.post(
        "/api/v1/2fa/enable",
        json={"code": "000000"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Неверный код" in response.json()["detail"]


def test_2fa_enable_without_setup(client, auth_headers):
    """Попытка включения без предварительной настройки"""
    response = client.post(
        "/api/v1/2fa/enable",
        json={"code": "123456"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "setup" in response.json()["detail"]


@patch("app.api.v1.two_factor.verify_totp_code")
def test_2fa_disable_success(mock_verify, client, auth_headers, registered_user):
    """Успешное отключение 2FA"""
    # Настраиваем и включаем
    client.post("/api/v1/2fa/setup", headers=auth_headers)
    mock_verify.return_value = True
    client.post("/api/v1/2fa/enable", json={"code": "123456"}, headers=auth_headers)

    # Отключаем
    response = client.post(
        "/api/v1/2fa/disable",
        json={
            "password": "password123",
            "code": "123456"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "отключена" in response.json()["message"]

    # Проверяем статус
    status_resp = client.get("/api/v1/2fa/status", headers=auth_headers)
    assert status_resp.json()["enabled"] is False


def test_2fa_disable_wrong_password(client, auth_headers):
    """Отключение 2FA с неверным паролем"""
    # Настраиваем и включаем
    client.post("/api/v1/2fa/setup", headers=auth_headers)
    with patch("app.api.v1.two_factor.verify_totp_code", return_value=True):
        client.post("/api/v1/2fa/enable", json={"code": "123456"}, headers=auth_headers)

    # Пытаемся отключить с неверным паролем
    response = client.post(
        "/api/v1/2fa/disable",
        json={
            "password": "wrongpassword",
            "code": "123456"
        },
        headers=auth_headers
    )
    assert response.status_code == 401
    assert "Неверный пароль" in response.json()["detail"]


def test_2fa_disable_not_enabled(client, auth_headers):
    """Попытка отключения когда 2FA не включена"""
    response = client.post(
        "/api/v1/2fa/disable",
        json={
            "password": "password123",
            "code": "123456"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "не включена" in response.json()["detail"]


@patch("app.api.v1.two_factor.verify_totp_code")
def test_2fa_verify_success(mock_verify, client, auth_headers):
    """Успешная проверка 2FA кода"""
    # Настраиваем и включаем
    client.post("/api/v1/2fa/setup", headers=auth_headers)
    mock_verify.return_value = True
    client.post("/api/v1/2fa/enable", json={"code": "123456"}, headers=auth_headers)

    # Проверяем код
    response = client.post(
        "/api/v1/2fa/verify",
        json={"code": "123456"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "верный" in response.json()["message"]


@patch("app.api.v1.two_factor.verify_totp_code")
@patch("app.api.v1.two_factor.verify_backup_code")
def test_2fa_verify_backup_code(mock_verify_backup, mock_verify, client, auth_headers):
    """Проверка резервного кода"""
    # Настраиваем и включаем
    setup_resp = client.post("/api/v1/2fa/setup", headers=auth_headers)
    backup_codes = setup_resp.json()["backup_codes"]

    mock_verify.return_value = True
    client.post("/api/v1/2fa/enable", json={"code": "123456"}, headers=auth_headers)

    # Проверяем резервный код
    mock_verify.return_value = False  # Обычный код не подходит
    mock_verify_backup.return_value = True  # Резервный код подходит

    response = client.post(
        "/api/v1/2fa/verify",
        json={"code": backup_codes[0]},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "Резервный код" in response.json()["message"]

    # Проверяем что количество резервных кодов уменьшилось
    status_resp = client.get("/api/v1/2fa/status", headers=auth_headers)
    assert status_resp.json()["backup_codes_count"] == 9


@patch("app.api.v1.two_factor.verify_totp_code")
def test_2fa_verify_wrong_code(mock_verify, client, auth_headers):
    """Проверка неверного кода"""
    # Настраиваем и включаем
    client.post("/api/v1/2fa/setup", headers=auth_headers)
    mock_verify.return_value = True
    client.post("/api/v1/2fa/enable", json={"code": "123456"}, headers=auth_headers)

    # Проверяем неверный код
    mock_verify.return_value = False
    response = client.post(
        "/api/v1/2fa/verify",
        json={"code": "000000"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Неверный код" in response.json()["detail"]


def test_2fa_verify_not_enabled(client, auth_headers):
    """Попытка проверки кода когда 2FA не включена"""
    response = client.post(
        "/api/v1/2fa/verify",
        json={"code": "123456"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "не включена" in response.json()["detail"]


def test_2fa_unauthorized(client):
    """Попытка доступа к 2FA без авторизации"""
    endpoints = [
        "/api/v1/2fa/status",
        "/api/v1/2fa/setup",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint) if "status" in endpoint else client.post(endpoint)
        assert response.status_code == 401
