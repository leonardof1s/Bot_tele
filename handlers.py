import datetime
import logging
import groq
import requests
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext
from config import GROQ_API_KEY, API_KEY_CLIMA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = groq.Client(api_key=GROQ_API_KEY)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Olá! Use /ajuda para ver os comandos disponíveis.")


async def ajuda(update: Update, context: CallbackContext):
    mensagem = """
🔹 Comandos disponíveis:
/start - Inicia o bot
/ajuda - Mostra esta mensagem
/info - Mostra informações do usuário
/hora - Mostra a hora atual
/clima <cidade> - Mostra a previsão do tempo
/ia <pergunta> - Faz uma pergunta para a IA
    """
    await update.message.reply_text(mensagem, parse_mode="Markdown")


async def info(update: Update, context: CallbackContext):
    user = update.message.from_user
    mensagem = f"""
📌 Informações do Usuário:
👤 Nome: {user.first_name} {user.last_name or ""}
🆔 ID: {user.id}
🌎 Idioma: {user.language_code}
    """
    await update.message.reply_text(mensagem, parse_mode="Markdown")


async def hora(update: Update, context: CallbackContext):
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"⏰ Hora atual: {agora}", parse_mode="Markdown")


async def clima(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text(
            "❌ Você precisa informar uma cidade! Exemplo: /clima São Paulo"
        )
        return

    cidade = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY_CLIMA}&lang=pt&units=metric"

    try:
        resposta = requests.get(url).json()

        if resposta["cod"] != 200:
            await update.message.reply_text(
                "❌ Cidade não encontrada. Tente novamente."
            )
            return

        descricao = resposta["weather"][0]["description"].capitalize()
        temperatura = resposta["main"]["temp"]
        sensacao = resposta["main"]["feels_like"]
        umidade = resposta["main"]["humidity"]
        vento = resposta["wind"]["speed"]

        mensagem = f"""
🌤️ **Previsão do tempo para {cidade.capitalize()}**
📌 Clima: {descricao}
🌡️ Temperatura: {temperatura}°C
🤒 Sensação térmica: {sensacao}°C
💧 Umidade: {umidade}%
💨 Vento: {vento} m/s
        """

        await update.message.reply_text(mensagem, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ Erro ao obter a previsão do tempo.")


async def ia(update: Update, context: CallbackContext):
    texto = update.message.text.replace("/ia", "").strip()

    if not texto:
        await update.message.reply_text("❌ Envie um texto para que eu possa responder!")
        return

    try:
        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": texto}]
        )

        resposta_ia = resposta.choices[0].message.content if resposta.choices else None

        if resposta_ia:
            await update.message.reply_text(resposta_ia)
        else:
            await update.message.reply_text("❌ A IA não retornou nenhuma resposta válida.")

    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        await update.message.reply_text("❌ Erro ao consultar a IA. Tente novamente.")


def get_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("ajuda", ajuda),
        CommandHandler("info", info),
        CommandHandler("hora", hora),
        CommandHandler("clima", clima),
        CommandHandler("ia", ia),
    ]
