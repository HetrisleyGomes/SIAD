from flask import Flask
from app.config.config import SENHA
app = Flask(__name__)
app.config['SECRET_KEY'] = SENHA

from app import routes, api
app.run(debug=True)
