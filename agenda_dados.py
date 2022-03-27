import csv

import gspread
import pandas as pd
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime
from pytz import timezone

from log_gsheets import login_sheets

def gera_data_hoje():
    data_fuso = datetime.now(timezone('America/Bahia'))
    data = data_fuso.strftime('%d/%m/%Y')
    data_url = data_fuso.strftime('%Y-%m-%d')
    url_hoje = f"https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica/{data_url}"
    
    return data_fuso, data, url_hoje

def gera_dados_hoje():
    url_hoje = gera_data_hoje()[2]
    resposta = requests.get(url_hoje)
    html = resposta.text
    soup = BeautifulSoup(html, "html.parser")

  #pegar hora do início
    tag_inicio = soup.find_all("time", {"class": "compromisso-inicio"})
    if tag_inicio != []:
        hora_inicio = [i.text for i in tag_inicio]
    else:
        hora_inicio = " "

  #pegar hora do fim
    tag_fim = soup.find_all("time", {"class": "compromisso-fim"})
    if tag_fim != []:
        hora_fim = [h.text for h in tag_fim]
    else:
        hora_fim = " "

  # pegar compromisso
    tag_compromisso = soup.find_all("h2", {"class": "compromisso-titulo"})
    if tag_compromisso != []:
        compromisso = [c.text for c in tag_compromisso]
    else:
        compromisso = ["Sem compromisso oficial"]

  # pegar local
    tag_local = soup.find_all("div", {"class": "compromisso-local"})
    if tag_local != []:
        local = [l.text for l in tag_local]
    else:
        local = " "
    
    return hora_inicio, hora_fim, compromisso, local
    
def gera_df():
    data = gera_data_hoje()[1]
    hora_inicio, hora_fim, compromisso, local = gera_dados_hoje()
    lista = list(zip(hora_inicio, hora_fim, compromisso, local))
    df = pd.DataFrame(lista, columns=["hora_inicio", "hora_fim", "compromisso", "local"])
    df['data']=pd.Series(data)
    df['data'] = df['data'].fillna(method='ffill')
    df = df[["data", "hora_inicio", "hora_fim", "compromisso", "local"]] 
    
    return df

def envia_sheets():
    df = gera_df()
    spreadsheet = login_sheets()

    worksheet = spreadsheet.worksheet("dados_agenda") 
    worksheet.append_rows(df.values.tolist())

if __name__ == "__main__":
    envia_sheets()
