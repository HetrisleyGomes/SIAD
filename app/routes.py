from app import app, db
import os
from flask import render_template, redirect, flash, url_for, session, request, jsonify
from app.api.main import check_and_refresh_token, authenticate_google
import app.api.list_courses as api
import app.api.gagap as gg
import app.functions as func
from app.models import Professor, ProfessorTurmas, Turma
import app.Selenium.main as selenium
from app.api.forms import LoginForm
from decouple import config
from flask_login import login_user, login_required, logout_user, current_user
import math
import json

json_formatado = {}
nota_maxima = []

@app.route('/')
@app.route('/home')
def index():
    data = False
    if os.path.exists(config("DATA")):
        data = True
    turmas = []
    if current_user.is_authenticated:
        turmas_do_usuario = ProfessorTurmas.query.filter_by(professorID=current_user.professorId).all()
        for turma in turmas_do_usuario:
            turmas.append([Turma.query.join(ProfessorTurmas).filter(ProfessorTurmas.professorTurmasid == turma.professorTurmasid).all(), turma.professorTurmasid])
    #turmas = func.get_all_turmas()
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

# LOGIN -----------------------------------------------
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        usuario = Professor.query.filter_by(email=email, senha=password).first()
        if usuario:
            login_user(usuario)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    return render_template('login.html', form=form)


# Rota para fazer logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido!', 'success')
    return redirect(url_for('login'))

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
@login_required
def registrar():
    #dominio_alvo = "suap.ifrn.edu.br"
    turma = request.form.get('turma')
    etapa = request.form.get('etapa')
    turma_do_professor = ProfessorTurmas.query.get(turma)
    turma_info = Turma.query.filter_by(turmaID = turma_do_professor.turmaID).first()
    turma_info.alunos = json.loads(turma_info.alunos)
    url = turma_do_professor.link
    print(url)
    print(turma_info.alunos)
    try:
        selenium.iniciar(url, turma_info.alunos, etapa)
        flash('Notas Registradas no SUAP com sucesso!')
        return redirect(url_for('index'))
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
@login_required
def turmas_salvas():
    professor_id = current_user.professorId
    turmas_do_usuario = ProfessorTurmas.query.filter_by(professorID=professor_id).all()
    turmas = []
    for turma in turmas_do_usuario:
        turmas.append([Turma.query.join(ProfessorTurmas).filter(ProfessorTurmas.professorTurmasid == turma.professorTurmasid).all(), turma.professorTurmasid])
    return render_template("turmas-forms/turmas.html", turmas = turmas)

@app.route('/turma/novo')
@login_required
def turma_novo():
    turmas = Turma.query.all()
    return render_template("turmas-forms/nova_turma.html", turmas = turmas)

@app.route('/turma/salvar', methods=['POST'])
@login_required
def turma_salvar():
    url = request.form.get('link-turma')
    turma_id = request.form['turma-select']
    nova_turma = ProfessorTurmas(professorID=current_user.professorId, turmaID=turma_id, link=url)
    db.session.add(nova_turma)
    db.session.commit()
    return redirect(url_for('turmas_salvas'))

@app.route('/turma/ver/<string:turma>')
@login_required
def turma_ver(turma):
    turmas_do_usuario = ProfessorTurmas.query.filter_by(professorID=current_user.professorId).all()
    turma_ref = func.get_turma(turmas_do_usuario=turmas_do_usuario, turma=turma)
    turma_info = Turma.query.filter_by(turmaID = turma_ref.turmaID).first()
    turma_info.alunos = json.loads(turma_info.alunos)
    return render_template("turmas-forms/turma_ver.html", turma_ref= turma_ref, turma = turma_info, edit = False)

@app.route('/turma/editar/<string:turma>')
@login_required
def turma_edt(turma):
    #turmas_do_usuario = ProfessorTurmas.query.filter_by(professorID=current_user.professorId).all()
    #turma_ref = func.get_turma(turmas_do_usuario=turmas_do_usuario, turma=turma)
    turma_do_professor = ProfessorTurmas.query.get(turma)
    turma_info = Turma.query.filter_by(turmaID = turma_do_professor.turmaID).first()
    turma_info.alunos = json.loads(turma_info.alunos)
    return render_template("turmas-forms/turma_ver.html", turma_ref= turma_do_professor, turma = turma_info, edit = True)

@app.route('/turma/del/<string:turma>')
@login_required
def turma_del(turma):
    turma_do_professor = ProfessorTurmas.query.get(turma)
    db.session.delete(turma_do_professor)
    db.session.commit()
    #func.delete_turma(turma)
    return redirect(url_for('turmas_salvas'))

@app.route('/turma/salvar2', methods=['POST'])
@login_required
def turma_salvar2():
    professor_turma_id = request.form.get('professorturma-id')
    url_nova = request.form.get('link-turma')
    
    turma_do_professor = ProfessorTurmas.query.get(professor_turma_id)
    turma_do_professor.link = url_nova
    db.session.commit()
    #turma = {'nome': nome, 'url': v1['url'], 'alunos': v1['alunos']}
    #func.edit_turma(nome, turma)
    return redirect(url_for('turmas_salvas'))

@app.route('/reordenar_turmas', methods=['POST'])
@login_required
def reordenar_turmas():
    nova_ordem = request.json.get('novaOrdem')
    func.reordenar_turmas_no_json(nova_ordem)
    return jsonify({'status': 'success'})