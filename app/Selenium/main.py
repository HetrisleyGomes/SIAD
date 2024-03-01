#import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from selenium.webdriver.chrome.options import Options
from decouple import config

#print(webdriver.Chrome().service.service_args[1])

datapath = config("DATA")

def get_dados():
    dados = pd.read_json(datapath)
    return dados
        
def aluno_data_name(a, alunos):
    if type(a) == dict:
        a = a["fullName"]
    for aluno in alunos:
        nome = f"{aluno['Nome']} {aluno['Sobrenome']}"
        if nome == a and aluno.get('Nome-SUAP') is not None:
            return aluno['Nome-SUAP']
    return a
            

def iniciar(url, alunos, etapa):
    print(f"ETAPA: {etapa -2} <=======================")
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Executar em modo headless

    navegador = webdriver.Chrome(options=chrome_options)
    navegador.get(url)

    dados = []
    dados = get_dados()

    table = navegador.find_elements(By.XPATH, "//table[@id='table_notas']//tr")
    tabela_notas = []
    for row in table:
        tabela_notas.append(row)

    sleep(1)

    # Alunos do Classroom não encontrados
    acne = []
    # Alunos do SUAP faltantes
    asf = []

    for index,row in dados.iterrows():
        # Obtém a lista de alunos na tabela de registrar notas
        registro_falt_bool = True

        aluno_name = aluno_data_name(row['aluno'], alunos)
        print(f"Busando aluno: {aluno_name}")
        for element in navegador.find_elements(By.XPATH, "//*[@id='table_notas']/tbody/tr"):
            # Obtém o nome do aluno no SUAP
            element_text = element.find_element(By.XPATH, "td[2]/dl/dd").text
            nome_aluno = element_text.split('(')[0].strip()
            # Se o nome do aluno nesta linha for igual ao nome do aluno em dados.json
            if (nome_aluno.lower() == aluno_name.lower()):
                registro_falt_bool = False 
                nota_final = row['nota']
                # Se etapa 1 etapa_table = 3, se etapa 2 então etapa_table = 4
                #//*[@id="table_notas"]/tbody/tr[1]/td[3]/table/tbody/tr[1]/td[2]/input
                #//*[@id="table_notas"]/tbody/tr[1]/td[4]/table/tbody/tr[1]/td[2]/input
                navegador.find_element(By.XPATH, f"//table[@id='table_notas']//tr[{index + 1}]//td[{etapa}]//table//tr[1]//td[2]//input").send_keys(str(nota_final))
                print(f"Registrado, nota {nota_final}")
                break
            sleep(1)
        print("CHegou aqui")
        if (registro_falt_bool):
            if 'aluno' in row and 'fullName' in row['aluno']:
                acne.append(row['aluno']['fullName'])
            else:
                acne.append(row['aluno'])

        if (acne):
            print("Alunos do Classroom não encontrados:")
            for aluno in acne:
                print(aluno)

