from clients.ckan_client import NotFound

valid_username = 'fjelltopp_user'


def authenticate_user(password, username):
    if username == valid_username:
        return {
            "email_hash": "0e774ad846b368575ab7ca8738d114d",
            "about": "Stubbed CKAN user",
            "apikey": "46b76277-a274-433f-9b61-7b8085a1ce6f",
            "display_name": "Tomasz Sabala",
            "name": "tomek",
            "created": "2019-09-18T08:34:32.156325",
            "image_display_url": "",
            "id": "a3418c4d-62a0-5d26-89ba-01ba0f6057f0",
            "state": "active",
            "image_url": "",
            "fullname": "Fake CkanUser",
            "email": "fake@fjelltopp.org",
            "number_created_packages": 1
        }
    return {}


def fetch_country_estimates_datasets(ckan_cli):
    pass


def fetch_user_organization_ids(ckan_cli, capacity="editor"):
    pass


def fetch_user_collabolator_ids(ckan_cli, ckan_user_id=None, capacity="editor"):
    pass


def fetch_dataset_details(ckan_cli, dataset_id):
    pass


def fetch_workflow_state(ckan_cli, dataset_id):
    pass


def push_workflow_state(ckan_cli, dataset_id, workflow_state):
    pass


def dataset_show_url(ckan_cli, dataset_id):
    pass

