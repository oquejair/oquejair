import csv

import gspread
import pandas as pd
import numpy as np
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from pytz import timezone

from log_gsheets import login_sheets

def generate_past_dates():
  url_list= []
  calendar_list = []

  tz_date = datetime.now(timezone('America/Bahia'))
  #tz_date  = datetime.strptime("2022-03-21", '%Y-%m-%d').date() #Usar para capturar outras datas
    
  for i in range(30):
    tz_date = tz_date - timedelta(days=1)
    past_date = tz_date.strftime('%d/%m/%Y')
    past_url_date = tz_date.strftime('%Y-%m-%d')
    past_url = f"https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica/{past_url_date}"

    url_list.append(past_url)
    calendar_list.append(past_date)
  
  return url_list, calendar_list

def generate_past_datas():
  url_list, calendar_list = generate_past_dates()
  
  dict_agenda = []
  list_soup = []

  for url in url_list:
    reply = requests.get(url)
    html_past = reply.text
    bsoup_past = BeautifulSoup(html_past, "html.parser")
    list_soup.append(bsoup_past)

    for soup_past in list_soup:
      #pegar hora do início
      tag_start = soup_past.find_all("time", {"class": "compromisso-inicio"})
      start_hour = [i.text for i in tag_start]
      if start_hour == []:
          start_hour = float('NaN')
    
      #pegar hora do fim
      tag_end= soup_past.find_all("time", {"class": "compromisso-fim"})
      end_hour = [h.text for h in tag_end]
      if end_hour == []:
          end_hour = float('NaN')

      #pegar compromisso
      tag_appointment = soup_past.find_all("h2", {"class": "compromisso-titulo"})
      appointment = [c.text for c in tag_appointment]
      if appointment == []:
          appointment = ["Sem compromisso oficial"]

      #pegar local
      tag_place = soup_past.find_all("div", {"class": "compromisso-local"})
      place = [l.text for l in tag_place]
      if place == []:
          place = float('NaN')

    dict_agenda.append({"hora_inicio":start_hour, "hora_fim": end_hour, "compromisso": appointment, "local":place})  
  
  return dict_agenda

def generate_past_df():
  url_list, calendar_list = generate_past_dates()
  dict_agenda = generate_past_datas()

  # criando dataframe:
  df_dict = pd.DataFrame(dict_agenda)
  df_dict["data"]=pd.Series(calendar_list)

  # usando explode para explodir as listas:
  stacked = df_dict.stack().explode().reset_index()
  stacked["uid"] = stacked.groupby(["level_0", "level_1"]).cumcount()
  past_df = stacked.pivot(["level_0", "uid"], "level_1", 0).reset_index(drop=True).rename_axis(None, axis=1)
  past_df["data"] = past_df["data"].fillna(method="ffill")
  past_df = past_df[["data", "hora_inicio", "hora_fim", "compromisso", "local"]]

  #substituindo NaN por " ":
  past_df.replace([np.inf, -np.inf], np.nan, inplace=True)
  past_df.fillna(' ', inplace=True)

  return past_df

#para quando rodar o código com datas específicas
#def send_past_sheets():
    #past_df = generate_past_df()
    #spreadsheet = login_sheets()
    
    #worksheet = spreadsheet.worksheet("dados_agenda") 
    #worksheet.append_rows(past_df.values.tolist())

#send_past_sheets()

#if __name__ == "__main__":
    #send_past_sheets()
