import os
from flask import Flask

def create_app():

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='Mickey',
        DATABASE_HOST= os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD= os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER= os.environ.get('FLASK_DATABASE_USER'),
        DATABASE= os.environ.get('FLASK_DATABASE')
    )
    
    from toDo.db import init_app
    init_app(app) #Se llama la función y pasa como parametro la app creada

    from . import auth
    
    from . import todo

    app.register_blueprint(auth.bluePrint)
    app.register_blueprint(todo.bluePrint)



    return app



