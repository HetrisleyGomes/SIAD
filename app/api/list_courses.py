import json
from decouple import config
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


# Escopo de acesso para as APIs do Google que você deseja utilizar
SCOPES = ["https://www.googleapis.com/auth/classroom.rosters.readonly","https://www.googleapis.com/auth/classroom.courses.readonly","https://www.googleapis.com/auth/classroom.student-submissions.students.readonly"]

# Caminho do arquivo de credenciais
credentials_path = config('CREDENTIAL')

# Caminho do arquivo de token
token_path = config('TOKEN')

def listar_cursos():
    """Lista os cursos cadastrados no Google Classroom."""
    # Carrega as informações do token do arquivo
    with open(token_path, 'r') as token_file:
        token_json = json.load(token_file)

    # Cria um objeto Credentials a partir do conteúdo do arquivo
    credentials = Credentials.from_authorized_user_info(token_json, SCOPES)


    # Cria um serviço para a API do Google Classroom
    service = build('classroom', 'v1', credentials=credentials)

    # Faz a solicitação para listar os cursos
    courses = service.courses().list().execute()
    return courses
    
def get_curso(curso_id):
    """Lista os cursos cadastrados no Google Classroom."""
    with open(token_path, 'r') as token_file:
        token_json = json.load(token_file)
    credentials = Credentials.from_authorized_user_info(token_json, SCOPES)
    service = build('classroom', 'v1', credentials=credentials)
    course = service.courses().get(id=curso_id).execute()
    
    return course

def get_estudantes(curso_id):
    """Obtém as notas das atividades de todos os alunos de um curso."""
    # Carrega as informações do token do arquivo
    with open(token_path, 'r') as token_file:
        token_json = json.load(token_file)

    credentials = Credentials.from_authorized_user_info(token_json, SCOPES)
    service = build('classroom', 'v1', credentials=credentials)
    # Faz a solicitação para obter a lista de todas as atividades do curso
    course_works = service.courses().courseWork().list(courseId=curso_id).execute()

    # Lista para armazenar as notas de todas as atividades
    all_student_submissions = []
    activity_names = []

    if 'courseWork' in course_works:
        for course_work in course_works['courseWork']:
            # Faz a solicitação para obter as notas das atividades de todos os alunos para a atividade atual
            student_submissions = service.courses().courseWork().studentSubmissions().list(
                courseId=curso_id,
                courseWorkId=course_work['id']
            ).execute()
        
            # Nome da atividade
            activity_name = course_work['title']  
            # Adiciona o nome da atividade à lista
            activity_names.append(activity_name)

            # Adiciona as notas da atividade atual à lista geral
            all_student_submissions.append(student_submissions)

    return all_student_submissions, activity_names

def get_student_name(actor_user_id):
    """Obtém o nome do aluno usando o actorUserId."""
    # Carrega as informações do token do arquivo
    with open(token_path, 'r') as token_file:
        token_json = json.load(token_file)

    credentials = Credentials.from_authorized_user_info(token_json, SCOPES)
    service = build('classroom', 'v1', credentials=credentials)
    # Faz a solicitação para obter as informações do perfil do aluno
    student_profile = service.userProfiles().get(userId=actor_user_id).execute()

    return student_profile.get('name', 'Nome do Aluno')  # Substitua 'Nome do Aluno' pelo nome padrão desejado

def get_course_name(curso_id):
    # Carrega as informações do token do arquivo
    with open(token_path, 'r') as token_file:
        token_json = json.load(token_file)

    credentials = Credentials.from_authorized_user_info(token_json, SCOPES)
    service = build('classroom', 'v1', credentials=credentials)
    course = service.courses().get(id=curso_id).execute()

    # O nome da turma está em 'course['name']'
    turma_nome = course['name']

    return turma_nome