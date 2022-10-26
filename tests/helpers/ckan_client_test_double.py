from clients.ckan_client import init_ckan, NotFound  # noqa: F401

valid_username = 'fjelltopp_user'
valid_user_id = "fake_user_id"
valid_user_email = "fake@fjelltopp.org"
USER_DETAILS = {
    "email_hash": "0e774ad846b368575ab7ca8738d114d",
    "about": "Stubbed CKAN user",
    "apikey": "46b76277-a274-433f-9b61-7b8085a1ce6f",
    "display_name": "Tomasz Sabala",
    "name": "tomek",
    "created": "2019-09-18T08:34:32.156325",
    "image_display_url": "",
    "id": valid_user_id,
    "state": "active",
    "image_url": "",
    "fullname": "Fake CkanUser",
    "email": valid_user_email,
    "number_created_packages": 1
}


def authenticate_user(password, username):
    if username == valid_username:
        return USER_DETAILS
    return {}


def get_user_details_for_email_or_404(email):
    return USER_DETAILS


def get_username_from_email_or_404(email):
    return USER_DETAILS['name']


def fetch_country_estimates_datasets(ckan_cli):
    return [
        {
            "id": f"dataset_{i}",
            "title": f"Dataset {i}",
            "organization": {
                "id": f"org_{i}",
                "title": f"Organization {i}"
            }
        } for i in range(1, 6)
    ]


def fetch_user_organization_ids(ckan_cli, capacity="editor"):
    return ["org_1"]


def fetch_user_collabolator_ids(ckan_cli, ckan_user_id=None, capacity="editor"):
    return ["dataset_5"]


def fetch_dataset_details(ckan_cli, dataset_id):
    pass


def fetch_workflow_state(ckan_cli, dataset_id):
    return {
        "completedTasks": [
            {"id": "task2", "completedAt": '2021-12-10 15:22:12.640480'},
            {"id": "task3", "completedAt": '2021-12-10 15:23:12.640480'}
        ]
    }


def push_workflow_state(ckan_cli, dataset_id, workflow_state):
    pass


def dataset_show_url(ckan_cli, dataset_id):
    pass
