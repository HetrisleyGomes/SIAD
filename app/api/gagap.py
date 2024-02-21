import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from flask import session

def classificar_nota_1(planilha, n_grupos):
    dados = pd.read_excel(planilha)
    dados2 = dados.loc[ (dados['Situação'] != "Cancelado") & (dados['Situação'] != "Trancado")]
    p1 = dados2.Nome.str.split(" ",n = 3, expand=True)
    p1.columns = ["N1","N2","N3","N4"]
    Nomes = p1['N1'].str.cat(p1['N2'],sep=" ")
    basefim = {"Nome":Nomes,"Nota1":dados2["Nota Etapa 1"],"Nota2":dados2["Nota Etapa 2"]}
    basefim = pd.DataFrame(basefim)
    
    n_alunos, n_colunas = dados2.shape
    k = int(np.ceil(n_alunos/n_grupos))
    basefim.index = range(basefim.shape[0])
    
    # Incluindo nomes "Vazios" na lista...
    tt = np.arange(basefim.shape[0],k*n_grupos)
    for i in tt:
        oo =pd.DataFrame([["None", 0, 0]],columns = basefim.columns)
        basefim = pd.concat([basefim, oo],axis=0)
    basefim.index = range(basefim.shape[0])
    
    # Matriz Vázia
    m = np.matrix(np.zeros((k,n_grupos)))
    basefim = basefim.sort_values(by=['Nota1'],ascending=False)
    basefim["Seq"] = np.arange(k*n_grupos)
    
    # Matriz de Organização
    mm = np.arange(n_grupos*k).reshape((k, n_grupos))
    for i in range(k):
        np.random.shuffle(mm[i,])
    
    grupos = pd.DataFrame(mm)
    grupos = grupos.applymap(str)

    kk = 0
    for i in range(k):
        for j in range(n_grupos):
            grupos.at[i,j] = basefim.Nome[mm[i,j]]
            kk=kk+1
    
    for j in range(n_grupos):
        text = "Grupo " + str(j+1)
        grupos.rename(columns = {j : text},inplace=True)

    return grupos
