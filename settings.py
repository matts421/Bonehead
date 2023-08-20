import pathlib
import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
MW_DICTIONARY = os.getenv("MW_DICTIONARY")
MUSIC_BOT_PASSWORD = os.getenv("MUSIC_BOT_PASSWORD")

BASE_DIR = pathlib.Path(__file__).parent

CMDS_DIR = BASE_DIR / "cmds"
COGS_DIR = BASE_DIR / "cogs"

GUILDS_ID = discord.Object(id = int(os.getenv("GUILD")))
FEEDBACK_CH = int(os.getenv("FEEDBACK_CH"))

MEMBERS_JSON_PATH = BASE_DIR / "members.json"