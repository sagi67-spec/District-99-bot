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

# ==================== CONFIGURACIÓN DE ROLES ====================
# ¡CAMBIA ESTOS NOMBRES POR LOS DE TU SERVIDOR!
ROL_HOST_NOMBRE = "Host | 🎮"
ROL_POLICIA_NOMBRE = "Wsp | 👮"
ROL_DNI_NOMBRE = "Dni | 📋"

def tiene_rol(member, rol_buscado):
    """Verifica si un miembro tiene un rol específico"""
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

# ==================== FUNCIONES DE ARCHIVOS ====================

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

# ==================== CONFIGURACIÓN DEL BOT ====================

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Crear archivos JSON si no existen
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

# ==================== DNI ====================

@bot.tree.command(name="crear_dni", description="🪪 Crea tu DNI de personaje")
@app_commands.describe(
    nombre="Nombre del personaje",
    apellidos="Apellidos del personaje",
    fecha_nacimiento="Fecha de nacimiento (DD/MM/YYYY)",
    edad="Edad del personaje"
)
async def crear_dni(interaction: discord.Interaction, nombre: str, apellidos: str, fecha_nacimiento: str, edad: int):
    """✅ Cualquier usuario puede crear su DNI"""
    
    if not validar_fecha(fecha_nacimiento):
        await interaction.response.send_message("❌ Formato de fecha inválido. Usa: **DD/MM/YYYY**", ephemeral=True)
        return

    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)
    
    if user_id in dnis:
        await interaction.response.send_message("⚠️ Ya tienes un DNI creado. Usa `/ver_dni` para verlo.", ephemeral=True)
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
            await interaction.response.send_message("✅ **¡DNI creado exitosamente!** Te he asignado el rol correspondiente. 🪪", ephemeral=True)
        else:
            await interaction.response.send_message("✅ **¡DNI creado exitosamente!** 🪪", ephemeral=True)
    except:
        await interaction.response.send_message("✅ **¡DNI creado exitosamente!** 🪪", ephemeral=True)

@bot.tree.command(name="ver_dni", description="🔍 Ver el DNI de un usuario")
@app_commands.describe(usuario="Usuario a consultar (opcional)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    """✅ Cualquier usuario puede ver DNIs"""
    
    objetivo = usuario or interaction.user
    dnis = cargar(DNI_FILE)
    datos = dnis.get(str(objetivo.id))
    
    if not datos:
        await interaction.response.send_message(f"❌ {objetivo.mention} **no tiene DNI creado**", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🪪 DNI DE {objetivo.name.upper()}",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Nombre", value=datos["nombre"], inline=True)
    embed.add_field(name="👥 Apellidos", value=datos["apellidos"], inline=True)
    embed.add_field(name="🎂 Edad", value=str(datos["edad"]), inline=True)
    embed.add_field(name="📅 Nacimiento", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="🔢 Número", value=datos["numero_dni"], inline=True)
    embed.add_field(name="📆 Expedición", value=datos.get("fecha_expedicion", "Desconocida"), inline=True)
    embed.set_thumbnail(url=objetivo.display_avatar.url)
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_dni", description="🗑️ Elimina tu propio DNI")
async def eliminar_dni(interaction: discord.Interaction):
    """✅ Solo el dueño del DNI puede eliminarlo"""
    
    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)
    
    if user_id not in dnis:
        await interaction.response.send_message("❌ **No tienes un DNI para eliminar**", ephemeral=True)
        return
    
    del dnis[user_id]
    guardar(DNI_FILE, dnis)
    
    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_DNI_NOMBRE)
        if rol and rol in interaction.user.roles:
            await interaction.user.remove_roles(rol)
    except:
        pass
    
    await interaction.response.send_message("🗑️ **Tu DNI ha sido eliminado correctamente**", ephemeral=True)

# ==================== ESCENAS ====================

@bot.tree.command(name="abrir_escena", description="🎬 Abrir sesión de rol - SOLO HOSTS")
@app_commands.describe(
    vias="Número de vías (1 o 2)",
    velocidad_maxima="Límite de velocidad (km/h)",
    adelantamientos="¿Se permiten adelantamientos? (Si/No)",
    link="Link del servidor (ej: https://...)"
)
async def abrir_escena(interaction: discord.Interaction, vias: str, velocidad_maxima: str, adelantamientos: str, link: str):
    """🔒 Solo usuarios con rol HOST pueden abrir escenas"""
    
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ **No tienes permisos para usar este comando.**\nSolo los **Hosts** pueden abrir escenas.", ephemeral=True)
        return
    
    if vias not in ["1", "2"]:
        await interaction.response.send_message("⚠️ **Vías inválidas.** Solo puedes seleccionar `1` o `2`.", ephemeral=True)
        return
    
    if not velocidad_maxima.isdigit():
        await interaction.response.send_message("⚠️ **Velocidad inválida.** Debe ser un número", ephemeral=True)
        return
    
    if adelantamientos.lower() not in ["si", "no"]:
        await interaction.response.send_message("⚠️ **Respuesta inválida.** Solo puedes seleccionar `Si` o `No`", ephemeral=True)
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id in escenas:
        await interaction.response.send_message("⚠️ **Ya hay una sesión abierta en este canal**", ephemeral=True)
        return

    adelanto_permitido = adelantamientos.lower() == "si"
    
    if adelanto_permitido:
        class VelocidadAdelantoModal(discord.ui.Modal, title="🚗 Velocidad de Adelantamiento"):
            velocidad_adelanto = discord.ui.TextInput(
                label="Velocidad permitida para adelantar (km/h)",
                placeholder="Ej: 80",
                max_length=10
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                if not self.velocidad_adelanto.value.isdigit():
                    await modal_interaction.response.send_message("⚠️ **Velocidad inválida.** Debe ser un número", ephemeral=True)
                    return
                
                velocidad_adelanto = int(self.velocidad_adelanto.value)
                
                escenas[channel_id] = {
                    "vias": vias,
                    "velocidad_maxima": velocidad_maxima,
                    "adelantamientos": True,
                    "velocidad_adelanto": velocidad_adelanto,
                    "link_servidor": link,
                    "host": str(interaction.user),
                    "host_id": str(interaction.user.id),
                    "inicio": datetime.now(timezone.utc).isoformat(),
                }
                guardar(ESCENAS_FILE, escenas)
                
                embed = discord.Embed(
                    title="🎬 **SESIÓN ABIERTA**",
                    description=f"**{NOMBRE_SERVIDOR}** - ¡Comienza el rol!",
                    color=discord.Color.gold()
                )
                embed.add_field(name="🛣️ Vías", value=f"{vias} vías", inline=True)
                embed.add_field(name="🚗 Velocidad Máx", value=f"{velocidad_maxima} km/h", inline=True)
                embed.add_field(name="🏁 Adelantamientos", value="✅ Permitidos", inline=True)
                embed.add_field(name="🚀 Vel. Adelanto", value=f"{velocidad_adelanto} km/h", inline=True)
                embed.add_field(name="👑 Host", value=interaction.user.mention, inline=False)
                embed.add_field(name="🔗 Servidor", value=f"[Haz clic aquí]({link})", inline=False)
                embed.add_field(name="📢", value="**¡Todos con DNI listo para el rol!** 🪪", inline=False)
                embed.set_footer(text=f"Sesión iniciada por {interaction.user.name}")
                
                await modal_interaction.response.send_message(embed=embed)
        
        await interaction.response.send_modal(VelocidadAdelantoModal())
        return
    
    escenas[channel_id] = {
        "vias": vias,
        "velocidad_maxima": velocidad_maxima,
        "adelantamientos": False,
        "link_servidor": link,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🎬 **SESIÓN ABIERTA**",
        description=f"**{NOMBRE_SERVIDOR}** - ¡Comienza el rol!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🛣️ Vías", value=f"{vias} vías", inline=True)
    embed.add_field(name="🚗 Velocidad Máx", value=f"{velocidad_maxima} km/h", inline=True)
    embed.add_field(name="🏁 Adelantamientos", value="❌ No permitidos", inline=True)
    embed.add_field(name="👑 Host", value=interaction.user.mention, inline=False)
    embed.add_field(name="🔗 Servidor", value=f"[Haz clic aquí]({link})", inline=False)
    embed.add_field(name="📢", value="**¡Todos con DNI listo para el rol!** 🪪", inline=False)
    embed.set_footer(text=f"Sesión iniciada por {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cerrar_escena", description="🔒 Cerrar sesión de rol - SOLO HOSTS")
async def cerrar_escena(interaction: discord.Interaction):
    """🔒 Solo usuarios con rol HOST pueden cerrar escenas"""
    
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ **No tienes permisos para usar este comando.**\nSolo los **Hosts** pueden cerrar escenas.", ephemeral=True)
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id not in escenas:
        await interaction.response.send_message("❌ **No hay una sesión activa en este canal**", ephemeral=True)
        return

    escena = escenas[channel_id]
    inicio = datetime.fromisoformat(escena["inicio"])
    duracion = datetime.now(timezone.utc) - inicio
    horas, resto = divmod(int(duracion.total_seconds()), 3600)
    minutos = resto // 60

    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🔒 **SESIÓN FINALIZADA**",
        description=f"**¡Excelente rol!** 👏\nDuración: {horas}h {minutos}m",
        color=discord.Color.red()
    )
    embed.add_field(name="⭐", value="**¡No olvides evaluar al staff con `/evaluar_staff`!**", inline=False)
    
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
            await interaction.response.send_message("⛔ **Esta votación ya no está activa**", ephemeral=True)
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
            title="🗳️ **VOTACIÓN EN CURSO**",
            description=f"✅ **Asistirán:** {len(asist)}/{votacion['votos_requeridos']}\n❌ **No asistirán:** {len(no_asist)}",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="✅ Asistentes",
            value="\n".join(f"<@{u}>" for u in asist) or "Nadie aún",
            inline=False
        )
        embed.add_field(
            name="❌ No asistentes",
            value="\n".join(f"<@{u}>" for u in no_asist) or "Nadie aún",
            inline=False
        )

        await interaction.response.edit_message(embed=embed, view=self)

        if len(asist) == votacion["votos_requeridos"]:
            await interaction.channel.send(
                f"🎉 **<@{votacion['host_id']}> ¡Meta alcanzada!**\n"
                f"Puedes abrir la sesión con `/abrir_escena` 🚗"
            )

@bot.tree.command(name="votacion_sesion", description="🗳️ Crear votación para abrir sesión - SOLO HOSTS")
@app_commands.describe(votos_requeridos="Número de votos necesarios (1-20)")
async def votacion_sesion(interaction: discord.Interaction, votos_requeridos: int):
    """🔒 Solo usuarios con rol HOST pueden crear votaciones"""
    
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ **No tienes permisos para usar este comando.**\nSolo los **Hosts** pueden crear votaciones.", ephemeral=True)
        return
    
    if not (1 <= votos_requeridos <= 20):
        await interaction.response.send_message("⚠️ **Número inválido.** Debe ser entre `1` y `20`.", ephemeral=True)
        return

    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id in votaciones:
        await interaction.response.send_message("⚠️ **Ya hay una votación activa en este canal**", ephemeral=True)
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
        title="🗳️ **¿ABRIMOS SESIÓN?**",
        description=f"**Necesitamos {votos_requeridos} votos para empezar**",
        color=discord.Color.orange()
    )
    embed.add_field(name="✅ Asistentes", value="Nadie aún", inline=False)
    embed.add_field(name="❌ No asistentes", value="Nadie aún", inline=False)
    embed.set_footer(text=f"Host: {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed, view=VotoView(interaction.channel_id))

@bot.tree.command(name="cerrar_votacion", description="🔒 Cerrar votación - SOLO HOSTS")
async def cerrar_votacion(interaction: discord.Interaction):
    """🔒 Solo usuarios con rol HOST pueden cerrar votaciones"""
    
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ **No tienes permisos para usar este comando.**\nSolo los **Hosts** pueden cerrar votaciones.", ephemeral=True)
        return

    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id not in votaciones:
        await interaction.response.send_message("❌ **No hay una votación activa en este canal**", ephemeral=True)
        return

    del votaciones[channel_id]
    guardar(VOTACIONES_FILE, votaciones)
    
    await interaction.response.send_message("🔒 **Votación cerrada exitosamente**")

# ==================== AUTOS ====================

class AutoModal(discord.ui.Modal, title="🚗 Registrar Vehículo"):
    usuario_roblox = discord.ui.TextInput(label="Usuario de Roblox", placeholder="Ej: Juanito_99", max_length=50)
    placa = discord.ui.TextInput(label="Placa del vehículo", placeholder="Ej: ABC-123", max_length=20)
    modelo = discord.ui.TextInput(label="Modelo/Marca", placeholder="Ej: Ferrari 488", max_length=50)
    color = discord.ui.TextInput(label="Color", placeholder="Ej: Rojo", max_length=30)

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

        embed = discord.Embed(
            title="🚗 **¡VEHÍCULO REGISTRADO!**",
            color=discord.Color.green()
        )
        embed.add_field(name="🎮 Roblox", value=self.usuario_roblox.value, inline=False)
        embed.add_field(name="📋 Modelo", value=self.modelo.value, inline=True)
        embed.add_field(name="🎨 Color", value=self.color.value, inline=True)
        embed.add_field(name="📢", value="**¡Todos con DNI listo para el rol!** 🪪", inline=False)
