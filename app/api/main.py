import os
import json
from decouple import config
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Escopo de acesso para as APIs do Google que você deseja utilizar
SCOPES = ["https://www.googleapis.com/auth/classroom.rosters.readonly","https://www.googleapis.com/auth/classroom.courses.readonly","https://www.googleapis.com/auth/classroom.student-submissions.students.readonly"]

# Caminho do arquivo de credenciais
credentials_path = config('CREDENTIAL')

# Caminho do arquivo de token
token_path = config('TOKEN')

def authenticate_google():
    """Autentica o usuário usando o Google OAuth2.0."""
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path, SCOPES)
    credentials = flow.run_local_server(port=7890)
    save_token(credentials)

def save_token(credentials):
    """Salva as informações do token em um arquivo 'token.json'."""
    token = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    with open(token_path, 'w') as token_file:
        json.dump(token, token_file)

def check_and_refresh_token():
    """Verifica e atualiza o token de credencial, se necessário."""
    try:
        creds = Credentials.from_authorized_user_file(token_path)
        print(creds.valid)
    except FileNotFoundError:
        creds = None

    if not creds or not creds.valid:
        print("Credenciais inválidas ou expiradas.")
        if creds and creds.expired and creds.refresh_token:
            print("Credenciais expiradas. Tentando atualizar...")
            try:
                creds.refresh(Request())
                print("Credenciais atualizadas com sucesso.")
                save_token(creds)
            except Exception as e:
                print(f"Erro ao atualizar credenciais: {e}")
                if str(e) == "('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant', 'error_description': 'Token has been expired or revoked.'})":
                    return bool(False)
                elif str(e) == "('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})":
                    authenticate_google()
        else:
            return bool(False)
    return creds


