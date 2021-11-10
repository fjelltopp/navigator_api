"""Entry point module for WSGI

This is used when running the app using a WSGI server such as uWSGI
"""
from gevent import monkey
from navigator_api.app import create_app

print("Monkey patching the standard library...")
monkey.patch_all()

print("Creating app...")
app = create_app()
