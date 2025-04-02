import os
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GEMINI_API_KEY! Check your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash-lite' 
try:
    gemini_model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
except Exception as e:
    print(f"Error initializing model {DEFAULT_GEMINI_MODEL}: {e}")
    gemini_model = None

async def get_health_response(question):
    if gemini_model is None:
        return f"Error: Could not initialize the Gemini model ({DEFAULT_GEMINI_MODEL}). Please check the logs."
    try:
        response = gemini_model.generate_content(
            [{"role": "user", "parts": [question]}],
            stream=False 
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

async def send_long_message(update: Update, text: str, chunk_size: int = 4000) -> None:
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        await update.message.reply_text(chunk)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(f"Hello! I am your AI Health Assistant powered by Gemini ({DEFAULT_GEMINI_MODEL}). Ask me anything about health.")

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    response = await get_health_response(user_text)
    await send_long_message(update, response)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
    