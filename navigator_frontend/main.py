import time
from flask import Blueprint, Response

from . import pubsub

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    pubsub.publish('navigate', "{'fileurl': '/'}")
    return 'Index'

@main_blueprint.route('/profile')
def profile():
    r = Response(pubsub.response('result'), mimetype="text/event-stream")
    # Sleep to make sure we subscribe for response before sending event
    # to the engine
    time.sleep(5)
    pubsub.publish('navigate', "{'fileurl': 'profile'}")
    return r
