import os
import praw
import logging
import json
from dotenv import load_dotenv
from telegram import Bot

def load_env():
    """Carrega as variáveis de ambiente do arquivo .env"""
    load_dotenv()
    return {
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
        "REDDIT_USER_AGENT": os.getenv("REDDIT_USER_AGENT"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHANNEL_ID": os.getenv("TELEGRAM_CHANNEL_ID")
    }

def get_quotes(reddit):
    """Obtém as postagens principais do subreddit r/quotes"""
    quotes = []
    subreddit = reddit.subreddit("quotes")
    for post in subreddit.hot(limit=5):  # Pegamos as 5 postagens principais
        if not post.stickied:
            quotes.append(post.title + "\n\n" + post.selftext)
    return quotes

def load_sent_quotes(file_path="sent_quotes.json"):
    """Carrega as citações enviadas de um arquivo JSON"""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return set(json.load(f))  # Carrega as citações como um conjunto
    return set()

def save_sent_quotes(sent_quotes, file_path="sent_quotes.json"):
    """Salva as citações enviadas em um arquivo JSON"""
    with open(file_path, "w") as f:
        json.dump(list(sent_quotes), f)  # Salva como lista, pois JSON não suporta set diretamente

def send_to_telegram(bot, chat_id, messages, sent_quotes, file_path="sent_quotes.json"):
    """Envia mensagens para um canal do Telegram sem repetir frases"""
    for msg in messages:
        if msg not in sent_quotes:  # Verifica se a mensagem já foi enviada
            bot.send_message(chat_id=chat_id, text=msg)
            sent_quotes.add(msg)  # Adiciona a mensagem ao conjunto de frases enviadas
            logging.info(f"Mensagem enviada: {msg}")
        else:
            logging.info(f"Mensagem repetida ignorada: {msg}")
    
    # Salva as citações enviadas no arquivo JSON
    save_sent_quotes(sent_quotes, file_path)

def main():
    logging.basicConfig(level=logging.INFO)
    env = load_env()
    
    reddit = praw.Reddit(
        client_id=env["REDDIT_CLIENT_ID"],
        client_secret=env["REDDIT_CLIENT_SECRET"],
        user_agent=env["REDDIT_USER_AGENT"]
    )
    
    bot = Bot(token=env["TELEGRAM_BOT_TOKEN"])
    chat_id = env["TELEGRAM_CHANNEL_ID"]
    
    # Carregar as citações já enviadas (se houver)
    sent_quotes = load_sent_quotes()

    quotes = get_quotes(reddit)
    if quotes:
        send_to_telegram(bot, chat_id, quotes, sent_quotes)
        logging.info("Mensagens enviadas com sucesso!")
    else:
        logging.info("Nenhuma citação encontrada.")

if __name__ == "__main__":
    main()
