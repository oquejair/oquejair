import datetime
import os
import pytz
import random
import requests
import tweepy

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from pytz import timezone

#autenticação no Twitter
ckey = os.environ["TW_CONSUMER_KEY"]
cskey = os.environ["TW_CONSUMER_SECRET"]
atoken = os.environ["TW_ACCESS_TOKEN"]
astoken = os.environ["TW_ACCESS_TOKEN_SECRET"]

api = tweepy.Client(
    consumer_key = ckey,
    consumer_secret = cskey,
    access_token = atoken,
    access_token_secret = astoken
)

def gera_data_tw():
    data_fuso = datetime.now(timezone('America/Bahia'))
    data_hoje = data_fuso.strftime('%d/%m/%Y')
    data_url = data_fuso.strftime('%Y-%m-%d')
    url_hoje = f"https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica/{data_url}"
    return data_fuso, data_hoje, url_hoje

def gera_dados_tw():
    url_hoje = gera_data_tw()[2]
    resposta = requests.get(url_hoje)
    html = resposta.text
    soup = BeautifulSoup(html, "html.parser")

    #pegar hora do início
    tag_inicio = soup.find_all("time", {"class": "compromisso-inicio"})
    if tag_inicio != []:
      hora_inicio = [i.text for i in tag_inicio]
    else:
      hora_inicio = []

    #pegar hora do fim
    tag_fim = soup.find_all("time", {"class": "compromisso-fim"})
    if tag_fim != []:
      hora_fim = [h.text for h in tag_fim]
    else:
      hora_fim = []

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
      local = []

    return hora_inicio, hora_fim, compromisso, local

def should_tweet():
    data_fuso = gera_data_tw()[0]
    hora_inicio, hora_fim, compromisso, local = gera_dados_tw()

    now = data_fuso
    start = now - timedelta(minutes=15)
    end = now + timedelta (minutes=15)

    date_format = "%Y-%m-%d %H:%M:%S"
    data_formatada = data_fuso.strftime('%Y-%m-%d ')

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

def sem_agenda():
    compromisso = gera_dados_tw()[2]

    if compromisso == ["Sem compromisso oficial"]:
        now = data_fuso
        start = now - timedelta(minutes=5)
        end = now + timedelta (minutes=5)

        tweet_09 = data_fuso.strftime('%Y-%m-%d ') + "09:00:00"
        tweet_09 = datetime.strptime(tweet_09, date_format)

        tweet_14 = data_fuso.strftime('%Y-%m-%d ') + "14:00:00"
        tweet_14 = datetime.strptime(tweet_14, date_format)

        if start <= tweet_09 <= end or start <= tweet_14 <= end:
            phrases_no_agenda = ["Sem agenda hoje... dia bom pra dar uma volta de jetski e comer camarão, 'talquey?'",
                                "Sem compromisso oficial... Jair deve tá pensando em arrumar uma live pra criar polêmica.",
                                "Nada na agenda... Ê, do jeito que Jair gosta!",
                                "Sem compromissos oficiais... #partiumoto",
                                "Nada na agenda hoje... Jair pode aparecer numa Havan pra fazer merchand",
                                "Nada na agenda! Bem melhor do que começar a trabalhar às 10h e terminar às 15h30, né?"]
            no_agenda = random.choice(phrases_no_agenda)
            api.create_tweet(text = no_agenda)

   
should_tweet()
sem_agenda()
