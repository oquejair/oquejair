import base64
import datetime
import json
import os
import random

import gspread
import requests
from flask import request, Flask

from agenda_dados import gera_dados_hoje


spreadsheet_id = os.environ["GOOGLE_SHEET_ID_BOT"]
conteudo_codificado = os.environ["GOOGLE_SHEETS_CREDENTIALS_BOT"]
conteudo = base64.b64decode(conteudo_codificado)
credentials = json.loads(conteudo)

service_account = gspread.service_account_from_dict(credentials)
spreadsheet = service_account.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet("Página1") 

app = Flask(__name__)

@app.route("/telegram", methods=["POST"])
def telegram():
    # Recebe dados da mensagem
    datahora = str(datetime.datetime.now())
    update = request.json
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"].lower()
    username = update["message"]["from"].get("username", "")
    first_name = update["message"]["from"]["first_name"]
    last_name = update["message"]["from"]["last_name"]

    # Guarda na planilha a mensagem recebida
    worksheet.append_row([datahora, chat_id, "robô", username, first_name, last_name, text])
    
    # Gera a resposta, responde e guarda na planilha
    token = os.environ["TELEGRAM_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    datahora = str(datetime.datetime.now())
    if text:
        hora_inicio, hora_fim, compromisso, local = gera_dados_hoje()
        answer = "Quer saber o que Jair tá fazendo hoje?"
        message = {"chat_id": chat_id, "text": answer}
        response = requests.post(url, data=message)
        worksheet.append_row([datahora, "robô", chat_id, "", "", "", answer])
        
        if hora_inicio != " - ":
            for line in range(len(hora_inicio)):
                schedule = f"\n\nHorário: {hora_inicio[line]} \nCompromisso: {compromisso[line]} \nLocal: {local[line]}"
                schedule = schedule.replace("['", "").replace("']", "")
                message = {"chat_id": chat_id, "text": schedule}
                response = requests.post(url, data=message)
                worksheet.append_row([datahora, "robô", chat_id, "", "", "", schedule])
        else:
            without_schedule = ["Nada na agenda oficial (talvez Jair esteja no Planalto agora, comendo um pão com leite condensado)",
                                "Sem compromisso oficial... quem sabe uma 'motociata'?",
                                "Nada na agenda... Jair deve ver jogo do Palmeiras com a camiseta do Flamengo",
                                "Sem compromissos oficiais... #partiu chinelão!",
                                "Nada na agenda hoje... Jair deve ter ido na padoca da esquina tomar café pra ficar popular",
                                "Sem nada na agenda oficial... do jeito que Jair gosta!"]
            answer = random.choice(without_schedule)
            message = {"chat_id": chat_id, "text": answer}
            response = requests.post(url, data=message)
            worksheet.append_row([datahora, "robô", chat_id, "", "", "", answer])

    if response.json()["ok"] == False:
        raise RuntimeError("Erro ao responder mensagem para API do Telegram")
    
    # Finaliza
    return "ok"
