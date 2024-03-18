from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config.config import SENHA
from sqlalchemy import text
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = SENHA

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://@localhost/siad_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
# Movendo o teste de conexão para dentro do contexto da aplicação
with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print("Conexão com o banco de dados bem-sucedida!")
    except Exception as e:
        print(f"Erro na conexão com o banco de dados: {e}")
        
from app import routes, api

app.run(debug=True)