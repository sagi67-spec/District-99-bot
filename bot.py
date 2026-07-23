"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
Sistema: DNI, votaciones, escenas, autos, multas
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

def es_host(member):
    return any(rol.name.lower() == ROL_HOST.lower() for rol in member.roles)

def es_policia(member):
    return any(rol.name.lower() == ROL_POLICIA.lower() for rol in member.roles)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========== CREAR ARCHIVOS JSON SI NO EXISTEN ==========
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
        print(f"✅ Bot online. {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")

# ==================== DNI ====================

@bot.tree.command(name="crear_dni", description="Crea el DNI de tu personaje")
@app_commands.describe(
    nombre="Nombre",
    apellidos="Apellidos",
    fecha_nacimiento="Fecha (DD/MM/YYYY)",
    edad="Edad",
)
async def crear_dni(interaction: discord.Interaction, nombre: str, apellidos: str, fecha_nacimiento: str, edad: int):
    if not validar_fecha(fecha_nacimiento):
        await interaction.response.send_message("⚠️ Usa: DD/MM/YYYY", ephemeral=True)
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

    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_DNI)
        if rol:
            await interaction.user.add_roles(rol)
    except:
        pass

    embed = discord.Embed(title="📋 DNI CREADO", color=discord.Color.blue())
    embed.add_field(name="👤 Nombre", value=nombre, inline=True)
    embed.add_field(name="👥 Apellidos", value=apellidos, inline=True)
    embed.add_field(name="🎂 Edad", value=str(edad), inline=True)
    embed.add_field(name="📅 Nacimiento", value=fecha_nacimiento, inline=True)
    embed.add_field(name="🔢 DNI", value=dnis[user_id]["numero_dni"], inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="Ve un DNI")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    dnis = cargar(DNI_FILE)
    datos = dnis.get(str(objetivo.id))
    if not datos:
        await interaction.response.send_message(f"🚫 {objetivo.mention} sin DNI", ephemeral=True)
        return
    embed = discord.Embed(title="📋 DNI", color=discord.Color.blue())
    embed.add_field(name="👤 Nombre", value=datos["nombre"], inline=True)
    embed.add_field(name="👥 Apellidos", value=datos["apellidos"], inline=True)
    embed.add_field(name="🎂 Edad", value=str(datos["edad"]), inline=True)
    embed.add_field(name="📅 Nacimiento", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="🔢 DNI", value=datos["numero_dni"], inline=True)
    embed.set_thumbnail(url=objetivo.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_dni", description="Elimina tu DNI")
async def eliminar_dni(interaction: discord.Interaction):
    dnis = cargar(DNI_FILE)
    if str(interaction.user.id) not in dnis:
        await interaction.response.send_message("❌ Sin DNI", ephemeral=True)
        return
    del dnis[str(interaction.user.id)]
    guardar(DNI_FILE, dnis)
    await interaction.response.send_message("✅ DNI eliminado")

# ==================== ESCENAS ====================

@bot.tree.command(name="abrir_escena", description="Abre sesion - SOLO HOSTS")
@app_commands.describe(vias="1 o 2", velocidad_maxima="Numeros", adelantamientos="Si/No", link="Link")
async def abrir_escena(interaction: discord.Interaction, vias: str, velocidad_maxima: str, adelantamientos: str, link: str):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo hosts", ephemeral=True)
        return
    if vias not in ["1", "2"]:
        await interaction.response.send_message("⚠️ Vias: 1 o 2", ephemeral=True)
        return
    if not velocidad_maxima.isdigit():
        await interaction.response.send_message("⚠️ Velocidad: numeros", ephemeral=True)
        return
    if adelantamientos.lower() not in ["si", "no"]:
        await interaction.response.send_message("⚠️ Adelanto: Si/No", ephemeral=True)
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id in escenas:
        await interaction.response.send_message("⚠️ Ya hay sesion abierta", ephemeral=True)
        return

    adelanto_permitido = adelantamientos.lower() == "si"
    escenas[channel_id] = {
        "vias": vias,
        "velocidad_maxima": velocidad_maxima,
        "adelantamientos": adelanto_permitido,
        "link_servidor": link,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    guardar(ESCENAS_FILE, escenas)

    desc = (
        f"🎬 **{NOMBRE_SERVIDOR}** - SESION ABIERTA\n\n"
        f"🔹 Vias: {vias}\n"
        f"🔹 Velocidad max: {velocidad_maxima} km/h\n"
        f"🔹 Adelantos: {'✅' if adelanto_permitido else '❌'}\n"
        f"🔹 Host: {interaction.user.mention}\n"
        f"🔗 Link: {link}\n\n"
        "¡Traigan su DNI! 🪪"
    )
    embed = discord.Embed(title="📢 INICIO DE SESION", description=desc, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cerrar_escena", description="Cierra sesion - SOLO HOSTS")
async def cerrar_escena(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo hosts", ephemeral=True)
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id not in escenas:
        await interaction.response.send_message("🚫 No hay sesion", ephemeral=True)
        return

    escena = escenas[channel_id]
    inicio = datetime.fromisoformat(escena["inicio"])
    duracion = datetime.now(timezone.utc) - inicio
    horas, resto = divmod(int(duracion.total_seconds()), 3600)
    minutos = resto // 60

    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🔒 SESION FINALIZADA",
        description=f"¡Buen rol! Duracion: {horas}h {minutos}m\n⭐ Califiquen con `/evaluar_staff`",
        color=discord.Color.red()
    )
    host_id = escena.get("host_id")
    await interaction.response.send_message(
        content=f"<@{host_id}>" if host_id else None,
        embed=embed
    )

# ==================== VOTACIONES ====================

class VotoView(discord.ui.View):
    def __init__(self, channel_id: str):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Asistir", emoji="✅", style=discord.ButtonStyle.success)
    async def asistir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._votar(interaction, "asistentes")

    @discord.ui.button(label="No asistir", emoji="❌", style=discord.ButtonStyle.danger)
    async def no_asistir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._votar(interaction, "no_asistentes")

    async def _votar(self, interaction: discord.Interaction, voto_tipo: str):
        votaciones = cargar(VOTACIONES_FILE)
        votacion = votaciones.get(str(self.channel_id))
        if not votacion:
            await interaction.response.send_message("⛔ Votacion expirada", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        votacion["asistentes"] = [u for u in votacion.get("asistentes", []) if u != user_id]
        votacion["no_asistentes"] = [u for u in votacion.get("no_asistentes", []) if u != user_id]
        votacion[voto_tipo].append(user_id)

        votaciones[str(self.channel_id)] = votacion
        guardar(VOTACIONES_FILE, votaciones)

        asist = votacion.get("asistentes", [])
        no_asist = votacion.get("no_asistentes", [])
        embed = discord.Embed(
            title="🗳️ VOTACION",
            description=f"✅ Iran: {len(asist)}/{votacion['votos_requeridos']}\n❌ No iran: {len(no_asist)}",
            color=discord.Color.orange()
        )
        embed.add_field(name="✅", value="\n".join(f"<@{u}>" for u in asist) or "Nadie", inline=False)
        embed.add_field(name="❌", value="\n".join(f"<@{u}>" for u in no_asist) or "Nadie", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

        if len(asist) == votacion["votos_requeridos"]:
            await interaction.channel.send(f"🎉 <@{votacion['host_id']}> ¡Meta alcanzada! Abre con `/abrir_escena`")

@bot.tree.command(name="votacion_sesion", description="Votacion (0-20) - SOLO HOSTS")
@app_commands.describe(votos_requeridos="1-20")
async def votacion_sesion(interaction: discord.Interaction, votos_requeridos: int):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo hosts", ephemeral=True)
        return
    if not (0 < votos_requeridos <= 20):
        await interaction.response.send_message("⚠️ 1-20 votos", ephemeral=True)
        return

    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id in votaciones:
        await interaction.response.send_message("⚠️ Ya hay votacion", ephemeral=True)
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

    embed = discord.Embed(
        title="🗳️ ¿ABRIMOS SESION?",
        description=f"Meta: {votos_requeridos} votos",
        color=discord.Color.orange()
    )
    embed.add_field(name="✅ Iran", value="Nadie", inline=False)
    embed.add_field(name="❌ No iran", value="Nadie", inline=False)
    await interaction.response.send_message(embed=embed, view=VotoView(interaction.channel_id))

@bot.tree.command(name="cerrar_votacion", description="Cierra votacion - SOLO HOSTS")
async def cerrar_votacion(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo hosts", ephemeral=True)
        return

    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id not in votaciones:
        await interaction.response.send_message("🚫 Sin votacion", ephemeral=True)
        return

    del votaciones[channel_id]
    guardar(VOTACIONES_FILE, votaciones)
    await interaction.response.send_message("🔒 Votacion cerrada")

# ==================== AUTOS ====================

class AutoModal(discord.ui.Modal, title="🚗 Registrar Vehiculo"):
    usuario_roblox = discord.ui.TextInput(label="Usuario Roblox", max_length=50)
    placa = discord.ui.TextInput(label="Placa", max_length=20)
    modelo = discord.ui.TextInput(label="Modelo/Marca", max_length=50)
    color = discord.ui.TextInput(label="Color", max_length=30)

    async def on_submit(self, interaction: discord.Interaction):
        autos = cargar(AUTOS_FILE)
        user_id = str(interaction.user.id)
        autos.setdefault(user_id, []).append({
            "usuario_discord": str(interaction.user),
            "usuario_roblox": self.usuario_roblox.value,
            "placa": self.placa.value,
            "modelo": self.modelo.value,
            "color": self.color.value,
            "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        })
        guardar(AUTOS_FILE, autos)

        embed = discord.Embed(title="🚗 AUTO REGISTRADO", color=discord.Color.green())
        embed.add_field(name="🎮 Roblox", value=self.usuario_roblox.value, inline=False)
        embed.add_field(name="📋 Modelo", value=self.modelo.value, inline=True)
        embed.add_field(name="🎨 Color", value=self.color.value, inline=True)
        embed.add_field(name="🅿️ Placa", value=self.placa.value, inline=True)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="registrar_auto", description="Registra tu vehiculo")
async def registrar_auto(interaction: discord.Interaction):
    await interaction.response.send_modal(AutoModal())

@bot.tree.command(name="ver_autos", description="Ve autos registrados")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE)
    user_autos = autos.get(str(objetivo.id), [])
    if not user_autos:
        await interaction.response.send_message(f"🚫 {objetivo.mention} sin autos", ephemeral=True)
        return

    embed = discord.Embed(title=f"🚗 AUTOS DE {objetivo.name.upper()}", color=discord.Color.blue())
    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"Auto #{i}",
            value=f"🎮 {auto['usuario_roblox']}\n📋 {auto['modelo']}\n🎨 {auto['color']}\n🅿️ {auto['placa']}",
            inline=False,
        )
    await interaction.response.send_message(embed=embed)

# ==================== MULTAS ====================

class MultiModal(discord.ui.Modal, title="🚨 Registrar Multa"):
    infractor = discord.ui.TextInput(label="Infractor", max_length=100)
    infraccion = discord.ui.TextInput(label="Infraccion", max_length=100)
    precio = discord.ui.TextInput(label="Monto ($)", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        if not es_policia(interaction.user):
            await interaction.response.send_message("⛔ Solo policia", ephemeral=True)
            return
        if not self.precio.value.isdigit():
            await interaction.response.send_message("⚠️ Monto: numeros", ephemeral=True)
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

        embed = discord.Embed(title="🚨 MULTA REGISTRADA", color=discord.Color.red())
        embed.add_field(name="👮 Oficial", value=interaction.user.mention, inline=False)
        embed.add_field(name="👤 Infractor", value=self.infractor.value, inline=False)
        embed.add_field(name="⚖️ Infraccion", value=self.infraccion.value, inline=False)
        embed.add_field(name="💰 Monto", value=f"${self.precio.value}", inline=True)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="registrar_multa", description="Registra multa - SOLO POLICIA")
async def registrar_multa(interaction: discord.Interaction):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo policia", ephemeral=True)
        return
    await interaction.response.send_modal(MultiModal())

@bot.tree.command(name="historial_multas", description="Historial de multas")
async def historial_multas(interaction: discord.Interaction):
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    if not historial:
        await interaction.response.send_message("📋 Sin multas", ephemeral=True)
        return

    embed = discord.Embed(title="🚨 HISTORIAL", color=discord.Color.red())
    for i, multa in enumerate(historial[-10:], 1):
        embed.add_field(
            name=f"#{i}",
            value=f"👮 {multa['oficial']}\n👤 {multa['infractor']}\n⚖️ {multa['infraccion']}\n💰 ${multa['precio']}\n📅 {multa['fecha']}",
            inline=False,
        )
    await interaction.response.send_message(embed=embed)

# ==================== EVALUACION ====================

class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
    que_hizo = discord.ui.TextInput(label="¿Que hizo?", max_length=100)
    calificacion = discord.ui.TextInput(label="1-10", max_length=2)
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
        except:
            await interaction.response.send_message("⚠️ 1-10", ephemeral=True)
            return

        evaluaciones = cargar(EVALUACIONES_FILE)
        clave = str(self.staff.id)
        evaluaciones.setdefault(clave, []).append({
            "staff": str(self.staff),
            "evaluador": str(interaction.user),
            "que_hizo": self.que_hizo.value,
            "calificacion": nota,
            "amable": self.amable.value,
            "queja": self.queja.value or "Ninguna",
            "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
        })
        guardar(EVALUACIONES_FILE, evaluaciones)

        estrellas = "⭐" * round(nota / 2) if nota >= 2 else "✩"
        embed = discord.Embed(title="📝 EVALUACION", color=discord.Color.purple())
        embed.add_field(name="⭐ Atencion", value=f"{estrellas} ({nota}/10)", inline=False)
        embed.add_field(name="🤝 Amable", value=self.amable.value, inline=False)
        embed.add_field(name="💬 Sugerencias", value=self.queja.value or "Ninguna", inline=False)
        await interaction.response.send_message(content=self.staff.mention, embed=embed)

@bot.tree.command(name="evaluar_staff", description="Evalua al staff")
@app_commands.describe(staff="Staff a evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvalModal(staff))

# ==================== INICIAR BOT ====================
if __name__ == "__main__":
    bot.run(TO
