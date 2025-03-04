from flask import Blueprint
from controllers.auth_controller import  signin, signout, auth

auth_views = Blueprint('auth_views', __name__)


@auth_views.route('/signin', methods=['GET'])
def signin_route():
    return signin()

@auth_views.route('/signout', methods=['GET'])
def signout_route():
    return signout()


@auth_views.route('/auth', methods=['POST'])
def auth_route():
    return auth()

