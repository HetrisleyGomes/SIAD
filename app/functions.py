from flask import session
from decouple import config
import app.api.list_courses as api
import numpy as np
import json, io, os
import pandas as pd
from urllib.parse import urlparse


path = config('DATABASE')
temp = config('DATA')
def passFormFile(form):
    try:
        file_stream = io.BytesIO(form.read())
        dados = pd.read_csv(file_stream)
        cols_to_keep = ['Sobrenome', 'Nome', 'Endereço de e-mail']
        alunos_infos = dados.drop(columns=[c for c in dados.columns if c not in cols_to_keep])
        alunos_infos = alunos_infos.drop(index=[0, 1])
        alunos_notas = dados[[c for c in dados.columns if c not in cols_to_keep]]
        alunos_notas = alunos_notas.drop(index=[0, 1])
        # Gabarito de quanto valia cada atividade para posteriormente fazer uma média aritmética
        gab = dados.drop(columns=["Sobrenome", "Nome", "Endereço de e-mail"])
        gab = gab.iloc[1].values
        gab = gab.astype(float)
        # Converterndo as informações dos alunos em arrays. A variavel "ai" conta com as informações pessoais que são strings (como nome).
        # Enquanto "an" são as notas obtidas nas atividades convertidas para floats.
        ai = alunos_infos.values.tolist()
        an = alunos_notas.values.tolist()
        an = [[float(float(item)) for item in sublist] for sublist in an]
        return ai, an, gab
    except Exception as e:
        print(f'Erro ao processar o arquivo: {str(e)}')

def formSoma(aluno, nota):
    json_formatado = {}
    for index, i in enumerate(aluno):
        aluno_nome = f'{i[1]} {i[0]}'
        nota_final = format(round(np.sum(nota[index])))
        json_formatado[aluno_nome] = {"aluno": aluno_nome, "nota": nota_final}
    json_formatado = list(json_formatado.values())
    return json_formatado

def formPorcento(aluno, nota, gab):
    json_formatado = {}
    for index, i in enumerate(aluno):
        aluno_nome = f'{i[1]} {i[0]}'
        nota_final = format(round(np.sum(nota[index])*100/np.sum(gab)))
        json_formatado[aluno_nome] = {"aluno": aluno_nome, "nota": nota_final}
    json_formatado = list(json_formatado.values())
    return json_formatado

def executar_selenium(link):
    """Inicia o Selenium."""
    from .Selenium.main import set_url;
    try:
        set_url(link)
        return 'Script Selenium executado com sucesso.'
    except Exception as e:
        return f'Erro ao executar o script Selenium: {str(e)}'

def extract_points_earned(student_submissions, nomes):
    """Extrai os pontos ganhos de todos os estudantes."""
    students_earned = [] # Lista para armazenar os nome e notas dos alunos
    value_points = [] # Lista para armazenar a nota maxima de cada atividade
    activity_names = []  # Lista para armazenar os nomes das atividades

    for submission in student_submissions:
        activity_name = nomes[len(activity_names)]  # Nome da atividade
        activity_names.append(activity_name)  # Adiciona o nome da atividade à lista
        # Para pegar a nota máxima:
        max_point = []
        max_point.append(submission.get('studentSubmissions')[0].get('submissionHistory')[2].get('gradeHistory', {}).get('maxPoints'))
        # ------------
        # Inicializa a lista de notas para a atividade atual
        data = []
        for ss in submission.get('studentSubmissions',[]):
            # Retorna o nome do estudante
            actor_user_id = ss.get('submissionHistory', [{}])[0].get('stateHistory', {}).get('actorUserId')
            student_name = api.get_student_name(actor_user_id)
            #------------
            points_earned = []
            for history in ss.get('submissionHistory', []):
                grade_history = history.get('gradeHistory', {})
                points_earned.append(grade_history.get('pointsEarned', '-'))
                if points_earned and points_earned != ['-'] and points_earned != ['-', '-']:
                    points_earned = [points for points in points_earned if points != '-']
                    data.append({'nome': student_name, 'nota': points_earned[0]})
                    break
        value_points.append(max_point)
        # Cria a estrutura final com nome da atividade como chave e notas como valor
        students_earned.append({'atividade': activity_name, 'alunos': data})
    # Inverte a lista para que as primeiras atividades venham primeiro
    students_earned.reverse()
    value_points.reverse()
    flat_value_points = [item for sublist in value_points for item in sublist]
    return students_earned, flat_value_points

def group_by_alunos(table_data):
    """Obtém a nota pela média arentimetica da soma de todas as notas"""
    # Lista para armazenar os resultados
    json_formatado = {}
    # Lista para realizar os calculos
    json_formatado_calc = {}

    for atividade in table_data:
        nota_final = 0
        aluno_nome = ""
        for aluno in atividade["alunos"]:
            nota_final = 0
            aluno_nome = aluno["nome"]["fullName"]
            nota = aluno["nota"]
            if aluno_nome in json_formatado_calc:
                json_formatado_calc[aluno_nome]["notas"].append(nota)
            else:
                json_formatado_calc[aluno_nome] = {"notas": [nota]}
            nota_final = format(round(np.sum(json_formatado_calc[aluno_nome]["notas"])))
            if aluno_nome in json_formatado:
                json_formatado[aluno_nome]["nota"] = nota_final
            else:
                json_formatado[aluno_nome] = {"aluno": aluno["nome"], "nota": [nota]}

        
    # Converta o dicionário formatado em uma lista
    json_formatado = list(json_formatado.values())
    return json_formatado

def group_by_percents(table_data):
    """Obtém a nota pela média arentimetica do valor obtido e o valor maximo de uma tarefa"""
    # Lista para armazenar os resultados
    json_formatado = {}
    # Lista para realizar os calculos
    json_formatado_calc = {}

    for atividade in table_data:
        nota_final = 0
        aluno_nome = ""
        for aluno in atividade["alunos"]:
            nota_final = 0
            aluno_nome = aluno["nome"]["fullName"]
            nota = aluno["nota"]
            if aluno_nome in json_formatado_calc:
                json_formatado_calc[aluno_nome]["notas"].append(nota)
            else:
                json_formatado_calc[aluno_nome] = {"notas": [nota]}
            nota_final = format(round(np.sum(json_formatado_calc[aluno_nome]["notas"])*100/np.sum(session['nota_maxima'])))
            if aluno_nome in json_formatado:
                json_formatado[aluno_nome]["nota"] = nota_final
            else:
                json_formatado[aluno_nome] = {"aluno": aluno["nome"], "nota": [nota]}

    print("TA VINDO AQUI")
    json_formatado = list(json_formatado.values())
    return json_formatado

def exist_json():
    """Verifica se existe um arquivo Turmas.json"""
    
    if os.path.exists(path) and os.path.isfile(path):
        return True
    return False

def salvar_json(curso_data):
    """Salva o arquivo data.json"""
    with open(temp, 'w') as token_file:
        json.dump(curso_data, token_file)

def verifica_link(link, dominio_desejado):
    # Analise o URL fornecido
    url_parse = urlparse(link)
    print(url_parse)

    # Verifique se o domínio no URL corresponde ao domínio desejado
    if url_parse.netloc == dominio_desejado:
        return True
    else:
        return False

def get_all_turmas():
    """Busca todos os registros de Turmas.json"""
    if not os.path.exists(path):
        return "Nenhuma turma salva"
    try:
        with open(path, 'r') as turmas_file:
            turmas = json.load(turmas_file)
    except json.JSONDecodeError as e:
        turmas = "Nenhuma turma salva"
    return turmas

def get_turma(turmas_do_usuario, turma):
    """Busca um registro especifico de Turmas.json"""
    for turmas in turmas_do_usuario:
        if turmas.turmaID == int(turma):
            return turmas
    return None
    

def set_turma(turma):
    """VSalva um novo registro no arquivo Turmas.json"""
    try:
        with open(path, 'r') as turmas_file:
            turmas = json.load(turmas_file)
    except json.JSONDecodeError:
        turmas = {}
    
    turmas[turma['nome']] = turma

    with open(path, 'w') as turmas_file:
        json.dump(turmas, turmas_file)

def form_get_nomes(form):
    """Reordena os nomes dos alunos baseado no arquivo Turmas.json"""
    try:
        file_stream = io.BytesIO(form.read())
        dados = pd.read_csv(file_stream)
        dados.columns = dados.columns.str.replace('Endereço de e-mail', 'Endereco de e-mail')
        cols_to_keep = ['Sobrenome', 'Nome', 'Endereco de e-mail']
        alunos_infos = dados.drop(columns=[c for c in dados.columns if c not in cols_to_keep])
        alunos_infos = alunos_infos.drop(index=[0, 1])
        alunos_list = alunos_infos.to_dict(orient='records')
        return alunos_list
    except Exception as e:
        print(e)

def edit_turma(chave, turma):
    """Edita ocorrências no arquivo Turmas.json"""
    try:
        with open(path, 'r') as turmas_file:
            turmas = json.load(turmas_file)
    except json.JSONDecodeError:
        turmas = {}

    if chave in turmas:
        turmas[chave] = turma
        with open(path, 'w') as turmas_file:
            json.dump(turmas, turmas_file)
    else:
        print(f"A turma '{chave}' não existe.")

def delete_turma(chave):
    """Remove uma ocorrência do arquivo Turmas.json"""
    try:
        with open(path, 'r') as turmas_file:
            turmas = json.load(turmas_file)
    except json.JSONDecodeError:
        turmas = {}

    if chave in turmas:
        del turmas[chave]
        with open(path, 'w') as turmas_file:
            json.dump(turmas, turmas_file)
    else:
        print(f"A turma '{chave}' não existe.")

def reordenar_turmas_no_json(nova_ordem):
    """Reordena as ocorrências do arquivo Turmas.json"""
    with open(path, 'r') as file:
        turmas = json.load(file)
    turmas = {turma: turmas[turma] for turma in nova_ordem}
    with open(path, 'w') as file:
        json.dump(turmas, file)