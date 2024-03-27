from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def get_user(user_id):
    return Professor.query.filter_by(professorId=user_id).first()

class Professor(UserMixin, db.Model):
    __tablename__ = 'tbProfessor' 

    professorId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(50), nullable=False)
    matricula = db.Column(db.String(100), nullable=False)

    def __init__(self,nome, email, senha, matricula):
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)
        self.matricula = matricula
    
    def veriffy_password(self, senha):
        #return check_password_hash(self.senha, senha)
        return True
    
    @staticmethod
    def get(professor_id):
        return Professor.query.get(int(professor_id))
    
    def getNome(self):
        #professor = Professor.query.get(int(professor_id))
        return self.nome
    
    def get_id(self):
        return str(self.professorId)

class Turma(db.Model):
    __tablename__ = 'tbTurmas'

    turmaID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    turmaInfo = db.Column(db.String(50), nullable=False)
    alunos = db.Column(db.Text, nullable=False)

    def __init__(self, turmaInfo, alunos):
        self.turmaInfo = turmaInfo
        self.alunos = alunos

class ProfessorTurmas(db.Model):
    __tablename__ = 'tbProfessorTurmas'

    professorTurmasid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    professorID = db.Column(db.Integer, nullable=False)
    turmaID = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(255))

    __table_args__ = (
        db.ForeignKeyConstraint(['professorID'], ['tbProfessor.professorId']),
        db.ForeignKeyConstraint(['turmaID'], ['tbTurmas.turmaID'])
    )

    def __init__(self, professorID, turmaID, link=None):
        self.professorID = professorID
        self.turmaID = turmaID
        self.link = link