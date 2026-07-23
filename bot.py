"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
"""

import json
import os
import re
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"🔍 TOKEN: {TOKEN[:10] if TOKEN else 'NO ENCONTRADO'}...")

if not TOKEN:
    print("❌ TOKEN NO ENCONTRADO")
    exit(1)

DNI_FILE = "dnis.json"
ESCENAS_FILE = "escenas.json"
EVALUACIONES_FILE = "evaluaciones.json"
VOTACIONES_FILE = "votaciones.json"
AUTOS_FILE = "autos.json"
MULTAS_FILE = "multas.json"

NOMBRE_SERVIDOR = "DISTRICT 99"

# ==================== ROLES ====================
ROL_HOST_NOMBRE = "Host | 🎮"
ROL_POLICIA_NOMBRE = "Wsp | 👮"
ROL_DNI_NOMBRE = "Dni | 📋"

def tiene_rol(member, rol_buscado):
    if not member:
        return False
    rol_buscado_lower = rol_buscado.lower().strip()
    for rol in member.roles:
        if rol.name.lower().strip() == rol_buscado_lower:
            return True
    return False

def es_host(member):
    return tiene_rol(member, ROL_HOST_NOMBRE)

def es_policia(member):
    return tiene_rol(member, ROL_POLICIA_NOMBRE)

# ==================== FUNCIONES ====================
def cargar(archivo):
    if not os.path.exists(archivo):
        return {}
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar(archivo, data):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generar_numero_dni(user_id):
    return f"{int(user_id) % 100000000:08d}"

def validar_fecha(fecha):
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha):
        return False
    try:
        day, month, year = map(int, fecha.split('/'))
        return 1 <= month <= 12 and 1 <= day <= 31
    except:
        return False

# ==================== BOT ====================
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Crear archivos
ARCHIVOS_JSON = [DNI_FILE, ESCENAS_FILE, EVALUACIONES_FILE, VOTACIONES_FILE, AUTOS_FILE, MULTAS_FILE]
for archivo in ARCHIVOS_JSON:
    if not os.path.exists(archivo):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump({}, f)
        print(f"✅ Creado: {archivo}")

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Bot online como {bot.user.name}")
        print(f"✅ {len(synced)} comandos sincronizados")
        print(f"✅ Roles configurados:")
        print(f"   🔹 Host: {ROL_HOST_NOMBRE}")
        print(f"   🔹 Policía: {ROL_POLICIA_NOMBRE}")
        print(f"   🔹 DNI: {ROL_DNI_NOMBRE}")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")

# ==================== COMANDO DE PRUEBA ====================
@bot.tree.command(name="ping", description="🏓 Prueba del bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! El bot está funcionando.")

# ==================== DNI ====================
@bot.tree.command(name="crear_dni", description="🪪 Crea tu DNI")
@app_commands.describe(
    nombre="Nombre",
    apellidos="Apellidos",
    fecha_nacimiento="DD/MM/YYYY",
    edad="Edad"
)
async def crear_dni(interaction: discord.Interaction, nombre: str, apellidos: str, fecha_nacimiento: str, edad: int):
    if not validar_fecha(fecha_nacimiento):
        await interaction.response.send_message("❌ Usa DD/MM/YYYY", ephemeral=True)
        return
    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)
    if user_id in dnis:
        await interaction.response.send_message("⚠️ Ya tienes DNI", ephemeral=True)
        return
    dnis[user_id] = {
        "nombre": nombre,
        "apellidos": apellidos,
        "fecha_nacimiento": fecha_nacimiento,
        "edad": edad,
        "numero_dni": generar_numero_dni(user_id),
        "fecha_expedicion": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
    }
    guardar(DNI_FILE, dnis)
    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_DNI_NOMBRE)
        if rol:
            await interaction.user.add_roles(rol)
    except:
        pass
    embed = discord.Embed(title="✅ DNI CREADO", color=discord.Color.blue())
    embed.add_field(name="👤 Nombre", value=nombre, inline=True)
    embed.add_field(name="👥 Apellidos", value=apellidos, inline=True)
    embed.add_field(name="🎂 Edad", value=str(edad), inline=True)
    embed.add_field(name="📅 Nacimiento", value=fecha_nacimiento, inline=True)
    embed.add_field(name="🔢 DNI", value=dnis[user_id]["numero_dni"], inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="🔍 Ver DNI")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    dnis = cargar(DNI_FILE)
    datos = dnis.get(str(objetivo.id))
    if not datos:
        await interaction.response.send_message(f"❌ {objetivo.mention} sin DNI", ephemeral=True)
        return
    embed = discord.Embed(title=f"🪪 DNI DE {objetivo.name}", color=discord.Color.blue())
    embed.add_field(name="👤 Nombre", value=datos["nombre"], inline=True)
    embed.add_field(name="👥 Apellidos", value=datos["apellidos"], inline=True)
    embed.add_field(name="🎂 Edad", value=str(datos["edad"]), inline=True)
    embed.add_field(name="🔢 DNI", value=datos["numero_dni"], inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_dni", description="🗑️ Elimina tu DNI")
async def eliminar_dni(interaction: discord.Interaction):
    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)
    if user_id not in dnis:
        await interaction.response.send_message("❌ No tienes DNI", ephemeral=True)
        return
    del dnis[user_id]
    guardar(DNI_FILE, dnis)
    await interaction.response.send_message("✅ DNI eliminado", ephemeral=True)

# ==================== ESCENAS (SOLO HOSTS) ====================
@bot.tree.command(name="abrir_escena", description="🎬 Abrir sesión - SOLO HOSTS")
@app_commands.describe(
    vias="1 o 2",
    velocidad_maxima="km/h",
    adelantamientos="Si/No",
    link="Link del servidor"
)
async def abrir_escena(interaction: discord.Interaction, vias: str, velocidad_maxima: str, adelantamientos: str, link: str):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS", ephemeral=True)
        return
    if vias not in ["1", "2"]:
        await interaction.response.send_message("⚠️ Vías: 1 o 2", ephemeral=True)
        return
    if not velocidad_maxima.isdigit():
        await interaction.response.send_message("⚠️ Velocidad: número", ephemeral=True)
        return
    if adelantamientos.lower() not in ["si", "no"]:
        await interaction.response.send_message("⚠️ Si/No", ephemeral=True)
        return
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id in escenas:
        await interaction.response.send_message("⚠️ Ya hay sesión", ephemeral=True)
        return
    escenas[channel_id] = {
        "vias": vias,
        "velocidad_maxima": velocidad_maxima,
        "adelantamientos": adelantamientos.lower() == "si",
        "link_servidor": link,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    guardar(ESCENAS_FILE, escenas)
    embed = discord.Embed(
        title="🎬 SESIÓN ABIERTA",
        description=f"{NOMBRE_SERVIDOR}",
        color=discord.Color.gold()
    )
    embed.add_field(name="🛣️ Vías", value=f"{vias} vías", inline=True)
    embed.add_field(name="🚗 Velocidad", value=f"{velocidad_maxima} km/h", inline=True)
    embed.add_field(name="🏁 Adelantos", value="✅ Si" if adelantamientos.lower() == "si" else "❌ No", inline=True)
    embed.add_field(name="👑 Host", value=interaction.user.mention, inline=False)
    embed.add_field(name="🔗 Link", value=f"[Click]({link})", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cerrar_escena", description="🔒 Cerrar sesión - SOLO HOSTS")
async def cerrar_escena(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS", ephemeral=True)
        return
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id not in escenas:
        await interaction.response.send_message("❌ No hay sesión", ephemeral=True)
        return
    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)
    await interaction.response.send_message("🔒 Sesión cerrada")

# ==================== VOTACIONES (SOLO HOSTS) ====================
@bot.tree.command(name="votacion_sesion", description="🗳️ Votación - SOLO HOSTS")
@app_commands.describe(votos_requeridos="1-20")
async def votacion_sesion(interaction: discord.Interaction, votos_requeridos: int):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS", ephemeral=True)
        return
    if not 1 <= votos_requeridos <= 20:
        await interaction.response.send_message("⚠️ 1-20", ephemeral=True)
        return
    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id in votaciones:
        await interaction.response.send_message("⚠️ Ya hay votación", ephemeral=True)
        return
    votaciones[channel_id] = {
        "votos_requeridos": votos_requeridos,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "asistentes": [],
        "no_asistentes": [],
    }
    guardar(VOTACIONES_FILE, votaciones)
    await interaction.response.send_message(f"🗳️ Votación iniciada. Necesitan {votos_requeridos} votos.")

@bot.tree.command(name="cerrar_votacion", description="🔒 Cerrar votación - SOLO HOSTS")
async def cerrar_votacion(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS", ephemeral=True)
        return
    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id not in votaciones:
        await interaction.response.send_message("❌ No hay votación", ephemeral=True)
        return
    del votaciones[channel_id]
    guardar(VOTACIONES_FILE, votaciones)
    await interaction.response.send_message("🔒 Votación cerrada")

# ==================== AUTOS ====================
@bot.tree.command(name="registrar_auto", description="🚗 Registrar auto")
async def registrar_auto(interaction: discord.Interaction):
    class AutoModal(discord.ui.Modal, title="🚗 Registrar Auto"):
        usuario_roblox = discord.ui.TextInput(label="Usuario Roblox", max_length=50)
        placa = discord.ui.TextInput(label="Placa", max_length=20)
        modelo = discord.ui.TextInput(label="Modelo", max_length=50)
        color = discord.ui.TextInput(label="Color", max_length=30)
        async def on_submit(self, modal_interaction: discord.Interaction):
            autos = cargar(AUTOS_FILE)
            user_id = str(modal_interaction.user.id)
            autos.setdefault(user_id, []).append({
                "usuario_roblox": self.usuario_roblox.value,
                "placa": self.placa.value,
                "modelo": self.modelo.value,
                "color": self.color.value,
                "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
            })
            guardar(AUTOS_FILE, autos)
            await modal_interaction.response.send_message("✅ Auto registrado", ephemeral=True)
    await interaction.response.send_modal(AutoModal())

@bot.tree.command(name="ver_autos", description="🚗 Ver autos")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE)
    user_autos = autos.get(str(objetivo.id), [])
    if not user_autos:
        await interaction.response.send_message(f"❌ {objetivo.name} sin autos", ephemeral=True)
        return
    embed = discord.Embed(title=f"🚗 Autos de {objetivo.name}", color=discord.Color.blue())
    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"Auto #{i}",
            value=f"🎮 {auto['usuario_roblox']}\n📋 {auto['modelo']}\n🎨 {auto['color']}\n🅿️ {auto['placa']}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# ==================== MULTAS (SOLO POLICÍA) ====================
@bot.tree.command(name="registrar_multa", description="🚨 Registrar multa - SOLO POLICÍA")
async def registrar_multa(interaction: discord.Interaction):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICÍA", ephemeral=True)
        return
    class MultiModal(discord.ui.Modal, title="🚨 Registrar Multa"):
        infractor = discord.ui.TextInput(label="Infractor", max_length=100)
        infraccion = discord.ui.TextInput(label="Infracción", max_length=100)
        precio = discord.ui.TextInput(label="Monto ($)", max_length=10)
        async def on_submit(self, modal_interaction: discord.Interaction):
            if not self.precio.value.isdigit():
                await modal_interaction.response.send_message("⚠️ Monto: número", ephemeral=True)
                return
            multas = cargar(MULTAS_FILE)
            multas.setdefault("historial", []).append({
                "oficial": str(modal_interaction.user),
                "infractor": self.infractor.value,
                "infraccion": self.infraccion.value,
                "precio": int(self.precio.value),
                "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
            })
            guardar(MULTAS_FILE, multas)
            await modal_interaction.response.send_message("✅ Multa registrada", ephemeral=True)
    await interaction.response.send_modal(MultiModal())

@bot.tree.command(name="historial_multas", description="📋 Historial - SOLO POLICÍA")
async def historial_multas(interaction: discord.Interaction):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICÍA", ephemeral=True)
        return
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    if not historial:
        await interaction.response.send_message("📋 Sin multas", ephemeral=True)
        return
    embed = discord.Embed(title="🚨 HISTORIAL", color=discord.Color.red())
    for i, multa in enumerate(historial[-10:], 1):
        embed.add_field(
            name=f"#{i}",
            value=f"👮 {multa['oficial']}\n👤 {multa['infractor']}\n⚖️ {multa['infraccion']}\n💰 ${multa['precio']}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# ==================== EVALUACIÓN ====================
@bot.tree.command(name="evaluar_staff", description="⭐ Evaluar staff")
@app_commands.describe(staff="Staff a evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
        que_hizo = discord.ui.TextInput(label="¿Qué hizo?", max_length=100)
        calificacion = discord.ui.TextInput(label="1-10", max_length=2)
        amable = discord.ui.TextInput(label="¿Fue amable?", max_length=150)
        queja = discord.ui.TextInput(label="Sugerencias", required=False, max_length=300)
        async def on_submit(self, modal_interaction: discord.Interaction):
            try:
                nota = int(self.calificacion.value)
                if not 1 <= nota <= 10:
                    raise ValueError
            except:
                await modal_interaction.response.send_message("⚠️ 1-10", ephemeral=True)
                return
            evaluaciones = cargar(EVALUACIONES_FILE)
            clave = str(staff.id)
            evaluaciones.setdefault(clave, []).append({
                "staff": str(staff),
                "evaluador": str(modal_interaction.user),
                "que_hizo": self.que_hizo.value,
                "calificacion": nota,
                "amable": self.amable.value,
                "queja": self.queja.value or "Ninguna",
                "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
            })
            guardar(EVALUACIONES_FILE, evaluaciones)
            await modal_interaction.response.send_message("✅ Evaluación registrada", ephemeral=True)
    await interaction.response.send_modal(EvalModal())

# ==================== INICIAR ====================
print("🚀 Intentando conectar a Discord...")
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ ERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
