![Untitled design (1)](https://agenciadeviagenscriativas.files.wordpress.com/2022/01/add-a-heading-1.png)

# O projeto

Olá! Este é um projeto que visa dar transparência à agenda oficial do presidente do Brasil. Foi idealizado e desenvolvido por alguém que ainda acredita que o voto e a fiscalização dos políticos eleitos são ferramentas poderosas de mudanças. O controle social fortalece a democracia!

## O que tem por aqui

O projeto tem 3 produtos finais:

- Robô no Telegram - https://t.me/oquejair_bot

- Robô no Twitter - https://twitter.com/OqueJair

- Publicação diária dos dados da agenda em planilha do Google Sheets

## Como funciona

O programa faz raspagem de dados no site da agenda oficial do presidente automaticamente. Neste repositório, você encontra em `agenda_dados.py` o código para capturar os dados do dia e em `agenda_passada.py`, o código que estabelece um período de tempo para que os dados de agendas passadas sejam capturados.
*(dica: insira no código o range de 30 /31 dias para que não sobrecarregue o sistema)*

No Telegram, o **robô OqueJair**, ao ser acionado por qualquer comando ou palavra, informa a agenda do dia do presidente do Brasil, atualizada no momento em que roda. O código está em `app.py`.

No Twitter, o **robô OqueJair** tuíta no momento em que for ocorrer um compromisso ou informa que naquele dia não há agenda oficial do presidente do Brasil. O código está em `twitter_bot.py`.

A planilha do Google, de acesso restrito, é atualizada diariamente antes das 00h com todos as informações disponibilizadas no dia pelo site oficial do governo. O código para acessá-la está na última função de `agenda_dados.py`.


## Licença

Todos com os códigos são abertos, com licença MIT, e dados gerados Creative Commons Attribution ShareAlike. 

Com esses códigos, você tem:

- a liberdade de usar o software para qualquer finalidade,
- a liberdade de mudar o software de acordo com suas necessidades,
- a liberdade de compartilhar o software com seus amigos e vizinhos e
- a liberdade de compartilhar as mudanças que você faz.

Caso utilize o código, utilize a mesma licença. 

## Bibliotecas

Para que seu código rode, tenha o Python 3.7+ e instale as bibliotecas:

- flask
- beautifulsoup4
- gspread == 5.0.0
- gunicorn
- pandas
- numpy
- oauth2client == 4.1.3
- requests
- tweepy == 4.4.0

## Atualização
Última atualização: 12/01/2021
