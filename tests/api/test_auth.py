import pytest
from flask import session

from unittest.mock import patch
from tests.helpers import ckan_client_test_double


class TestLogin:
    @pytest.fixture
    def ckan_client_mock(self):
        with patch('api.auth.ckan_client', wraps=ckan_client_test_double) as ckan_client_mock:
            yield ckan_client_mock

    def test_login_with_valid_credentials(self, test_client, ckan_client_mock):
        r = test_client.post('login', json={"username": ckan_client_test_double.valid_username, "password": "pass"})

        assert ckan_client_mock.authenticate_user.called
        assert r.status_code == 200
        assert r.json["message"] == "Login successful"

    def test_login_with_invalid_credentials(self, test_client, ckan_client_mock):
        r = test_client.post('login', json={"username": "invalid_username", "password": "pass"})

        assert ckan_client_mock.authenticate_user.called
        assert r.status_code == 401
        assert r.json["message"] == "Bad credentials"

    def test_login_stores_ckan_user_in_session(self, test_client, ckan_client_mock):
        test_client.post('login', json={"username": ckan_client_test_double.valid_username, "password": "pass"})
        assert session.get('ckan_user')

    def test_logout_removes_ckan_user_from_session(self, test_client, ckan_client_mock):
        test_client.post('login', json={"username": ckan_client_test_double.valid_username, "password": "pass"})
        test_client.post('logout')
        assert not session.get('ckan_user')
