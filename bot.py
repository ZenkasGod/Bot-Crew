import os
import discord
from discord.ext import commands
import asyncio
import time
import json
from dotenv import load_dotenv
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load token từ file .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Load config.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Không tìm thấy file cấu hình: {CONFIG_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

PREFIX = config.get("prefix", "!")  # Lấy prefix từ config.json

# Khởi tạo bot với prefix và intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Phải bật message_content để đọc tin nhắn
intents.members = True
intents.presences = True  # Cho phép bot xem trạng thái hoạt động của người dùng
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Danh sách theo dõi người dùng on duty
bot.active_duty_users = {}

async def load_cogs():
    for folder in os.listdir("cogs"):
        cog_path = f"cogs.{folder}"
        if os.path.isdir(os.path.join("cogs", folder)):
            for filename in os.listdir(os.path.join("cogs", folder)):
                if filename.endswith(".py") and not filename.startswith("_"):
                    full_cog_path = f"cogs.{folder}.{filename[:-3]}"
                    try:
                        await bot.load_extension(full_cog_path)
                        print(f"Loaded cog: {full_cog_path}")
                    except Exception as e:
                        print(f"Không thể load {full_cog_path}: {e}")

@bot.event
async def on_ready():
    print(f"Bot đã online với tên: {bot.user}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(config["DISCORD_TOKEN"])

asyncio.run(main())




