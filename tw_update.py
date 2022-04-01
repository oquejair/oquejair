import itertools 
import math
import sys
import textwrap

import datetime
import gspread
import pandas as pd
import pytz
import tweepy

from pytz import timezone
from datetime import date, datetime, timedelta

from log_tw import login_twitter
from log_gsheets import login_sheets
from agenda_dados import gera_data_hoje, gera_dados_hoje
from agenda_passada import generate_past_dates, generate_past_datas, generate_past_df

#login no Twitter
api =  login_twitter()

#login no Google Sheets
spreadsheet = login_sheets()

data_fuso, data, url_hoje = gera_data_hoje()
hora_inicio, hora_fim, compromisso, local = gera_dados_hoje()

# Checa se houve alterações na agenda de hoje após os eventos ocorrerem

def today_posted():
    data_today = datetime.now(timezone('America/Bahia'))
    data_tw = data_today.strftime('%Y-%m-%d')
    start_time = (datetime.strptime(data_tw, '%Y-%m-%d')).isoformat("T") + "Z"

    #pega os tweets que estão no perfil no dia
    tweets = api.get_users_tweets(id=1467647897470738433,
                              start_time = start_time,
                              max_results = 100,
                              user_auth=True)

    # Pega os tweets postados hoje
    today_tweets_list =[]
    today_posted_list = []

    for tweet in tweets:
        today_tweets_list.append(tweet)
        tweets_text = today_tweets_list[0]

        if tweets_text is not None:
          for posted_text in tweets_text:
            posted_text = posted_text.text
            today_posted_list.append(posted_text)
        else:
          today_posted_list = []

    return today_posted_list

def today_update_tweet():
    today_posted_list = today_posted()
    hora_inicio, hora_fim, compromisso, local = gera_dados_hoje()

    #Lista os tweets que deveriam estar postados agora
    today_tweet_check = []
    today_tweet_updates = []
    
    if today_posted_list != []:
        for inter in itertools.zip_longest(hora_inicio, hora_fim, compromisso, local):
            if None in inter:
                element_none = ['' if v is None else v for v in inter]
                phrase = "De: "+ element_none[0] + " às " + element_none[1] + " \nCompromisso: " + element_none[2] + " \nLocal: " + element_none[3]
            else:
                phrase = "De: "+ inter[0] + " às " + inter[1] + " \nCompromisso: " + inter[2] + " \nLocal: " + inter[3]
            today_tweet_check.append(phrase)

        #formatando as horas para poder comparar:
        hora_inicio_tw = []

        if hora_inicio != " ":
            for hora_ini in hora_inicio:
                hora_ini_date = datetime.today().strftime('%Y-%m-%d ')
                hora_ini_dateformat = hora_ini_date + hora_ini
                hora_ini_total = datetime.strptime(hora_ini_dateformat, "%Y-%m-%d %Hh%M")
                hora_ini_total = pytz.timezone('America/Bahia').localize(hora_ini_total)
                hora_inicio_tw.append(hora_ini_total)

        now_today = datetime.now(timezone('America/Bahia')).strftime('%Y, %m, %d, %H, %M')
        now_today = datetime.strptime(now_today, '%Y, %m, %d, %H, %M')
        now_today = pytz.timezone('America/Bahia').localize(now_today)

        if hora_inicio_tw != " ":
            for tw_hour in hora_inicio_tw:
                if tw_hour < now_today:
                    format_twh = tw_hour.strftime('%Hh%M')
                    for tweet_tw in today_tweet_check:
                        if tweet_tw not in today_posted_list:
                            if format_twh in tweet_tw:
                              tweet_tw_phrases = f"Atenção! Evento de hoje foi adicionado após ocorrer: \n{tweet_tw}"
                              today_tweet_updates.append(tweet_tw_phrases)
                              today_tweet_updates = list(set(today_tweet_updates))
                        else:
                            print(f"Tudo ok até aqui, sem atualizações")

        #postar tanto em caso de tweets curtos quanto longos
        if today_tweet_updates != []:
            for tweet_final in today_tweet_updates:
                tweet_length = len(tweet_final)
                if tweet_length <= 280: #caso for tweet curto
                    api.create_tweet(text=tweet_final)
                #para tweets longos:
                elif tweet_length >= 280:
                    tweet_length_limit = tweet_length / 280
                    tweet_chunk_length = tweet_length / math.ceil(tweet_length_limit)
                    tweet_chunks = textwrap.wrap(tweet_final,  math.ceil(tweet_chunk_length), break_long_words=False)

                    for x, chunk in zip(range(len(tweet_chunks)), tweet_chunks):
                        if x == 0:
                            api.create_tweet(text= f'1 of {len(tweet_chunks)} {chunk}')
                        else:
                            api.create_tweet(text= f'{x+1} of {len(tweet_chunks)} {chunk}')
    else:
        print("No tweets now")

# # # #  # # # #  # # # #  # # # #  # # # #  # # # #  # # # #  # # # #  # # # #  # # # #  # # # #  # # # #           
#Checa se houve alterações na agenda de até 1 mês atrás após os eventos ocorrerem  

url_list, calendar_list = generate_past_dates()
dict_agenda = generate_past_datas()
past_df = generate_past_df()

def check_updates():
    past_df = generate_past_df()
    new_values_list = []
    update_list = []
    
    worksheet = spreadsheet.worksheet("dados_agenda") 
    all_values =  worksheet.get_all_values()

    # retirar a coluna 'atualizacao' para poder comparar
    for v in all_values:
        v.pop(5)
        new_values_list.append(v)

    check_list = past_df.values.tolist()
    for value_update in check_list:
        if value_update not in new_values_list:
            update_list.append(value_update)
            
    #Remover "sem compromisso oficial" e chegadas e partidas de viagens
    if update_list != []:
        sem_compromisso  = [sem_compromisso for sem_compromisso in update_list if "Sem compromisso oficial" in sem_compromisso]
        for sem_compromisso_remove in sem_compromisso:
            if sem_compromisso_remove in update_list:
                update_list.remove(sem_compromisso_remove)

        partida  = [partida for partida in update_list if "Partida" in partida[3]]
        for partida_remove in partida:
            if partida_remove in update_list:
                update_list.remove(partida_remove)

        chegada  = [chegada for chegada in update_list if "Chegada" in chegada[3]]
        for chegada_remove in chegada:
            if chegada_remove in update_list:
                update_list.remove(chegada)

    return update_list

def update_tweet():
    update_list = check_updates()
    update_tweet_list = []

    if update_list != []:
        for tweet_up in update_list:
            tweet_past = f"Atenção! Agenda atualizada após a data do evento: \nData: {tweet_up[0]}\nDe: {tweet_up[1]} às {tweet_up[2]} \nCompromisso: {tweet_up[3]} \nLocal: {tweet_up[4]}"
            update_tweet_list.append(tweet_past)
    else:
        print("There are no updates")

    #tweetar se houver tanto tweets longos quanto curtos
    if update_tweet_list !=[]:
        for tw_past in update_tweet_list:
            tweet_length = len(tw_past)
            if tweet_length <= 280: #caso for tweet curto
                api.create_tweet(text=tw_past)
            #para tweets longos:
            elif tweet_length >= 280:
                tweet_length_limit = tweet_length / 280
                tweet_chunk_length = tweet_length / math.ceil(tweet_length_limit)
                tweet_chunks_past = textwrap.wrap(tw_past,  math.ceil(tweet_chunk_length), break_long_words=False)

                for x_past, chunk_past in zip(range(len(tweet_chunks_past)), tweet_chunks_past):
                    if x_past == 0:
                        api.create_tweet(text=f'1 of {len(tweet_chunks_past)} {chunk_past}')
                    else:
                        api.create_tweet(text=f'{x_past+1} of {len(tweet_chunks_past)} {chunk_past}')

def update_sheets():
    update_list = check_updates()

    if update_list != []:
        current_date = datetime.now(timezone('America/Bahia'))
        current_date_format = current_date.strftime('%d/%m/%Y')

        df_update = pd.DataFrame(update_list, columns = [['data', 'hora_inicio', 'hora_fim', 'compromisso', 'local']])
        df_update  = df_update.assign(atualizacao=current_date_format)

        worksheet = spreadsheet.worksheet("dados_agenda") 
        worksheet.append_rows(df_update.values.tolist())
    else:
        print("No updates to put in worksheets")

if __name__ == "__main__":        
    today_update_tweet()
    update_tweet()
    update_sheets()
