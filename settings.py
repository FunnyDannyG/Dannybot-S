# ----------
# Imports
# ----------
import asyncio
import os
import threading

import discord
from discord.ext import commands

# ----------
# Variables
# ----------

# dannybot config
dannybot_prefixes = {"d.", "#", "D.", "ratio + "}  # bot prefix(es)
dannybot_token = os.getenv("TOKEN")  # token
dannybot_team_ids = {343224184110841856, 158418656861093888, 249411048518451200}
dannybot_denialRatio = 250  # chance for dannybot to deny your command input
dannybot_denialResponses = {
    "no",
    "nah",
    "nope",
    "no thanks",
}  # what dannybot says upon denial
dannybot = (
    os.getcwd()
)  # easy to call variable that stores our current working directory
cache_clear_onLaunch = True  # dannybot will clear his cache on launch if set to true
clean_pooter_onLaunch = True  # dannybot will clean up pooter on launch if set to true
database_acceptedFiles = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "mp4",
    "webm",
    "mov",
}  # list of accepted files for the bots public database
cmd_blacklist = ["0"]  # Users who cant use the bot lol
whitelist = {
    779136383033147403,
    367767486004985857,
    706353387855151105,
    922428724744454164,
    796606820348723230,
    1131490848014598268,
    352972878645428225,
}  # servers with full bot access

# configs for the image manipulation commands
imageLower = 250  # the smallest image width image commands will use. if the image is thinner than this, it will proportionally scale to this size
imageUpper = 1500  # the largest image width image commands will use. if the image is wider than this, it will proportionally scale to this size

# channel configs
bookmarks_channel = int(os.getenv("BOOKMARKS"))  # channel to send personal bookmarks to
logs_channel = int(os.getenv("LOGS"))  # channel to log commands

# more .env keys being assigned here
openai.api_key = os.getenv("OPENAI_API_KEY")  # i hope i can remove this soon
tenor_apikey = os.getenv("TENOR_KEY")
AlphaVantageAPI = os.getenv("AV_API_KEY")

# internal paths
Cookies = f"{dannybot}\\assets\\cookies.txt"  # set this to your YT-DL cookies
Waifu2x = f"{dannybot}\\tools\\waifu2x-caffe\\waifu2x-caffe-cui.exe"  # set this to the path of your waifu2x-caffe-cui.exe file in your waifu2x-caffe install

# 8ball responses for the 8ball command
ball_responses = {
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
    "yeah",
    "nah",
}

# logo list for the logo command
logolist = {
    "clan",
    "neon",
    "fluffy",
    "water",
    "smurfs",
    "style",
    "runner",
    "blackbird",
    "fabulous",
    "glow",
    "chrominium",
    "amped",
    "supermarket",
    "crafts",
    "fire",
    "steel",
    "glossy",
    "fifties",
    "retro",
    "beauty",
    "birdy",
    "inferno",
    "winner",
    "uprise",
    "global",
    "silver",
    "minions",
    "magic",
    "fancy",
    "orlando",
    "fortune",
    "swordfire",
    "roman",
    "golden",
    "outline",
    "funtime",
}

# this is for the undertext command
deltarune_dw = {
    "ralsei",
    "lancer",
    "king",
    "jevil",
    "queen",
    "spamton",
    "clyde",
    "lori",
    "rhombo",
}
