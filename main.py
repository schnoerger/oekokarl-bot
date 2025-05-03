import os
import openai
import discord
import asyncio
import traceback
from flask import Flask, request, jsonify, send_file
from threading import Thread

# OpenAI-API-Key laden
openai.api_key = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Stichwörter für Discord-Filterung
STICHHALTER = ["ökokarl", "nachhaltig", "swot", "verpackung", "projekt"]

# Flask-Webserver
app = Flask(__name__)

@app.route("/")
def startseite():
    return send_file("index.html")

@app.route("/chat", methods=["POST"])
def webchat():
    data = request.get_json()
    frage = data.get("frage", "")
    if not frage.strip():
        return jsonify({"antwort": "Bitte stelle eine sinnvolle Frage."})

    try:
        antwort = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ÖkoKarl, ein freundlicher, hilfsbereiter Chatbot für ein Schulprojekt zum Thema Nachhaltigkeit im Einzelhandel. Antworte immer auf Deutsch."},
                {"role": "user", "content": frage}
            ]
        )
        return jsonify({"antwort": antwort.choices[0].message.content})
    except Exception as e:
        print("Fehler (Web):", e)
        return jsonify({"antwort": "Hoppla! Die Antwort hat nicht geklappt."})

# Discord-Bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

async def frage_an_openai(frage):
    try:
        antwort = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ÖkoKarl, ein freundlicher, hilfsbereiter Chatbot für ein Schulprojekt zum Thema Nachhaltigkeit im Einzelhandel. Antworte immer auf Deutsch."},
                {"role": "user", "content": frage}
            ]
        )
        return antwort.choices[0].message.content
    except Exception as e:
        print("Fehler (Discord):", e)
        return "Hoppla! Da ging was schief."  

@client.event
async def on_ready():
    print(f"{client.user} ist online und bereit!")

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    inhalt = message.content.lower()
    if any(wort in inhalt for wort in STICHHALTER):
        antwort = await frage_an_openai(message.content)
        await message.channel.send(antwort)

# Webserver starten
def start_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=start_flask).start()

# Discord-Bot starten
client.run(DISCORD_TOKEN)
