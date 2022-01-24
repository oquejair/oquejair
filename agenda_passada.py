import base64
import csv
import json
import os

import gspread
import pandas as pd
import numpy as np
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime
from pytz import timezone

from google.colab import drive
drive.mount('/content/drive')

def gera_data_passado():
    resultado = []
    calendario = []

    data = datetime.date(2019, 1, 30) #inserir data de 1 dia antes do mês que se quer verificar
    for i in range(31): #inserir número de dias que há no mês verificado
      data = data + datetime.timedelta(days=1)
      data_passado = data.strftime('%d/%m/%Y')
      data_pass = data.strftime('%Y-%m-%d')
      url_pass = f"https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica/{data_pass}"

      resultado.append(url_pass)
      calendario.append(data_passado)

    return resultado, calendario

def gera_dados_passado():
    dict_agenda = []
    lista_soup = []
    resultado, calendario = gera_data_passado()

    for url in resultado:
      resposta = requests.get(url)
      html = resposta.text
      bsoup = BeautifulSoup(html, "html.parser")
      lista_soup.append(bsoup)

      for soup in lista_soup:
        #pegar hora do início
        tag_inicio = soup.find_all("time", {"class": "compromisso-inicio"})
        hora_inicio = [i.text for i in tag_inicio]
        if hora_inicio == []:
            hora_inicio = float('NaN')

        #pegar hora do fim
        tag_fim = soup.find_all("time", {"class": "compromisso-fim"})
        hora_fim = [h.text for h in tag_fim]
        if hora_fim == []:
            hora_fim = float('NaN')

        #pegar compromisso
        tag_compromisso = soup.find_all("h2", {"class": "compromisso-titulo"})
        compromisso = [c.text for c in tag_compromisso]
        if compromisso == []:
            compromisso = ["Sem compromisso oficial"]

        #pegar local
        tag_local = soup.find_all("div", {"class": "compromisso-local"})
        local = [l.text for l in tag_local]
        if local == []:
            local = float('NaN')

      dict_agenda.append({"hora_inicio":hora_inicio, "hora_fim": hora_fim, "compromisso": compromisso, "local":local})  

    return dict_agenda

def gera_df_passado():
    resultado, calendario = gera_data_passado()
    dict_agenda = gera_dados_passado() 

    # criando dataframe:
    df_dict = pd.DataFrame(dict_agenda)
    df_dict["data"]=pd.Series(calendario)

    # usando explode para explodir as listas:
    stacked = df_dict.stack().explode().reset_index()
    stacked["uid"] = stacked.groupby(["level_0", "level_1"]).cumcount()
    df = stacked.pivot(["level_0", "uid"], "level_1", 0).reset_index(drop=True).rename_axis(None, axis=1)
    df["data"] = df["data"].fillna(method="ffill")
    df = df[["data", "hora_inicio", "hora_fim", "compromisso", "local"]]

    #substituindo NaN por " ":
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna('', inplace=True)

    return df

def envia_sheets_passado():
    df = gera_df()
    
    spreadsheet_id = os.environ["GOOGLE_SHEET_ID"]
    conteudo_codificado = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
    conteudo = base64.b64decode(conteudo_codificado)
    credentials = json.loads(conteudo)

    service_account = gspread.service_account_from_dict(credentials)
    spreadsheet = service_account.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet("dados_agenda") 
    worksheet.append_rows(df.values.tolist())
    
envia_sheets_passado()
