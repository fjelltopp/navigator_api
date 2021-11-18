import pytest

class TestMain:
    def test_index(self, test_client):
        r = test_client.get('/')
        assert r.status_code == 200
        assert r.json

    @pytest.mark.parametrize("endpoint_path,http_methods",
                             [
                                 ('/user', ['GET']),
                                 ('/datasets', ['GET']),
                                 ('/workflows', ['GET']),
                                 ('/workflows/123/state', ['GET']),
                                 ('/workflows/123/tasks/123', ['GET']),
                                 ('/workflows/123/tasks/123/complete', ['POST', 'DELETE']),
                                 ('/workflows/123/tasks/123/skip', ['POST', 'DELETE']),
                             ])
    def test_endpoint_require_logging_in(self, test_client, endpoint_path, http_methods):
        for method in http_methods:
            if method == 'POST':
                r = test_client.post(endpoint_path)
            elif method == 'DELETE':
                r = test_client.delete(endpoint_path)
            elif method == 'GET':
                r = test_client.get(endpoint_path)
            else:
                pytest.fail(f"Unsupported http method {method}")
            assert r.status_code == 401

@pytest.mark.usefixtures('logged_in')
class TestUserDataAvaiable:
    def test_user_details(self, test_client):
        r = test_client.get('/user')
        assert r.status_code == 200
        user_details = r.json
        assert user_details['fullname'] == 'Fake CkanUser'
        assert user_details['email'] == 'fake@fjelltopp.org'

