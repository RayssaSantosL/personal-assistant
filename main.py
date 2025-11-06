from fastapi import FastAPI, Request
import requests
import datetime
import gspread

app = FastAPI()

# Autenticação com Google Sheets
gc = gspread.service_account(filename='credentials.json')
sheet = gc.open("Controle Financeiro").sheet1

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    message = data["messages"][0]["text"]["body"]

    # 1️⃣ Enviar pro Groq
    groq_response = requests.post(
        "https://api.groq.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {YOUR_GROQ_KEY}"},
        json={
            "model": "mixtral-8x7b",
            "messages": [{"role": "user", "content": f"Entenda isso e retorne em JSON: {message}"}]
        }
    )
    parsed = groq_response.json()["choices"][0]["message"]["content"]

    # 2️⃣ Gravar no Sheets
    dados = eval(parsed)  # cuidado aqui — depois vamos validar JSON
    sheet.append_row([
        str(datetime.date.today()),
        dados["categoria"],
        dados["valor"],
        dados.get("descricao", "")
    ])

    # 3️⃣ Responder usuário
    reply = f"✅ Adicionado: {dados['valor']} em {dados['categoria']}."
    send_whatsapp(reply)
    return {"status": "ok"}

def send_whatsapp(msg):
    requests.post(
        "https://graph.facebook.com/v19.0/YOUR_PHONE_ID/messages",
        headers={"Authorization": f"Bearer {YOUR_META_TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": "55SEUNUMERO",
            "type": "text",
            "text": {"body": msg}
        }
    )
