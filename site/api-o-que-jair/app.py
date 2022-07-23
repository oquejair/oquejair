import base64
import datetime
import json
import os

import gspread
import pandas as pd
import os
import requests
import gspread
import json

from datetime import date, datetime, timedelta
from github import Github

TOKEN_GITHUB = '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'

spreadsheet_id = os.environ["GOOGLE_SHEET_ID"]
conteudo_codificado = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
conteudo = base64.b64decode(conteudo_codificado)
credentials = json.loads(conteudo)
service_account = gspread.service_account_from_dict(credentials)
spreadsheet = service_account.open_by_key(spreadsheet_id)

worksheet = spreadsheet.worksheet("dados_agenda") 
dados = worksheet.get_all_records()
df = pd.DataFrame(dados)

#filtrar partidas e chegadas (não contabiliza como hora trabalhada)
partidas = (df[ df['compromisso'].str.contains('Partida')]).index
chegadas = (df[ df['compromisso'].str.contains('Chegada')]).index

#elimina esses dados do df
dados = df.drop(partidas)
dados = dados.drop(chegadas)

#tratar dados: substituir horas não trabalhadas por com 00h00
dados[['hora_inicio', 'hora_fim']] = dados[['hora_inicio', 'hora_fim']].replace('', '00:00')
dados[['hora_inicio', 'hora_fim']] = dados[['hora_inicio', 'hora_fim']].replace(' ', '00:00')
dados[['hora_inicio', 'hora_fim']] = dados[['hora_inicio', 'hora_fim']].fillna('00:00')

#padronizar horas
dados[['hora_inicio', 'hora_fim']] = dados[['hora_inicio', 'hora_fim']].replace(regex=r'h', value=':') + ":00"

#fazer lista dos dias trabalhados
date_list = df['data'].tolist()
date_list = list(set(date_list))
len(date_list)

lista_horas = []

#para cada index do total de linhas
for i in range(len(dados)):
  #cria variável que seleciona a linha
  row = dados.iloc[i]
  #cria variável que seleciona a data de cada linha
  check_date = dados.iloc[i, 0]

  for element in date_list:
    #se a data da lista for igual a data da linha
    if element == check_date:
      #seleciona a hora_inicio e transforma em datetime
      first_hour = row['hora_inicio']
      first_hour = datetime.strptime(first_hour, '%H:%M:%S')
      
      #seleciona a hora_fim e transforma em datetime
      last_hour = row['hora_fim']
      last_hour = datetime.strptime(last_hour, '%H:%M:%S')

      #calcula quantas horas trabalhou naquela linha
      total = last_hour - first_hour

      minutes = (total.total_seconds())/60
      
      lista_horas.append(minutes)

#tranforma as horas não trabalhadas de 0 para 1 (pq ao tornar int, o 0 é eliminado)
lista_um = [1 if value==0.0 else value for value in lista_horas]
tempo = list(map(int, lista_um))

#elimina valores negativos que são erros na agenda
for index, value in enumerate(tempo):
    if value < 0:
      tempo[index] = 1

#cria nova coluna
dados['horas_trabalhadas'] = tempo

#agrupa por data e soma as horas trabalhadas por dia
soma = dados.groupby(['data'])['horas_trabalhadas'].sum()

#transforma esse df em lista
time_dict = soma.to_dict()

#Checa se depois do tratamento o date_list está igual
presidencia = df['data'].tolist()
presidencia = list(set(presidencia))
dias_presidencia = len(presidencia)

print(f"Jair trabalhou até agora {dias_presidencia} dias.")

#pega os valores do dicionário e converte em lista
lista_tempo = list(time_dict.values())

#função para contar quantos dias entre determinados horários
def conta_dias(min1, min2):
  count = 0
  for t in lista_tempo:
    if min1 >= t > min2:
      count += 1
  return count

#dict_horas_trabalhadas = dict()
lista = []

#trabalhou mais de 8h
count = 0
for t in lista_tempo:
  if t > 480:
    count += 1
lista.append(count)

#trabalhou mais de 8h
count = 0
for t in lista_tempo:
  if t > 480:
    count += 1

#trabalhou entre 7h-8h
lista.append(conta_dias(480, 420))

#trabalhou entre 6h-7h
lista.append(conta_dias(420, 360))

#trabalhou entre 5h-6h
lista.append(conta_dias(360, 300))

#trabalhou entre 4h-5h
lista.append(conta_dias(300, 240))

#trabalhou entre 3h-4h
lista.append(conta_dias(240, 180))

#trabalhou entre 2h-3h
lista.append(conta_dias(180, 120))

#trabalhou entre 1h-2h
lista.append(conta_dias(120, 60))

#trabalhou menos de 1h
lista.append(conta_dias(60, 1))

#todos os dias menos a soma todas os valores do dicionário
sum = 0
for i in lista:
  sum = sum + i
nao_trabalhados = dias_presidencia - sum
lista.append(nao_trabalhados)

#cria lista de dicionários (que serão os dados usados em json)
lista_dicts = [
    { "hora": "+8",
    "cor": "#f7fcfd"
    },
    { "hora": "7-8",
    "cor": "#e0ecf4"
    },
    { "hora": "6-7",
    "cor": "#bfd3e6"
    },
    { "hora": "5-6",
    "cor": "#9ebcda"
    },
    { "hora": "4-5",
    "cor": "#8c96c6"
    },
    { "hora": "3-4",
    "cor": "#8c6bb1"
    },
    { "hora": "2-3",
    "cor": "#88419d"
    },
    { "hora": "1-2",
    "cor": "#810f7c"
    },
    { "hora": "0-1",
    "cor": "#4d004b"
    },
    { "hora": "0",
    "cor": "#2f012d"
    }
]

#adiciona a chave "total" e o valor dos dias para cada análise
for dic,lis in zip(lista_dicts, lista):
  dic['total'] = lis 

#cria o arquivo json
json_file = json.dumps(lista_dicts)

#atualiza arquivo no github
g = Github(TOKEN_GITHUB) 

# repositorio
repo = g.get_repo("carinadourado/preguica")

# local do arquivo no repositorio
contents = repo.get_contents("/dados.json")

# atualizando arquivo 
repo.update_file(contents.path, 'Dados atualizados', json_file, contents.sha, branch="main")
print('Aquivo atualizado no GitHub')
