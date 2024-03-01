from app import app
import os
from flask import render_template, redirect, flash, url_for, session, request, jsonify
from app.api.main import check_and_refresh_token, authenticate_google
import app.api.list_courses as api
import app.api.gagap as gg
import app.functions as func
import app.Selenium.main as selenium
from decouple import config
import math

json_formatado = {}
nota_maxima = []

@app.route('/')
@app.route('/home')
def index():
    data = False
    if os.path.exists(config("DATA")):
        data = True
    turmas = func.get_all_turmas()
    return render_template("index.html",json = func.exist_json(), turmas = turmas, data = data)

@app.route('/notas')
def notas():
    a = check_and_refresh_token()
    if a ==  False:
        return render_template("nota_JustCSV.html")
    cursos = api.listar_cursos()
    return render_template("nota.html", cursos = cursos['courses'])

@app.route('/curso/<int:curso_id>')
def curso(curso_id):
    curso_info, nomes = api.get_estudantes(curso_id)
    table_data, nota_maxima = func.extract_points_earned(curso_info, nomes)
    session['nome_turma'] = api.get_course_name(curso_id)
    session['table_data'] = table_data
    session['nota_maxima'] = nota_maxima
    return render_template("curso.html", data = table_data,  nota_maxima = nota_maxima, turma_nome = session.get('nome_turma'))

@app.route('/autorizar')
def autorizar():
    return render_template("autorizar.html")

@app.route('/autorizar/autenticar')
def autenticar():
    authenticate_google()
    return redirect(url_for('index'))

# SALVAR NOTAS ------------------------------------

@app.route('/arquivo/csv')
def arquivo_csv():
    return render_template("arquivocsv.html")

@app.route('/save/api', methods=['POST'])
def save_api():
    metodo = request.form.get('valor')
    table_data = session.get('table_data', {})
    if metodo == 'valorInteiro':
        # Salva a nota dos alunos usando a soma por inteiros
        json_formatado = func.group_by_alunos(table_data)
        erros = []
        for aluno in json_formatado:
            if int(aluno["nota"]) > 100:
                erros.append(f"O aluno {aluno['aluno']['fullName']} tem uma nota de {aluno['nota']}, um valor maior que 100.")
        if not erros:
            func.salvar_json(json_formatado)
            flash('Notas Registradas salvas na mémoria, agora registre as notas!')
            print("SEM ERROS")
            return redirect(url_for('index'))
        print("COM ERROS")
        session['erro'] = erros
        return redirect(url_for('confirm'))
    elif metodo == 'PorcentagemInteiro':
        # Salva a nota dos alunos usando a média por porcentagem
        table_data = session.get('table_data', {})
        json_formatado = func.group_by_percents(table_data)
        func.salvar_json(json_formatado)
        flash('Notas Registradas salvas na mémoria, agora registre as notas!')
        return redirect(url_for('index'))
    elif metodo == 'converter':
        # Transforma notas maior que 100 em 100
        json_formatado = func.group_by_alunos(table_data)
        for aluno in json_formatado:
            if int(aluno["nota"]) > 100:
                aluno["nota"] = 100
        func.salvar_json(json_formatado)
        flash('Notas Registradas salvas na mémoria, agora registre as notas!')
        return redirect(url_for('index'))
        
@app.route('/confirm')
def confirm():
    error_msg = session.get('erro')
    return render_template('confirmar.html', erros = error_msg)

@app.route('/registrar', methods=['POST'])
def registrar():
    #dominio_alvo = "suap.ifrn.edu.br"
    turma = request.form.get('turma')
    etapa = request.form.get('etapa')
    print(turma)
    turma_info = func.get_turma(turma)
    try:
        selenium.iniciar(turma_info['url'], turma_info['alunos'], etapa)
        import os
        path = config('DATA')
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        return f'Erro ao executar o script Selenium: {str(e)}'
    flash('Notas Registradas no SUAP com sucesso!')
    return redirect(url_for('index'))

@app.route('/save/csv', methods=['POST'])
def save_csv():
    metodo = request.form.get('valor')
    form = request.files['form-csv']
    aluno, nota, gab = func.passFormFile(form)
    if metodo == 'valorInteiro':
        json_formatado = func.formSoma(aluno, nota)
        for aluno in json_formatado:
            if int(aluno["nota"]) > 100:
                aluno["nota"] = 100
        func.salvar_json(json_formatado)
    elif metodo == 'PorcentagemInteiro':
        json_formatado = func.formPorcento(aluno, nota, gab)
        func.salvar_json(json_formatado)
    flash('Notas Registradas salvas na mémoria, agora registre as notas!')
    return redirect(url_for('index'))

# GAGAP ------------------------------------

@app.route('/gagap')
def gagap_form():
    return render_template("gagap/gagap_form.html")

@app.route('/gagap/analitc', methods=['POST'])
def gagap_analitics():
    planilha = request.files['planilha']
    grupos = int(request.form.get('grupos'))
    data_full = gg.classificar_nota_1(planilha, grupos)
    data_html = data_full.to_html(classes='table table-collspan', index=False)
    size = math.floor(100/grupos)
    return render_template("gagap/gagap.html", data = data_html, n = size)

# TURMAS ------------------------------------

@app.route('/turmas')
def turmas_salvas():
    turmas = func.get_all_turmas()
    return render_template("turmas-forms/turmas.html", turmas = turmas)

@app.route('/turma/novo')
def turma_novo():
    return render_template("turmas-forms/nova_turma.html")

@app.route('/turma/salvar', methods=['POST'])
def turma_salvar():
    nome = request.form.get('nome-turma').lower()
    url = request.form.get('link-turma').lower()
    form = request.files['form-csv']
    list_info = func.form_get_nomes(form)
    turma = {'nome': nome, 'url': url, 'alunos': list_info}
    func.set_turma(turma)
    return redirect(url_for('turmas_salvas'))

@app.route('/turma/ver/<string:turma>')
def turma_ver(turma):
    turma_info = func.get_turma(turma)
    return render_template("turmas-forms/turma_ver.html", turma = turma_info, edit = False)

@app.route('/turma/editar/<string:turma>')
def turma_edt(turma):
    turma_info = func.get_turma(turma)
    return render_template("turmas-forms/turma_ver.html", turma = turma_info, edit = True)

@app.route('/turma/del/<string:turma>')
def turma_del(turma):
    func.delete_turma(turma)
    return redirect(url_for('turmas_salvas'))

@app.route('/turma/salvar2', methods=['POST'])
def turma_salvar2():
    nome = request.form.get('nome-turma').lower()
    email = request.form.getlist('email-aluno')
    suap = request.form.getlist('name-suap')
    v1 = func.get_turma(nome)
    for aluno in v1['alunos']:
        for i, e in enumerate(email):
            if aluno['Endereco de e-mail'] == e:
                if suap[i] != 'Não registrado':
                    aluno['Nome-SUAP'] = suap[i]
    turma = {'nome': nome, 'url': v1['url'], 'alunos': v1['alunos']}
    func.edit_turma(nome, turma)
    return redirect(url_for('turmas_salvas'))

@app.route('/reordenar_turmas', methods=['POST'])
def reordenar_turmas():
    nova_ordem = request.json.get('novaOrdem')
    func.reordenar_turmas_no_json(nova_ordem)
    return jsonify({'status': 'success'})