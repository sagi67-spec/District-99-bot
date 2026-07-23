import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"🔍 TOKEN: {TOKEN[:10] if TOKEN else 'NO ENCONTRADO'}...")

if not TOKEN:
    print("❌ TOKEN NO ENCONTRADO")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user.name}")
    print(f"✅ ID: {bot.user.id}")
    await bot.tree.sync()
    print(f"✅ Comandos sincronizados")

@bot.tree.command(name="ping", description="🏓 Prueba")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

print("🚀 Iniciando...")
bot.run(TOKEN)
