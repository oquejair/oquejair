import random

import datetime
import gspread
import pandas as pd
import pytz
import requests
import tweepy

from datetime import date, datetime, timedelta
from pytz import timezone

from log_tw import login_twitter
from log_gsheets import login_sheets
from agenda_dados import gera_data_hoje, gera_dados_hoje
from tw_update import today_update_tweet, update_tweet, update_sheets

#login no Twitter
api =  login_twitter()

data_fuso, data, url_hoje = gera_data_hoje()
hora_inicio, hora_fim, compromisso, local = gera_dados_hoje()

def should_tweet():
    data_fuso = gera_data_hoje()[0]
    hora_inicio, hora_fim, compromisso, local = gera_dados_hoje()
    
    now = data_fuso
    start = now - timedelta(minutes=10)
    end = now + timedelta (minutes=10)
    date_format = "%Y-%m-%d %H:%M:%S"
    data_formatada = data_fuso.strftime('%Y-%m-%d ')
    
    if hora_inicio != " ":
        for hour_tw in hora_inicio :
            nova_data = data_formatada + hour_tw.replace("h", ":")+ ":00"
            event = datetime.strptime(nova_data, date_format)
            event = pytz.timezone('America/Bahia').localize(event)
            if start <= event <= end:
                for tw_hi, tw_hf, tw_comp, tw_loc in zip(hora_inicio, hora_fim, compromisso, local):
                  if hour_tw == tw_hi:
                    api.create_tweet(text= f"De: {tw_hi} às {tw_hf} \nCompromisso: {tw_comp} \nLocal: {tw_loc}")
            else:
              print(f"{event} is not in the interval {start} - {end}")
    else:
        print("No schedule today")
        
    return date_format, now, start, end
def no_schedule():
    date_format, now, start, end = should_tweet()
    compromisso = gera_dados_hoje()[2]
    data_fuso = gera_data_hoje()[0]
    if compromisso == ["Sem compromisso oficial"]:
        tweet_9 = data_fuso.strftime('%Y-%m-%d ') + "09:00:00"
        tweet_9 = datetime.strptime(tweet_9, date_format)
        tweet_9 = pytz.timezone('America/Bahia').localize(tweet_9)
        if start <= tweet_9 <= end:
            without_schedule = ["Nada na agenda oficial (talvez Jair esteja no Planalto agora, comendo um pão com leite condensado)",
                                "Sem compromisso oficial... quem sabe uma 'motociata'?",
                                "Nada na agenda... Jair deve ver jogo do Palmeiras com a camiseta do Flamengo",
                                "Sem compromissos oficiais... #partiu chinelão!",
                                "Nada na agenda hoje... Jair deve ter ido na padoca da esquina tomar café pra ficar popular",
                                "Nada na agenda oficial... do jeito que Jair gosta!"
                                "Sem agenda hoje... dia bom pra dar uma volta de jetski e comer camarão, 'talquey?'",
                                "Sem compromisso oficial... Jair deve tá pensando em arrumar uma live pra criar polêmica.",
                                "Sem compromissos oficiais... #partiumoto",
                                "Nada na agenda hoje... Jair pode aparecer numa Havan pra fazer merchand",
                                "Nada na agenda! Bem melhor do que começar a trabalhar às 10h e terminar às 15h30, né?"]         
            answer = random.choice(without_schedule)
            api.create_tweet(text = answer)
        else:
            print(f"{tweet_9} is not in the interval {start} - {end}")
def variable_report():
    spreadsheet = login_sheets()
    #obtendo data de ontem
    yesterday = date.today() - timedelta(days=1)
    yesterday_format = yesterday.strftime('%d/%m/%Y')
    #abrindo e selecionando dados no df
    worksheet = spreadsheet.worksheet("dados_agenda") 
    dados = worksheet.get_all_records()
    df = pd.DataFrame(dados)
    df_data = df[df["data"] == yesterday_format]
    
    #excluindo linhas de tempo de viagem
    df_data = df_data[~df_data["compromisso"].str.contains("Partida", "Chegada", na=False)]
    #definindo primeira horas do início e fim da agenda
    first_hour = df_data.iloc[0, 1] 
    last_hour = df_data.iloc[-1, 2]
    
    return df_data, first_hour, last_hour
def calc_report():
    
    df_data, first_hour, last_hour = variable_report()
    time_final_minute = []
    time_final_hour = []
    
    #transformando as horas em datetime
    if last_hour != " ":
        hour_1 = list(df_data['hora_inicio'])
        hour_1 = [f"{x}:00" for x in hour_1]
        hour_1 = [hour1.replace("h", ":") for hour1 in hour_1]
        hour_1 = [datetime.strptime(hour1_d, '%H:%M:%S') for hour1_d in hour_1]
        hour_2 = list(df_data['hora_fim'])
        hour_2 = [f"{x}:00" for x in hour_2]
        hour_2 = [hour2.replace("h", ":") for hour2 in hour_2]
        hour_2 = [datetime.strptime(hour2_d, '%H:%M:%S') for hour2_d in hour_2]
        #cálculo de horas trabalhadas 
        time_zip = zip(hour_1,hour_2)
        time_total = timedelta()
        time_sub = [b - a for a, b in time_zip]
        for t in time_sub:
          time_total += t
        #tranformando o time_total em string e formatando
        time_final = str(time_total)
        time_final = time_final.split(":")
        time_final_hour = time_final[0]
        time_final_minute = time_final[1]
    return time_final_hour, time_final_minute
def daily_report():
    data_fuso = gera_data_hoje()[0]
    date_format, now, start, end = should_tweet()
    df_data, first_hour, last_hour = variable_report()
    time_final_hour, time_final_minute = calc_report()
    tweet_7 = data_fuso.strftime('%Y-%m-%d ') + "07:00:00"
    tweet_7 = datetime.strptime(tweet_7, date_format)
    tweet_7 = pytz.timezone('America/Bahia').localize(tweet_7)
    if start <= tweet_7 <= end:
      if first_hour != " ":
        if first_hour is not False:
            api.create_tweet(text= f"Ontem, Jair começou a trabalhar às {first_hour} e terminou às {last_hour}. \nTrabalhou um total de {time_final_hour}h{time_final_minute}min. \nQuanto será que vai ser hoje?")
      else:
        api.create_tweet(text= f"Ontem, Jair não teve agenda oficial. \nHoje será que é dia de rala?")
        
should_tweet()
no_schedule()
daily_report()

today_update_tweet()
update_tweet()
update_sheets()
