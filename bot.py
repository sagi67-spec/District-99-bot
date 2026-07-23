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

# ==================== ROLES (NOMBRES EXACTOS DE DISCORD) ====================
ROL_HOST_NOMBRE = "Host│🎮"
ROL_POLICIA_NOMBRE = "Wsp│👮"
ROL_DNI_NOMBRE = "Dni│🪪"

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
            await interaction.response.send_message("✅ DNI creado y rol asignado", ephemeral=True)
        else:
            await interaction.response.send_message("✅ DNI creado", ephemeral=True)
    except:
        await interaction.response.send_message("✅ DNI creado", ephemeral=True)

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
    embed.add_field(name="📅 Nacimiento", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="🔢 DNI", value=datos["numero_dni"], inline=True)
    embed.set_thumbnail(url=objetivo.display_avatar.url)
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
    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_DNI_NOMBRE)
        if rol and rol in interaction.user.roles:
            await interaction.user.remove_roles(rol)
    except:
        pass
    await interaction.response.send_message("✅ DNI eliminado", ephemeral=True)

# ==================== ESCENAS ====================
@bot.tree.command(name="abrir_escena", description="🎬 Abrir sesion - SOLO HOSTS")
@app_commands.describe(
    vias="1 o 2",
    velocidad_maxima="km/h",
    adelantamientos="Si/No",
    link="Link del servidor"
)
async def abrir_escena(interaction: discord.Interaction, vias: str, velocidad_maxima: str, adelantamientos: str, link: str):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS pueden usar este comando", ephemeral=True)
        return
    if vias not in ["1", "2"]:
        await interaction.response.send_message("⚠️ Vias: 1 o 2", ephemeral=True)
        return
    if not velocidad_maxima.isdigit():
        await interaction.response.send_message("⚠️ Velocidad: numero", ephemeral=True)
        return
    if adelantamientos.lower() not in ["si", "no"]:
        await interaction.response.send_message("⚠️ Si/No", ephemeral=True)
        return
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id in escenas:
        await interaction.response.send_message("⚠️ Ya hay sesion abierta", ephemeral=True)
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
        title="🎬 SESION ABIERTA",
        description=f"**{NOMBRE_SERVIDOR}**",
        color=discord.Color.gold()
    )
    embed.add_field(name="🛣️ Vias", value=f"{vias} vias", inline=True)
    embed.add_field(name="🚗 Velocidad", value=f"{velocidad_maxima} km/h", inline=True)
    embed.add_field(name="🏁 Adelantos", value="✅ Si" if adelantamientos.lower() == "si" else "❌ No", inline=True)
    embed.add_field(name="👑 Host", value=interaction.user.mention, inline=False)
    embed.add_field(name="🔗 Link", value=f"[Haz clic aqui]({link})", inline=False)
    embed.set_footer(text="¡Todos con DNI listo para el rol! 🪪")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cerrar_escena", description="🔒 Cerrar sesion - SOLO HOSTS")
async def cerrar_escena(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS pueden usar este comando", ephemeral=True)
        return
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id not in escenas:
        await interaction.response.send_message("❌ No hay sesion activa", ephemeral=True)
        return
    escena = escenas[channel_id]
    inicio = datetime.fromisoformat(escena["inicio"])
    duracion = datetime.now(timezone.utc) - inicio
    horas, resto = divmod(int(duracion.total_seconds()), 3600)
    minutos = resto // 60
    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)
    embed = discord.Embed(
        title="🔒 SESION CERRADA",
        description=f"¡Buen rol! Duracion: {horas}h {minutos}m",
        color=discord.Color.red()
    )
    embed.add_field(name="⭐", value="No olvides evaluar al staff con `/evaluar_staff`", inline=False)
    await interaction.response.send_message(embed=embed)

# ==================== VOTACIONES ====================
class VotoView(discord.ui.View):
    def __init__(self, channel_id: str):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="✅ Asistir", style=discord.ButtonStyle.success)
    async def asistir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._votar(interaction, "asistentes")

    @discord.ui.button(label="❌ No asistir", style=discord.ButtonStyle.danger)
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
            description=f"✅ Asistiran: {len(asist)}/{votacion['votos_requeridos']}\n❌ No asistiran: {len(no_asist)}",
            color=discord.Color.orange()
        )
        embed.add_field(name="✅", value="\n".join(f"<@{u}>" for u in asist) or "Nadie", inline=False)
        embed.add_field(name="❌", value="\n".join(f"<@{u}>" for u in no_asist) or "Nadie", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)
        if len(asist) == votacion["votos_requeridos"]:
            await interaction.channel.send(f"🎉 <@{votacion['host_id']}> ¡Meta alcanzada! Abre con `/abrir_escena`")

@bot.tree.command(name="votacion_sesion", description="🗳️ Votacion - SOLO HOSTS")
@app_commands.describe(votos_requeridos="1-20")
async def votacion_sesion(interaction: discord.Interaction, votos_requeridos: int):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS pueden usar este comando", ephemeral=True)
        return
    if not 1 <= votos_requeridos <= 20:
        await interaction.response.send_message("⚠️ 1-20 votos", ephemeral=True)
        return
    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id in votaciones:
        await interaction.response.send_message("⚠️ Ya hay votacion activa", ephemeral=True)
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
        description=f"Necesitan {votos_requeridos} votos",
        color=discord.Color.orange()
    )
    embed.add_field(name="✅ Asistentes", value="Nadie", inline=False)
    embed.add_field(name="❌ No asistentes", value="Nadie", inline=False)
    embed.set_footer(text=f"Host: {interaction.user.name}")
    await interaction.response.send_message(embed=embed, view=VotoView(interaction.channel_id))

@bot.tree.command(name="cerrar_votacion", description="🔒 Cerrar votacion - SOLO HOSTS")
async def cerrar_votacion(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo HOSTS pueden usar este comando", ephemeral=True)
        return
    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    if channel_id not in votaciones:
        await interaction.response.send_message("❌ No hay votacion activa", ephemeral=True)
        return
    del votaciones[channel_id]
    guardar(VOTACIONES_FILE, votaciones)
    await interaction.response.send_message("🔒 Votacion cerrada")

# ==================== AUTOS ====================
@bot.tree.command(name="registrar_auto", description="🚗 Registrar auto")
async def registrar_auto(interaction: discord.Interaction):
    class AutoModal(discord.ui.Modal, title="🚗 Registrar Vehiculo"):
        usuario_roblox = discord.ui.TextInput(label="Usuario Roblox", placeholder="Ej: Juanito_99", max_length=50)
        placa = discord.ui.TextInput(label="Placa", placeholder="Ej: ABC-123", max_length=20)
        modelo = discord.ui.TextInput(label="Modelo/Marca", placeholder="Ej: Ferrari 488", max_length=50)
        color = discord.ui.TextInput(label="Color", placeholder="Ej: Rojo", max_length=30)
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
            embed = discord.Embed(title="🚗 AUTO REGISTRADO", color=discord.Color.green())
            embed.add_field(name="🎮 Roblox", value=self.usuario_roblox.value, inline=False)
            embed.add_field(name="📋 Modelo", value=self.modelo.value, inline=True)
            embed.add_field(name="🎨 Color", value=self.color.value, inline=True)
            embed.add_field(name="🅿️ Placa", value=self.placa.value, inline=True)
            await modal_interaction.response.send_message(embed=embed)
    await interaction.response.send_modal(AutoModal())

@bot.tree.command(name="ver_autos", description="🚗 Ver autos")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE)
    user_autos = autos.get(str(objetivo.id), [])
    if not user_autos:
        await interaction.response.send_message(f"❌ {objetivo.name} no tiene autos registrados", ephemeral=True)
        return
    embed = discord.Embed(title=f"🚗 AUTOS DE {objetivo.name.upper()}", color=discord.Color.blue())
    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"🚘 Auto #{i}",
            value=f"🎮 {auto['usuario_roblox']}\n📋 {auto['modelo']}\n🎨 {auto['color']}\n🅿️ {auto['placa']}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# ==================== MULTAS ====================
@bot.tree.command(name="registrar_multa", description="🚨 Registrar multa - SOLO POLICIA")
async def registrar_multa(interaction: discord.Interaction):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICIA pueden usar este comando", ephemeral=True)
        return
    class MultiModal(discord.ui.Modal, title="🚨 Registrar Multa"):
        infractor = discord.ui.TextInput(label="Infractor", placeholder="Ej: Juan Perez", max_length=100)
        infraccion = discord.ui.TextInput(label="Infraccion", placeholder="Ej: Exceso de velocidad", max_length=100)
        precio = discord.ui.TextInput(label="Monto ($)", placeholder="Ej: 500", max_length=10)
        async def on_submit(self, modal_interaction: discord.Interaction):
            if not self.precio.value.isdigit():
                await modal_interaction.response.send_message("⚠️ Monto: numero", ephemeral=True)
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
            embed = discord.Embed(title="🚨 MULTA REGISTRADA", color=discord.Color.red())
            embed.add_field(name="👮 Oficial", value=modal_interaction.user.mention, inline=False)
            embed.add_field(name="👤 Infractor", value=self.infractor.value, inline=False)
            embed.add_field(name="⚖️ Infraccion", value=self.infraccion.value, inline=False)
            embed.add_field(name="💰 Monto", value=f"${self.precio.value}", inline=True)
            await modal_interaction.response.send_message(embed=embed)
    await interaction.response.send_modal(MultiModal())

@bot.tree.command(name="historial_multas", description="📋 Historial multas - SOLO POLICIA")
async def historial_multas(interaction: discord.Interaction):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICIA pueden usar este comando", ephemeral=True)
        return
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    if not historial:
        await interaction.response.send_message("📋 No hay multas registradas", ephemeral=True)
        return
    embed = discord.Embed(title="🚨 HISTORIAL DE MULTAS", color=discord.Color.red())
    for i, multa in enumerate(historial[-10:], 1):
        embed.add_field(
            name=f"📌 Multa #{i}",
            value=f"👮 {multa['oficial']}\n👤 {multa['infractor']}\n⚖️ {multa['infraccion']}\n💰 ${multa['precio']}\n📅 {multa['fecha']}",
            inline=False
        )
    embed.set_footer(text="Mostrando ultimas 10 multas")
    await interaction.response.send_message(embed=embed)

# ==================== EVALUACION ====================
@bot.tree.command(name="evaluar_staff", description="⭐ Evaluar staff")
@app_commands.describe(staff="Staff a evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
        que_hizo = discord.ui.TextInput(label="Que hizo?", placeholder="Ej: Ayudo en el rol", max_length=100)
