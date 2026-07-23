"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99 v3
Sistema completo: DNI, votaciones, escenas, autos, multas
Permisos por roles: Hosts y Policías
"""

import json
import os
import re
from datetime import datetime, timezone

import discord
from discord import app_commands, Attachment
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
ROL_POLICIA = "Wsp | 👮"
ROL_HOST = "Host | 🎮"
ROL_DNI = "Dni | 📋"

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
    return any(rol.name.lower() == ROL_HOST.lower() for rol in member.roles)

def es_policia(member: discord.Member) -> bool:
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

    # Asignar rol DNI automáticamente
    try:
        rol_dni = discord.utils.get(interaction.guild.roles, name=ROL_DNI)
        if rol_dni:
            await interaction.user.add_roles(rol_dni)
    except Exception as e:
        print(f"Error al asignar rol DNI: {e}")

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

@bot.tree.command(name="abrir_escena", description="🎬 Abre una sesión de rol - SOLO HOSTS")
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
    if not es_host(interaction.user):
        await interaction.response.send_message(
            "⛔ Solo los hosts pueden abrir escenas.",
            ephemeral=True,
        )
        return

    if vias not in ["1", "2"]:
        await interaction.response.send_message(
            "⚠️ Las vías deben ser solo: 1 o 2",
            ephemeral=True,
        )
        return

    if not velocidad_maxima.isdigit():
        await interaction.response.send_message(
            "⚠️ La velocidad máxima solo debe contener números.",
            ephemeral=True,
        )
        return

    if adelantamientos.lower() not in ["sí", "si", "no"]:
        await interaction.response.send_message(
            "⚠️ Adelantamientos: solo 'Sí' o 'No'",
            ephemeral=True,
        )
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)

    if channel_id in escenas:
        await interaction.response.send_message(
            "⚠️ Ya hay una sesión abierta. Ciérrala con `/cerrar_escena`.",
            ephemeral=True,
        )
        return

    adelantamiento_permitido = adelantamientos.lower() in ["sí", "si"]
    velocidad_adelanto = "Pendiente configurar" if adelantamiento_permitido else "No aplica"

    escena = {
        "vias": vias,
        "velocidad_maxima": velocidad_maxima,
        "adelantamientos": adelantamiento_permitido,
        "velocidad_adelanto": velocidad_adelanto,
        "link_servidor": link_servidor,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    escenas[channel_id] = escena
    guardar(ESCENAS_FILE, escenas)

    descripcion = (
        "¡Atención, ciudadanos! 🚨\n"
        "El equipo de hosts ya tiene los motores encendidos y estamos listos para "
        "arrancar con nuestra sesión de rol. 🏎️💨\n\n"
        "🔹 **Estado del servidor:** ABIERTO ✅\n\n"
        f"🔹 **Vías:** {vias}\n"
        f"🔹 **Velocidad máxima:** {velocidad_maxima} km/h\n"
        f"🔹 **Adelantamientos:** {'✅ Permitidos' if adelantamiento_permitido else '❌ No permitidos'}\n"
        f"🔹 **Host:** {interaction.user.mention}\n\n"
        f"🔗 **Link:** {link_servidor}\n\n"
        "¡Recuerden traer su DNI! 🪪"
    )

    embed = discord.Embed(
        title=f"📢 INICIO DE SESIÓN OFICIAL - {NOMBRE_SERVIDOR}",
        description=descripcion,
        color=discord.Color.gold(),
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cerrar_escena", description="🔒 Cierra la sesión actual - SOLO HOSTS")
async def cerrar_escena(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message(
            "⛔ Solo los hosts pueden cerrar escenas.",
            ephemeral=True,
        )
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    escena = escenas.get(channel_id)

    if not escena:
        await interaction.response.send_message(
            "🚫 No hay sesión abierta en este canal.", ephemeral=True
        )
        return

    inicio = datetime.fromisoformat(escena["inicio"])
    duracion = datetime.now(timezone.utc) - inicio
    horas, resto = divmod(int(duracion.total_seconds()), 3600)
    minutos = resto // 60

    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🔒 SESIÓN FINALIZADA",
        description=(
            f"La sesión en **{NOMBRE_SERVIDOR}** ha llegado a su fin. ¡Buen rol, ciudadanos! 🏁🎉\n\n"
            "⭐ Califiquen a su host con `/evaluar_staff` ⭐"
        ),
        color=discord.Color.red(),
    )
    embed.add_field(name="🧑‍✈️ Host", value=escena["host"], inline=True)
    embed.add_field(name="⏱️ Duración", value=f"{horas}h {minutos}m", inline=True)

    host_id = escena.get("host_id")
    contenido = f"📣 <@{host_id}> ¡tu sesión finalizó! 👇" if host_id else None
    await interaction.response.send_message(content=contenido, embed=embed)

# ---------- VOTACIONES ----------

def _embed_votacion(votacion: dict) -> discord.Embed:
    asistentes = votacion.get("asistentes", [])
    no_asistentes = votacion.get("no_asistentes", [])

    embed = discord.Embed(
        title="🗳️ ¿ABRIMOS SESIÓN? — VOTACIÓN",
        description=(
            f"🎯 **Meta:** {votacion['votos_requeridos']} votos\n"
            "👇 Toca un botón para decir si vas"
        ),
        color=discord.Color.orange(),
    )
    embed.add_field(
        name=f"✅ Irán ({len(asistentes)}/{votacion['votos_requeridos']})",
        value="\n".join(f"<@{u}>" for u in asistentes) or "Nadie todavía",
        inline=True,
    )
    embed.add_field(
        name=f"❌ No irán ({len(no_asistentes)})",
        value="\n".join(f"<@{u}>" for u in no_asistentes) or "Nadie todavía",
        inline=True,
    )
    embed.set_footer(text=f"Host: {votacion['host']}")
    return embed

class VotacionView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Asistir", style=discord.ButtonStyle.success, emoji="✅")
    async def asistir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._marcar(interaction, "asistentes")

    @discord.ui.button(label="No asistir", style=discord.ButtonStyle.danger, emoji="❌")
    async def no_asistir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._marcar(interaction, "no_asistentes")

    async def _marcar(self, interaction: discord.Interaction, lista: str):
        votaciones = cargar(VOTACIONES_FILE)
        votacion = votaciones.get(str(self.channel_id))

        if not votacion:
            await interaction.response.send_message("⛔ Votación expirada.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        votacion["asistentes"] = [u for u in votacion.get("asistentes", []) if u != user_id]
        votacion["no_asistentes"] = [u for u in votacion.get("no_asistentes", []) if u != user_id]
        votacion[lista].append(user_id)

        votaciones[str(self.channel_id)] = votacion
        guardar(VOTACIONES_FILE, votaciones)

        await interaction.response.edit_message(embed=_embed_votacion(votacion), view=self)

        if lista == "asistentes" and len(votacion["asistentes"]) == votacion["votos_requeridos"]:
            await interaction.channel.send(
                f"🎉🏁 <@{votacion['host_id']}> ¡Se alcanzó! Ya puedes abrir con `/abrir_escena` 🚦"
            )

@bot.tree.command(name="votacion_sesion", description="🗳️ Abre una votación (máx 20) - SOLO HOSTS")
@app_commands.describe(votos_requeridos="Votos necesarios (0-20)")
async def votacion_sesion(interaction: discord.Interaction, votos_requeridos: int):
    if not es_host(interaction.user):
        await interaction.response.send_message(
            "⛔ Solo los hosts pueden abrir votaciones.",
            ephemeral=True,
        )
        return

    if not (0 < votos_requeridos <= 20):
        await interaction.response.send_message(
            "⚠️ Los votos deben estar entre 1 y 20.",
            ephemeral=True,
        )
        return

    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)

    if channel_id in votaciones:
        await interaction.response.send_message(
            "⚠️ Ya hay votación activa.",
            ephemeral=True,
        )
        return

    votacion = {
        "votos_requeridos": votos_requeridos,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "asistentes": [],
        "no_asistentes": [],
    }
    votaciones[channel_id] = votacion
    guardar(VOTACIONES_FILE, votaciones)

    await interaction.response.send_message(
        embed=_embed_votacion(votacion), view=VotacionView(interaction.channel_id)
    )

@bot.tree.command(name="cerrar_votacion", description="❌ Cierra la votación - SOLO HOSTS")
async def cerrar_votacion(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message(
            "⛔ Solo los hosts pueden cerrar votaciones.",
            ephemeral=True,
        )
        return

    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)

    if channel_id not in votaciones:
        await interaction.response.send_message("🚫 No hay votación activa.", ephemeral=True)
        return

    del votaciones[channel_id]
    guardar(VOTACIONES_FILE, votaciones)
    await interaction.response.send_message("🔒 Votación cerrada.")

# ---------- REGISTRO DE AUTOS ----------

class RegistroAutoModal(discord.ui.Modal, title="🚗 Registrar Vehículo"):
    usuario_roblox = discord.ui.TextInput(label="Usuario Roblox", max_length=50)
    placa = discord.ui.TextInput(label="Placa del vehículo", max_length=20)
    modelo = discord.ui.TextInput(label="Modelo/Marca", max_length=50)
    color = discord.ui.TextInput(label="Color", max_length=30)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "📸 Perfecto. Ahora usa `/subir_foto_auto` para adjuntar la foto de tu vehículo.",
            ephemeral=True,
        )
        # Guardar datos temporales
        temporal = cargar("temporal_autos.json") if os.path.exists("temporal_autos.json") else {}
        user_id = str(interaction.user.id)
        temporal[user_id] = {
            "usuario_roblox": self.usuario_roblox.value,
            "placa": self.placa.value,
            "modelo": self.modelo.value,
            "color": self.color.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        guardar("temporal_autos.json", temporal)

@bot.tree.command(name="registrar_auto", description="🚗 Registra tu vehículo - Paso 1/2")
async def registrar_auto(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistroAutoModal())

@bot.tree.command(name="subir_foto_auto", description="📸 Sube la foto de tu vehículo registrado")
@app_commands.describe(foto="Foto del vehículo (imagen o archivo)")
async def subir_foto_auto(interaction: discord.Interaction, foto: Attachment):
    user_id = str(interaction.user.id)
    temporal = cargar("temporal_autos.json") if os.path.exists("temporal_autos.json") else {}

    if user_id not in temporal:
        await interaction.response.send_message(
            "⚠️ Primero usa `/registrar_auto` para crear el registro.",
            ephemeral=True,
        )
        return

    # Validar que sea imagen
    if not foto.content_type or "image" not in foto.content_type:
        await interaction.response.send_message(
            "⚠️ Solo se aceptan imágenes.",
            ephemeral=True,
        )
        return

    # Guardar datos del auto
    autos = cargar(AUTOS_FILE)
    autos.setdefault(user_id, []).append({
        "usuario_discord": str(interaction.user),
        "usuario_roblox": temporal[user_id]["usuario_roblox"],
        "placa": temporal[user_id]["placa"],
        "modelo": temporal[user_id]["modelo"],
        "color": temporal[user_id]["color"],
        "foto_url": foto.url,
        "fecha_registro": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
    })
    guardar(AUTOS_FILE, autos)

    # Eliminar dato temporal
    del temporal[user_id]
    guardar("temporal_autos.json", temporal)

    embed = discord.Embed(
        title="🚗 VEHÍCULO REGISTRADO",
        description="¡Tu auto fue registrado exitosamente! 🎉",
        color=discord.Color.green(),
    )
    embed.add_field(name="👤 Discord", value=interaction.user.mention, inline=False)
    embed.add_field(name="🎮 Roblox", value=temporal[user_id]["usuario_roblox"] if user_id in temporal else "N/A", inline=False)
    embed.add_field(name="📋 Modelo", value=temporal[user_id]["modelo"] if user_id in temporal else autos[user_id][-1]["modelo"], inline=True)
    embed.add_field(name="🎨 Color", value=temporal[user_id]["color"] if user_id in temporal else autos[user_id][-1]["color"], inline=True)
    embed.add_field(name="🅿️ Placa", value=autos[user_id][-1]["placa"], inline=True)
    embed.set_image(url=foto.url)

    await interaction.response.send_message(embed=embed)

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
                f"🅿️ **Placa:** {auto['placa']}"
            ),
            inline=False,
        )

    await interaction.response.send_message(embed=
