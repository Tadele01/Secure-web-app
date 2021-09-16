import os
from flask import Flask
from flask.helpers import url_for

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='YJyOmvBP4s',
        DATABASE = os.path.join(app.instance_path, 'citizens_feedbacks.sqlite'),
    )
    if test_config == None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth, feedback
    app.register_blueprint(auth.bp)
    app.register_blueprint(feedback.bp)

    app.add_url_rule('/', endpoint='index')

    return app