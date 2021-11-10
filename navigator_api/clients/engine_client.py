def get_decision_engine(dataset_id, user_id):
    return {"id": "foobar"}


def get_decision(dataset_id):
    # get CKAN dataset dict for data_url
    # get nav Workflow obj for skipped steps
    # send engine POST request /api/decide
    pass


def get_action(action_id):
    # get engine Action by GET request to /api/action/action_id
    pass

def _engine_url():
    # get engine host url + /api/
    pass