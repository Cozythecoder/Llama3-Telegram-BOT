import os
import telebot
import replicate
import time
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

load_dotenv()

API_KEY = os.getenv("TELEGRAM_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = telebot.TeleBot(API_KEY)

# Set the API token for replicate
replicate.Client(api_token=REPLICATE_API_TOKEN)

# Function to handle /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_start_help_message(message):
    bot.reply_to(message, "Hello! How can I assist you today? Just type your question or prompt.")

# Function to handle text input
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.lower()  # Convert to lowercase for easier matching

    # Check if the input is asking about someone's origin
    if "who is" in user_input or "where is" in user_input:
        response = "He is from Cambodia."
        bot.reply_to(message, response)
    else:
        # Process the input with replicate
        input_data = {
            "prompt": user_input,
            "max_tokens": 1024
        }

        # Send initial "Loading..." message
        sent_message = bot.reply_to(message, "Loading...")

        # Get the full response
        try:
            full_response = ""
            for event in replicate.stream(
                "meta/meta-llama-3.1-405b-instruct",
                input=input_data
            ):
                full_response += event.data
            # Edit the "Loading..." message with the full response
            bot.edit_message_text(
                chat_id=sent_message.chat.id,
                message_id=sent_message.message_id,
                text=full_response
            )
        except ApiTelegramException as e:
            if e.result_json.get('error_code') == 429:  # Rate limit error
                print(f"Rate limit hit. Retrying...")
                time.sleep(32)  # Retry after a delay
            else:
                # Handle other exceptions
                print(f"Failed to edit message: {e}")

bot.infinity_polling()
