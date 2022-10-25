from unittest.mock import patch
import pytest

from tests import factories
from tests.helpers import ckan_client_test_double


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
    def test_endpoints_require_authorization(self, test_client, endpoint_path, http_methods):
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
            assert r.json["error"] == "missing_authorization"
            assert r.json["error_description"] == 'Missing \"Authorization\" in headers.'


@pytest.mark.usefixtures('auth0_authorized')
class TestUserDataAvailable:

    @patch('api.routes.ckan_client', wraps=ckan_client_test_double)
    def test_user_details(self, ckan_client_mock, test_client):
        r = test_client.get('/user')
        assert r.status_code == 200
        user_details = r.json
        assert user_details['fullname'] == 'Fake CkanUser'
        assert user_details['email'] == 'fake@fjelltopp.org'

    @patch('api.routes.ckan_client', wraps=ckan_client_test_double)
    def test_datasets_return_all_items(self, ckan_client_mock, test_client):
        r = test_client.get('/datasets')
        assert r.status_code == 200
        datasets = r.json['datasets']
        assert len(datasets) == 2
        actual_dataset_ids = set(dataset['id'] for dataset in datasets)
        assert "dataset_1" in actual_dataset_ids
        assert "dataset_5" in actual_dataset_ids

    @patch('api.routes.ckan_client', wraps=ckan_client_test_double)
    def test_datasets_return_all_item_details(self, ckan_client_mock, test_client):
        r = test_client.get('/datasets')
        dataset = r.json['datasets'][0]
        assert dataset['id']
        assert dataset['name']
        assert dataset['organizationName']

    @patch('api.workflow.routes.ckan_client', wraps=ckan_client_test_double)
    def test_workflow_list_returns_all_item_details(self, ckan_client_mock, test_client):
        factories.WorklowFactory.create_batch(10, user_id=ckan_client_test_double.valid_user_id)
        r = test_client.get('/workflows')
        assert r.status_code == 200
        workflows = r.json['workflows']
        assert len(workflows) == 10
        for workflow in workflows:
            assert workflow['id']
            assert workflow['name']
