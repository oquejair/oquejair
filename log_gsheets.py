import os
import base64
import json

import gspread

def login_sheets():
    spreadsheet_id = os.environ["GOOGLE_SHEET_ID"]
    conteudo_codificado = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
    conteudo = base64.b64decode(conteudo_codificado)
    credentials = json.loads(conteudo)
    service_account = gspread.service_account_from_dict(credentials)
    spreadsheet = service_account.open_by_key(spreadsheet_id)
    
    return spreadsheet

if __name__ == "__main__":
    login_sheets()
