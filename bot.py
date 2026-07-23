"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99 v2
Sistema completo con: DNI, votaciones, escenas, autos, y multas
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

# Archivos de datos
DNI_FILE = "dnis.json"
ESCENAS_FILE = "escenas.json"
EVALUACIONES_FILE = "evaluaciones.json"
VOTACIONES_FILE = "votaciones.json"
AUTOS_FILE = "autos.json"
MULTAS_FILE = "multas.json"

NOMBRE_SERVIDOR = "DISTRICT 99"
ROL_POLICIA = "Wsp | 👮"  # Rol de policías
ROL_HOST = "Host | 🎮"  # Rol de hosts

# ---------- Utilidades ----------

def cargar(archivo: str) -> dict:
    if not os.path.exists(archivo):
        return {}
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar(archivo: str, data: dict) -> None:
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generar_numero_dni(user_id: str) -> str:
    return f"{int(user_id) % 100000000:08d}"

def validar_fecha(fecha: str) -> bool:
    """Valida formato DD/MM/YYYY con solo números"""
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha):
        return False
    try:
        day, month, year = map(int, fecha.split('/'))
        if month < 1 or month > 12 or day < 1 or day > 31:
            return False
        return True
    except:
        return False

def es_host(member: discord.Member) -> bool:
    """Verifica si el usuario tiene rol de host"""
    return any(rol.name.lower() == ROL_HOST.lower() for rol in member.roles)

def es_policia(member: discord.Member) -> bool:
    """Verifica si el usuario tiene rol de policía"""
    return any(rol.name.lower() == ROL_POLICIA.lower() for rol in member.roles)

# ---------- Configuración del bot ----------

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sesión iniciada como {bot.user}. {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

# ---------- COMANDOS DE DNI ----------

@bot.tree.command(name="crear_dni", description="🪪 Crea el DNI de tu personaje")
@app_commands.describe(
    nombre="Nombre del personaje",
    apellidos="Apellidos del personaje",
    fecha_nacimiento="Fecha (formato: DD/MM/YYYY)",
    edad="Edad del personaje",
)
async def crear_dni(
    interaction: discord.Interaction,
    nombre: str,
    apellidos: str,
    fecha_nacimiento: str,
    edad: int,
):
    # Validar fecha
    if not validar_fecha(fecha_nacimiento):
        await interaction.response.send_message(
            "⚠️ Formato de fecha inválido. Usa: DD/MM/YYYY (solo números)",
            ephemeral=True,
        )
        return

    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)

    dnis[user_id] = {
        "nombre": nombre,
        "apellidos": apellidos,
        "fecha_nacimiento": fecha_nacimiento,
        "edad": edad,
        "numero_dni": generar_numero_dni(user_id),
        "fecha_expedicion": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
    }
    guardar(DNI_FILE, dnis)

    embed = discord.Embed(
        title="📋 DOCUMENTO NACIONAL DE IDENTIDAD",
        description="¡DNI creado exitosamente! 🎉",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="👤 Nombre", value=nombre, inline=True)
    embed.add_field(name="👥 Apellidos", value=apellidos, inline=True)
    embed.add_field(name="🎂 Edad", value=str(edad), inline=True)
    embed.add_field(name="📅 F. Nacimiento", value=fecha_nacimiento, inline=True)
    embed.add_field(name="🔢 Nº DNI", value=dnis[user_id]["numero_dni"], inline=True)
    embed.add_field(name="✅ Expedido", value=dnis[user_id]["fecha_expedicion"], inline=True)
    embed.set_footer(text=f"Jugador: {interaction.user}")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="🔍 Muestra un DNI")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    dnis = cargar(DNI_FILE)
    datos = dnis.get(str(objetivo.id))

    if not datos:
        await interaction.response.send_message(
            f"🕵️ {objetivo.mention} no tiene DNI creado aún.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title="📋 DOCUMENTO NACIONAL DE IDENTIDAD",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(url=objetivo.display_avatar.url)
    embed.add_field(name="👤 Nombre", value=datos["nombre"], inline=True)
    embed.add_field(name="👥 Apellidos", value=datos["apellidos"], inline=True)
    embed.add_field(name="🎂 Edad", value=str(datos["edad"]), inline=True)
    embed.add_field(name="📅 F. Nacimiento", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="🔢 Nº DNI", value=datos["numero_dni"], inline=True)
    embed.add_field(name="✅ Expedido", value=datos["fecha_expedicion"], inline=True)
    embed.set_footer(text=f"Jugador: {objetivo}")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_dni", description="🗑️ Elimina tu DNI")
async def eliminar_dni(interaction: discord.Interaction):
    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)

    if user_id not in dnis:
        await interaction.response.send_message("❌ No tienes DNI creado.", ephemeral=True)
        return

    del dnis[user_id]
    guardar(DNI_FILE, dnis)
    await interaction.response.send_message("✅ Tu DNI fue eliminado.")

# ---------- COMANDOS DE SESIÓN/ESCENA ----------

@bot.tree.command(name="abrir_escena", description="🎬 Abre una sesión de rol")
@app_commands.describe(
    vias="Vías disponibles (solo: 1 o 2)",
    velocidad_maxima="Velocidad máxima (números)",
    adelantamientos="¿Adelantamientos permitidos? (Sí/No)",
    link_servidor="Link del servidor/juego",
)
async def abrir_escena(
    interaction: discord.Interaction,
    vias: str,
    velocidad_maxima: str,
    adelantamientos: str,
    link_servidor: str,
):
    # Verificar si es host
    if not es_host(interaction.user):
        await interaction.response.send_message(
            "⛔ Solo los hosts pueden abrir escenas.",
            ephemeral=True,
        )
        return

    # Validar vías (solo 1 o 2)
    if vias not in ["1", "2"]:
        await interaction.response.send_message(
            "⚠️ Las vías deben ser solo: 1 o 2",
            ephemeral=True,
        )
        return

    # Validar velocidad (solo números)
    if not velocidad_maxima.isdigit():
        await interaction.response.send_message(
            "⚠️ La velocidad máxima solo debe contener números.",
            ephemeral=True,
        )
        return

< truncated lines 216-425 >
    foto_url = discord.ui.TextInput(label="Link de foto (URL)", max_length=500, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        autos = cargar(AUTOS_FILE)
        user_id = str(interaction.user.id)

        autos.setdefault(user_id, []).append({
            "usuario_discord": str(interaction.user),
            "usuario_roblox": self.usuario_roblox.value,
            "placa": self.placa.value,
            "modelo": self.modelo.value,
            "color": self.color.value,
            "foto_url": self.foto_url.value or "No proporcionada",
            "fecha_registro": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        })
        guardar(AUTOS_FILE, autos)

        embed = discord.Embed(
            title="🚗 VEHÍCULO REGISTRADO",
            description="¡Tu auto fue registrado exitosamente! 🎉",
            color=discord.Color.green(),
        )
        embed.add_field(name="👤 Discord", value=interaction.user.mention, inline=False)
        embed.add_field(name="🎮 Roblox", value=self.usuario_roblox.value, inline=False)
        embed.add_field(name="📋 Modelo", value=self.modelo.value, inline=True)
        embed.add_field(name="🎨 Color", value=self.color.value, inline=True)
        embed.add_field(name="🅿️ Placa", value=self.placa.value, inline=True)
        if self.foto_url.value:
            embed.add_field(name="📸 Foto", value=self.foto_url.value, inline=False)

        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="registrar_auto", description="🚗 Registra tu vehículo")
async def registrar_auto(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistroAutoModal())

@bot.tree.command(name="ver_autos", description="🚗 Ve los autos registrados")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE)
    user_autos = autos.get(str(objetivo.id), [])

    if not user_autos:
        await interaction.response.send_message(
            f"🚫 {objetivo.mention} no tiene autos registrados.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title=f"🚗 VEHÍCULOS DE {objetivo.name.upper()}",
        color=discord.Color.blue(),
    )

    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"Auto #{i}",
            value=(
                f"🎮 **Roblox:** {auto['usuario_roblox']}\n"
                f"📋 **Modelo:** {auto['modelo']}\n"
                f"🎨 **Color:** {auto['color']}\n"
                f"🅿️ **Placa:** {auto['placa']}\n"
                f"📸 **Foto:** {auto['foto_url']}"
            ),
            inline=False,
        )

    await interaction.response.send_message(embed=embed)

# ---------- SISTEMA DE MULTAS ----------

class RegistroMultaModal(discord.ui.Modal, title="🚨 Registrar Multa"):
    infractor = discord.ui.TextInput(label="Nombre del infractor", max_length=100)
    infraccion = discord.ui.TextInput(label="Tipo de infracción", max_length=100)
    precio = discord.ui.TextInput(label="Precio de la multa ($)", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        if not es_policia(interaction.user):
            await interaction.response.send_message(
                "⛔ Solo la policía puede registrar multas.",
                ephemeral=True,
            )
            return

        if not self.precio.value.isdigit():
            await interaction.response.send_message(
                "⚠️ El precio solo debe contener números.",
                ephemeral=True,
            )
            return

        multas = cargar(MULTAS_FILE)
        multas.setdefault("historial", []).append({
            "oficial": str(interaction.user),
            "infractor": self.infractor.value,
            "infraccion": self.infraccion.value,
            "precio": int(self.precio.value),
            "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
        })
        guardar(MULTAS_FILE, multas)

        embed = discord.Embed(
            title="🚨 MULTA REGISTRADA",
            description="La multa ha sido registrada en el sistema. 📝",
            color=discord.Color.red(),
        )
        embed.add_field(name="👮 Oficial", value=interaction.user.mention, inline=False)
        embed.add_field(name="👤 Infractor", value=self.infractor.value, inline=False)
        embed.add_field(name="⚖️ Infracción", value=self.infraccion.value, inline=False)
        embed.add_field(name="💰 Monto", value=f"${self.precio.value}", inline=True)
        embed.add_field(name="📅 Fecha", value=embed.fields[3].value if len(embed.fields) > 3 else "Hoy", inline=True)

        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="registrar_multa", description="🚨 Registra una multa (Solo policía)")
async def registrar_multa(interaction: discord.Interaction):
    if not es_policia(interaction.user):
        await interaction.response.send_message(
            "⛔ Solo los policías pueden usar este comando.",
            ephemeral=True,
        )
        return

    await interaction.response.send_modal(RegistroMultaModal())

@bot.tree.command(name="historial_multas", description="📋 Ve el historial de multas")
async def historial_multas(interaction: discord.Interaction):
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])

    if not historial:
        await interaction.response.send_message(
            "📋 No hay multas registradas aún.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title="🚨 HISTORIAL DE MULTAS",
        color=discord.Color.red(),
    )

    for i, multa in enumerate(historial[-10:], 1):  # Últimas 10 multas
        embed.add_field(
            name=f"#{i}",
            value=(
                f"👮 **Oficial:** {multa['oficial']}\n"
                f"👤 **Infractor:** {multa['infractor']}\n"
                f"⚖️ **Infracción:** {multa['infraccion']}\n"
                f"💰 **Monto:** ${multa['precio']}\n"
                f"📅 **Fecha:** {multa['fecha']}"
            ),
            inline=False,
        )

    await interaction.response.send_message(embed=embed)

# ---------- EVALUACIÓN DE STAFF ----------

class EvaluacionModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
    que_hizo = discord.ui.TextInput(label="¿Qué hizo?", max_length=100)
    calificacion = discord.ui.TextInput(label="Atención (1-10)", max_length=2)
    amable = discord.ui.TextInput(label="¿Fue amable?", max_length=150)
    queja = discord.ui.TextInput(label="Sugerencias", required=False, max_length=300)

    def __init__(self, staff: discord.Member):
        super().__init__()
        self.staff = staff

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nota = int(self.calificacion.value.strip())
            if not 1 <= nota <= 10:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "⚠️ La calificación debe ser un número del 1 al 10.",
                ephemeral=True,
            )
            return

        evaluaciones = cargar(EVALUACIONES_FILE)
        clave_staff = str(self.staff.id)
        evaluaciones.setdefault(clave_staff, []).append({
            "nombre_staff": str(self.staff),
            "evaluador": str(interaction.user),
            "que_hizo": self.que_hizo.value,
            "calificacion": nota,
            "amable_resolvio": self.amable.value,
            "queja_sugerencia": self.queja.value or "Ninguna",
            "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
        })
        guardar(EVALUACIONES_FILE, evaluaciones)

        estrellas = "⭐" * round(nota / 2) if nota >= 2 else "✩"
        embed = discord.Embed(
            title="📝 NUEVA EVALUACIÓN",
            description=f"¡Gracias por tu opinión, {interaction.user.mention}! 🙌",
            color=discord.Color.purple(),
        )
        embed.add_field(name="🧑‍✈️ Staff", value=self.staff.mention, inline=False)
        embed.add_field(name="📋 ¿Qué hizo?", value=self.que_hizo.value, inline=False)
        embed.add_field(name="⭐ Atención", value=f"{estrellas} ({nota}/10)", inline=True)
        embed.add_field(name="🤝 ¿Amable?", value=self.amable.value, inline=True)
        embed.add_field(name="💬 Sugerencias", value=self.queja.value or "Ninguna", inline=False)

        await interaction.response.send_message(content=self.staff.mention, embed=embed)

@bot.tree.command(name="evaluar_staff", description="⭐ Evalúa a un staff")
@app_commands.describe(staff="Selecciona el staff")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvaluacionModal(staff))

bot.run(TOKEN)
