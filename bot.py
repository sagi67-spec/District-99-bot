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

# ==================== CONFIGURACIÓN ====================
CANAL_PAGOS_ID = 1529957306198917200  # ID del canal para pagar multas
PAGOS_PENDIENTES = {}  # {user_id: {"monto": int, "timestamp": datetime}}

# ==================== ROLES ====================
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
    numero = int(user_id) % 100000000
    return f"{numero:08d}"

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
intents.message_content = True
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
    
    numero_dni = generar_numero_dni(user_id)
    
    dnis[user_id] = {
        "nombre": nombre,
        "apellidos": apellidos,
        "fecha_nacimiento": fecha_nacimiento,
        "edad": edad,
        "numero_dni": numero_dni,
        "fecha_expedicion": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        "usuario_discord": str(interaction.user)
    }
    guardar(DNI_FILE, dnis)
    
    embed = discord.Embed(
        title="🪪 DNI CREADO",
        description=f"**{interaction.user.mention}** tu DNI ha sido creado exitosamente.",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Nombre", value=nombre, inline=True)
    embed.add_field(name="👥 Apellidos", value=apellidos, inline=True)
    embed.add_field(name="🎂 Edad", value=str(edad), inline=True)
    embed.add_field(name="📅 Nacimiento", value=fecha_nacimiento, inline=True)
    embed.add_field(name="🔢 Número DNI", value=numero_dni, inline=True)
    embed.add_field(name="📆 Expedición", value=dnis[user_id]["fecha_expedicion"], inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"DNI registrado en {NOMBRE_SERVIDOR}")
    
    # Asignar rol de DNI
    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_DNI_NOMBRE)
        if rol:
            if interaction.guild.me.guild_permissions.manage_roles:
                await interaction.user.add_roles(rol)
                embed.add_field(name="✅ Rol", value=f"Rol {ROL_DNI_NOMBRE} asignado", inline=False)
            else:
                embed.add_field(name="⚠️ Rol", value="No tengo permisos para asignar el rol", inline=False)
        else:
            embed.add_field(name="⚠️ Rol", value=f"No encontré el rol '{ROL_DNI_NOMBRE}'", inline=False)
    except Exception as e:
        embed.add_field(name="⚠️ Rol", value=f"Error al asignar: {e}", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_dni", description="🔍 Ver DNI")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    dnis = cargar(DNI_FILE)
    datos = dnis.get(str(objetivo.id))
    
    if not datos:
        await interaction.response.send_message(f"❌ {objetivo.mention} no tiene DNI creado", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🪪 DNI DE {objetivo.name.upper()}",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Nombre", value=datos["nombre"], inline=True)
    embed.add_field(name="👥 Apellidos", value=datos["apellidos"], inline=True)
    embed.add_field(name="🎂 Edad", value=str(datos["edad"]), inline=True)
    embed.add_field(name="📅 Nacimiento", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="🔢 Número DNI", value=datos["numero_dni"], inline=True)
    embed.add_field(name="📆 Expedición", value=datos.get("fecha_expedicion", "Desconocida"), inline=True)
    embed.set_thumbnail(url=objetivo.display_avatar.url)
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    
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
    
    await interaction.response.send_message("🗑️ Tu DNI ha sido eliminado", ephemeral=True)
    # ==================== ESCENAS ====================
@bot.tree.command(name="abrir_escena", description="🎬 Abrir sesion - SOLO HOSTS")
@app_commands.describe(
    vias="1 o 2",
    velocidad_maxima="Limite de velocidad (mph)",
    adelantamientos="Selecciona Si o No",
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
        await interaction.response.send_message("⚠️ Solo puedes seleccionar `Si` o `No`", ephemeral=True)
        return
    
    if adelantamientos.lower() == "si":
        class VelocidadAdelantoModal(discord.ui.Modal, title="🚗 Velocidad de Adelantamiento"):
            velocidad_adelanto = discord.ui.TextInput(
                label="Velocidad permitida para adelantar (mph)",
                placeholder="Ej: 80",
                max_length=10,
                required=True
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                if not self.velocidad_adelanto.value.isdigit():
                    await modal_interaction.response.send_message("⚠️ Velocidad invalida. Debe ser un numero", ephemeral=True)
                    return
                
                velocidad_adelanto = int(self.velocidad_adelanto.value)
                
                escenas = cargar(ESCENAS_FILE)
                channel_id = str(modal_interaction.channel_id)
                
                if channel_id in escenas:
                    await modal_interaction.response.send_message("⚠️ Ya hay sesion abierta", ephemeral=True)
                    return
                
                escenas[channel_id] = {
                    "vias": vias,
                    "velocidad_maxima": velocidad_maxima,
                    "adelantamientos": True,
                    "velocidad_adelanto": velocidad_adelanto,
                    "link_servidor": link,
                    "host": str(modal_interaction.user),
                    "host_id": str(modal_interaction.user.id),
                    "inicio": datetime.now(timezone.utc).isoformat(),
                }
                guardar(ESCENAS_FILE, escenas)
                
                embed = discord.Embed(
                    title="🎬 SESION ABIERTA",
                    description=f"**{NOMBRE_SERVIDOR}**",
                    color=discord.Color.gold()
                )
                embed.add_field(name="🛣️ Vias", value=f"{vias} vias", inline=True)
                embed.add_field(name="🚗 Velocidad Max", value=f"{velocidad_maxima} mph", inline=True)
                embed.add_field(name="🏁 Adelantamientos", value="✅ Permitidos", inline=True)
                embed.add_field(name="🚀 Vel. Adelanto", value=f"{velocidad_adelanto} mph", inline=True)
                embed.add_field(name="👑 Host", value=modal_interaction.user.mention, inline=False)
                embed.add_field(name="🔗 Link", value=f"[Haz clic aqui]({link})", inline=False)
                embed.set_footer(text="¡Todos con DNI listo para el rol! 🪪")
                
                await modal_interaction.response.send_message(embed=embed)
        
        await interaction.response.send_modal(VelocidadAdelantoModal())
        return
    
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id in escenas:
        await interaction.response.send_message("⚠️ Ya hay sesion abierta", ephemeral=True)
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
        title="🎬 SESION ABIERTA",
        description=f"**{NOMBRE_SERVIDOR}**",
        color=discord.Color.gold()
    )
    embed.add_field(name="🛣️ Vias", value=f"{vias} vias", inline=True)
    embed.add_field(name="🚗 Velocidad Max", value=f"{velocidad_maxima} mph", inline=True)
    embed.add_field(name="🏁 Adelantamientos", value="❌ No permitidos", inline=True)
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
@bot.tree.command(name="registrar_auto", description="🚗 Registrar tu vehiculo con foto")
@app_commands.describe(
    usuario_roblox="Tu usuario de Roblox",
    placa="Placa del vehiculo",
    modelo="Modelo/Marca del vehiculo",
    color="Color del vehiculo",
    foto="Sube una foto del vehiculo (OBLIGATORIO - adjunta una imagen)"
)
async def registrar_auto(
    interaction: discord.Interaction,
    usuario_roblox: str,
    placa: str,
    modelo: str,
    color: str,
    foto: discord.Attachment
):
    """Registra un vehiculo con foto OBLIGATORIA"""
    
    autos = cargar(AUTOS_FILE)
    user_id = str(interaction.user.id)
    
    # Verificar si la foto es válida (que sea una imagen)
    if not foto.content_type or not foto.content_type.startswith('image/'):
        await interaction.response.send_message("⚠️ El archivo debe ser una imagen (jpg, png, gif, etc.)", ephemeral=True)
        return
    
    autos.setdefault(user_id, []).append({
        "usuario_discord": str(interaction.user),
        "usuario_roblox": usuario_roblox,
        "placa": placa,
        "modelo": modelo,
        "color": color,
        "foto": foto.url,
        "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        "registrado_por": str(interaction.user)
    })
    guardar(AUTOS_FILE, autos)
    
    embed = discord.Embed(
        title="🚗 ¡VEHICULO REGISTRADO!",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Usuario Discord", value=interaction.user.mention, inline=False)
    embed.add_field(name="🎮 Usuario Roblox", value=usuario_roblox, inline=False)
    embed.add_field(name="📋 Modelo", value=modelo, inline=True)
    embed.add_field(name="🎨 Color", value=color, inline=True)
    embed.add_field(name="🅿️ Placa", value=placa, inline=True)
    embed.set_image(url=foto.url)
    embed.set_footer(text=f"Registrado por {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ver_autos", description="🚗 Ver autos de un usuario")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE)
    user_autos = autos.get(str(objetivo.id), [])
    
    if not user_autos:
        await interaction.response.send_message(f"❌ {objetivo.name} no tiene autos registrados", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🚗 AUTOS DE {objetivo.name.upper()}",
        color=discord.Color.blue()
    )
    
    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"🚘 Auto #{i}",
            value=(
                f"👤 **Discord:** {auto['usuario_discord']}\n"
                f"🎮 **Roblox:** {auto['usuario_roblox']}\n"
                f"📋 **Modelo:** {auto['modelo']}\n"
                f"🎨 **Color:** {auto['color']}\n"
                f"🅿️ **Placa:** {auto['placa']}\n"
                f"📅 **Registro:** {auto['fecha']}"
            ),
            inline=False
        )
        if auto.get('foto'):
            embed.set_image(url=auto['foto'])
    
    await interaction.response.send_message(embed=embed)

# ==================== ELIMINAR AUTO ====================
@bot.tree.command(name="eliminar_auto", description="🗑️ Eliminar un auto registrado")
@app_commands.describe(
    numero_auto="Número del auto a eliminar (1, 2, 3...)"
)
async def eliminar_auto(interaction: discord.Interaction, numero_auto: int):
    """Elimina un auto registrado por el usuario"""
    
    autos = cargar(AUTOS_FILE)
    user_id = str(interaction.user.id)
    
    if user_id not in autos or not autos[user_id]:
        await interaction.response.send_message("❌ No tienes autos registrados", ephemeral=True)
        return
    
    if numero_auto < 1 or numero_auto > len(autos[user_id]):
        await interaction.response.send_message(f"⚠️ Número inválido. Tienes {len(autos[user_id])} autos registrados.", ephemeral=True)
        return
    
    auto_eliminado = autos[user_id].pop(numero_auto - 1)
    guardar(AUTOS_FILE, autos)
    
    embed = discord.Embed(
        title="🗑️ AUTO ELIMINADO",
        description=f"**{interaction.user.mention}** has eliminado tu auto.",
        color=discord.Color.red()
    )
    embed.add_field(name="📋 Modelo", value=auto_eliminado.get('modelo', 'Desconocido'), inline=True)
    embed.add_field(name="🅿️ Placa", value=auto_eliminado.get('placa', 'Desconocida'), inline=True)
    embed.add_field(name="🎨 Color", value=auto_eliminado.get('color', 'Desconocido'), inline=True)
    embed.set_footer(text=f"Auto eliminado el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    await interaction.response.send_message(embed=embed)

# ==================== MULTAS ====================
@bot.tree.command(name="registrar_multa", description="🚨 Registrar multa - SOLO POLICIA")
@app_commands.describe(
    infractor="Usuario infractor",
    infraccion="Infraccion cometida",
    precio="Monto de la multa ($)"
)
async def registrar_multa(
    interaction: discord.Interaction,
    infractor: discord.Member,
    infraccion: str,
    precio: str
):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICIA pueden usar este comando", ephemeral=True)
        return
    
    if not precio.isdigit():
        await interaction.response.send_message("⚠️ Monto: numero", ephemeral=True)
        return
    
    multas = cargar(MULTAS_FILE)
    multas.setdefault("historial", []).append({
        "oficial_id": str(interaction.user.id),
        "oficial": str(interaction.user),
        "infractor_id": str(infractor.id),
        "infractor": str(infractor),
        "infraccion": infraccion,
        "precio": int(precio),
        "pagada": False,
        "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
    })
    guardar(MULTAS_FILE, multas)
    
    embed = discord.Embed(
        title="🚨 ¡MULTA REGISTRADA!",
        color=discord.Color.red()
    )
    embed.add_field(name="👮 Oficial", value=interaction.user.mention, inline=False)
    embed.add_field(name="👤 Infractor", value=infractor.mention, inline=False)
    embed.add_field(name="⚖️ Infraccion", value=infraccion, inline=False)
    embed.add_field(name="💰 Monto", value=f"**${precio}**", inline=True)
    embed.add_field(name="📌 Estado", value="❌ Sin pagar", inline=True)
    embed.set_footer(text=f"Registrada el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    await interaction.response.send_message(
        content=f"{infractor.mention} ¡Has recibido una multa!\n"
                f"**Para pagar:**\n"
                f"1. Escribe en <#{CANAL_PAGOS_ID}>: `!pay <@{bot.user.id}> {precio}`\n"
                f"2. Luego usa `/confirmar_pago` en <#{CANAL_PAGOS_ID}>",
        embed=embed
    )

@bot.tree.command(name="historial_multas", description="📋 Ver historial de multas - SOLO POLICIA")
@app_commands.describe(usuario="Usuario (opcional)")
async def historial_multas(interaction: discord.Interaction, usuario: discord.Member = None):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICIA pueden usar este comando", ephemeral=True)
        return
    
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    
    if not historial:
        await interaction.response.send_message("📋 No hay multas registradas", ephemeral=True)
        return
    
    if usuario:
        historial = [m for m in historial if m.get('infractor_id') == str(usuario.id)]
        if not historial:
            await interaction.response.send_message(f"📋 {usuario.name} no tiene multas registradas", ephemeral=True)
            return
        titulo = f"🚨 MULTAS DE {usuario.name.upper()}"
    else:
        titulo = "🚨 HISTORIAL DE MULTAS (TODOS)"
    
    embed = discord.Embed(title=titulo, color=discord.Color.red())
    
    for i, multa in enumerate(historial[-10:], 1):
        estado = "✅ Pagada" if multa.get('pagada', False) else "❌ Sin pagar"
        embed.add_field(
            name=f"📌 Multa #{i}",
            value=(
                f"👮 **Oficial:** {multa['oficial']}\n"
                f"👤 **Infractor:** {multa['infractor']}\n"
                f"⚖️ **Infraccion:** {multa['infraccion']}\n"
                f"💰 **Monto:** ${multa['precio']}\n"
                f"📌 **Estado:** {estado}\n"
                f"📅 **Fecha:** {multa['fecha']}"
            ),
            inline=False
        )
    
    embed.set_footer(text="Mostrando ultimas 10 multas")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mis_multas", description="📋 Ver tu historial de multas")
async def mis_multas(interaction: discord.Interaction):
    """Ciudadanos pueden ver sus propias multas"""
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    user_id = str(interaction.user.id)
    
    mis_multas = [m for m in historial if m.get('infractor_id') == user_id]
    
    if not mis_multas:
        await interaction.response.send_message("📋 No tienes multas registradas", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🚨 TUS MULTAS",
        description=f"Total: {len(mis_multas)} multas",
        color=discord.Color.orange()
    )
    
    total = 0
    for i, multa in enumerate(mis_multas[-10:], 1):
        total += multa.get('precio', 0)
        estado = "✅ Pagada" if multa.get('pagada', False) else "❌ Sin pagar"
        embed.add_field(
            name=f"📌 Multa #{i}",
            value=(
                f"👮 **Oficial:** {multa['oficial']}\n"
                f"⚖️ **Infraccion:** {multa['infraccion']}\n"
                f"💰 **Monto:** ${multa['precio']}\n"
                f"📌 **Estado:** {estado}\n"
                f"📅 **Fecha:** {multa['fecha']}"
            ),
            inline=False
        )
    
    embed.add_field(name="💸 TOTAL ADEUDADO", value=f"**${total}**", inline=False)
    embed.set_footer(text="Mostrando ultimas 10 multas")
    
    await interaction.response.send_message(embed=embed)
    # ==================== PAGAR MULTAS ====================
@bot.tree.command(name="pagar_multa", description="💰 Ver tus multas pendientes para pagar")
async def pagar_multa(interaction: discord.Interaction):
    """Muestra las multas pendientes del usuario (solo él puede verlo)"""
    
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    user_id = str(interaction.user.id)
    
    # Buscar multas no pagadas del usuario
    mis_multas = []
    for multa in historial:
        if multa.get('infractor_id') == user_id and not multa.get('pagada', False):
            mis_multas.append(multa)
    
    if not mis_multas:
        await interaction.response.send_message(
            "✅ No tienes multas pendientes. ¡Estás al día!",
            ephemeral=True
        )
        return
    
    total = sum(multa['precio'] for multa in mis_multas)
    
    embed = discord.Embed(
        title="🚨 TUS MULTAS PENDIENTES",
        description=f"Tienes {len(mis_multas)} multas sin pagar.",
        color=discord.Color.orange()
    )
    
    for i, multa in enumerate(mis_multas, 1):
        embed.add_field(
            name=f"📌 Multa #{i}",
            value=(
                f"👮 **Oficial:** {multa['oficial']}\n"
                f"⚖️ **Infracción:** {multa['infraccion']}\n"
                f"💰 **Monto:** ${multa['precio']}\n"
                f"📅 **Fecha:** {multa['fecha']}"
            ),
            inline=False
        )
    
    embed.add_field(
        name="💸 TOTAL ADEUDADO",
        value=f"**${total}**",
        inline=False
    )
    embed.add_field(
        name="📢 ¿CÓMO PAGAR?",
        value=(
            f"1. Escribe en <#{CANAL_PAGOS_ID}>:\n"
            f"   `!pay <@{bot.user.id}> {total}` (para pagar todo)\n"
            f"   O `!pay <@{bot.user.id}> [monto]` (para pagar una multa específica)\n"
            f"2. Luego usa `/confirmar_pago` en <#{CANAL_PAGOS_ID}>"
        ),
        inline=False
    )
    embed.set_footer(text="Este mensaje es solo visible para ti.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== CONFIRMAR PAGO ====================
@bot.tree.command(name="confirmar_pago", description="💰 Confirmar el pago de una multa")
async def confirmar_pago(interaction: discord.Interaction):
    """Confirma el pago de una multa (solo si UnbelievaBoat lo aceptó)"""
    
    user_id = str(interaction.user.id)
    canal = interaction.channel
    
    # Verificar que el comando se use en el canal de pagos
    if canal.id != CANAL_PAGOS_ID:
        await interaction.response.send_message(
            f"⚠️ Este comando solo se puede usar en <#{CANAL_PAGOS_ID}>",
            ephemeral=True
        )
        return
    
    # Verificar si el usuario tiene un pago pendiente
    if user_id not in PAGOS_PENDIENTES:
        await interaction.response.send_message(
            "❌ **NO PUEDES CONFIRMAR ESTE PAGO**\n"
            "El pago fue rechazado por UnbelievaBoat porque no tenías suficiente dinero.\n"
            "💰 **Alternativas:**\n"
            "1. Retira dinero del banco con `!withdraw [cantidad]`\n"
            "2. Vuelve a intentar con `!pay <@District99Bot> [monto]`",
            ephemeral=True
        )
        return
    
    pago_data = PAGOS_PENDIENTES[user_id]
    monto = pago_data["monto"]
    
    # Verificar que el pago no haya expirado (10 minutos)
    tiempo_transcurrido = (datetime.now(timezone.utc) - pago_data["timestamp"]).total_seconds()
    if tiempo_transcurrido > 600:
        del PAGOS_PENDIENTES[user_id]
        await interaction.response.send_message(
            "⏰ El tiempo para confirmar el pago ha expirado (10 minutos).\n"
            "Usa `!pay` nuevamente.",
            ephemeral=True
        )
        return
    
    # Buscar multas pendientes del usuario
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    
    multas_pendientes = []
    for i, multa in enumerate(historial):
        if multa.get('infractor_id') == user_id and not multa.get('pagada', False):
            multas_pendientes.append((i, multa))
    
    if not multas_pendientes:
        del PAGOS_PENDIENTES[user_id]
        await interaction.response.send_message(
            "✅ No tienes multas pendientes. ¡Estás al día!",
            ephemeral=True
        )
        return
    
    total_adeudado = sum(multa['precio'] for _, multa in multas_pendientes)
    
    # ========== PROCESAR PAGO ==========
    # Caso 1: Pagó el total exacto (todas las multas)
    if monto == total_adeudado:
        oficiales_notificados = set()
        for idx, multa in multas_pendientes:
            historial[idx]['pagada'] = True
            historial[idx]['fecha_pago'] = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
            if multa.get('oficial_id'):
                oficiales_notificados.add(multa['oficial_id'])
        
        guardar(MULTAS_FILE, multas)
        del PAGOS_PENDIENTES[user_id]
        
        embed = discord.Embed(
            title="💰 ¡PAGO CONFIRMADO!",
            description=f"{interaction.user.mention} ha pagado **TODAS** sus multas.",
            color=discord.Color.green()
        )
        embed.add_field(name="💸 Total pagado", value=f"**${monto}**", inline=True)
        embed.add_field(name="📌 Multas pagadas", value=f"{len(multas_pendientes)} multas", inline=True)
        embed.set_footer(text=f"Pago confirmado el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
        
        await interaction.response.send_message(embed=embed)
        
        for oficial_id in oficiales_notificados:
            await canal.send(f"<@{oficial_id}> ✅ El ciudadano {interaction.user.mention} ha pagado todas sus multas.")
        return
    
    # Caso 2: Pagó una multa específica
    for idx, multa in multas_pendientes:
        if multa['precio'] == monto:
            historial[idx]['pagada'] = True
            historial[idx]['fecha_pago'] = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
            guardar(MULTAS_FILE, multas)
            
            oficial_id = multa.get('oficial_id')
            del PAGOS_PENDIENTES[user_id]
            
            embed = discord.Embed(
                title="💰 ¡PAGO CONFIRMADO!",
                description=f"{interaction.user.mention} ha pagado su multa.",
                color=discord.Color.green()
            )
            embed.add_field(name="👮 Oficial", value=f"<@{oficial_id}>" if oficial_id else "Desconocido", inline=False)
            embed.add_field(name="⚖️ Infracción", value=multa['infraccion'], inline=False)
            embed.add_field(name="💰 Monto pagado", value=f"**${monto}**", inline=True)
            embed.set_footer(text=f"Pago confirmado el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
            
            await interaction.response.send_message(embed=embed)
            
            if oficial_id:
                await canal.send(f"<@{oficial_id}> ✅ El ciudadano {interaction.user.mention} ha pagado su multa.")
            return
    
    # Caso 3: El monto no coincide con ninguna multa
    await interaction.response.send_message(
        f"⚠️ Pagaste **${monto}** pero tus multas pendientes son:\n" +
        "\n".join(f"• ${multa['precio']} - {multa['infraccion']}" for _, multa in multas_pendientes) +
        f"\n\nTotal adeudado: **${total_adeudado}**\n"
        f"Si pagaste el total, escribe `!pay <@{bot.user.id}> {total_adeudado}` y luego `/confirmar_pago` nuevamente.",
        ephemeral=True
    )

# ==================== EVALUAR STAFF ====================
class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
    que_hizo = discord.ui.TextInput(
        label="Que hizo el staff?",
        placeholder="Ej: Ayudo con el rol, fue muy atento...",
        max_length=200
    )
    calificacion = discord.ui.TextInput(
        label="Calificacion (1-10)",
        placeholder="Ej: 8",
        max_length=2
    )
    amable = discord.ui.TextInput(
        label="Fue amable?",
        placeholder="Ej: Si, muy amable",
        max_length=150
    )
    queja = discord.ui.TextInput(
        label="Sugerencias o queja (opcional)",
        required=False,
        max_length=300
    )

    def __init__(self, staff: discord.Member):
        super().__init__()
        self.staff = staff

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nota = int(self.calificacion.value.strip())
            if not 1 <= nota <= 10:
                raise ValueError
        except:
            await interaction.response.send_message("⚠️ Calificacion invalida. Usa un numero del 1 al 10", ephemeral=True)
            return
        
        evaluaciones = cargar(EVALUACIONES_FILE)
        clave = str(self.staff.id)
        
        evaluaciones.setdefault(clave, []).append({
            "staff_id": str(self.staff.id),
            "staff": str(self.staff),
            "evaluador_id": str(interaction.user.id),
            "evaluador": str(interaction.user),
            "que_hizo": self.que_hizo.value,
            "calificacion": nota,
            "amable": self.amable.value,
            "queja": self.queja.value or "Ninguna",
            "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
        })
        guardar(EVALUACIONES_FILE, evaluaciones)
        
        estrellas = "⭐" * round(nota / 2)
        
        embed = discord.Embed(
            title="📝 ¡EVALUACION REGISTRADA!",
            description=f"**Staff evaluado:** {self.staff.mention}",
            color=discord.Color.purple()
        )
        embed.add_field(name="⭐ Calificacion", value=f"{estrellas} ({nota}/10)", inline=False)
        embed.add_field(name="🤝 Amabilidad", value=self.amable.value, inline=False)
        embed.add_field(name="📌 Accion", value=self.que_hizo.value, inline=False)
        embed.add_field(name="💬 Sugerencias", value=self.queja.value or "Ninguna", inline=False)
        embed.set_footer(text=f"Evaluado por {interaction.user.name}")
        
        await interaction.response.send_message(
            content=f"{self.staff.mention} ¡Has recibido una evaluacion! ⭐",
            embed=embed
        )

@bot.tree.command(name="evaluar_staff", description="⭐ Evaluar al staff")
@app_commands.describe(staff="Staff a evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvalModal(staff))

# ==================== EVENTO ON_MESSAGE ====================
@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    
    # Solo procesar en el canal de pagos
    if message.channel.id != CANAL_PAGOS_ID:
        await bot.process_commands(message)
        return
    
    # Detectar comando !pay
    if message.content.lower().startswith("!pay"):
        partes = message.content.split()
        if len(partes) >= 3:
            mencion = partes[1]
            monto_str = partes[2]
            
            if monto_str.isdigit() and (mencion == f"<@{bot.user.id}>" or mencion == f"<@!{bot.user.id}>"):
                monto = int(monto_str)
                user_id = str(message.author.id)
                user_mention = message.author.mention
                
                # Guardar el pago pendiente temporalmente
                PAGOS_PENDIENTES[user_id] = {
                    "monto": monto,
                    "timestamp": datetime.now(timezone.utc),
                    "mensaje_id": message.id
                }
                
                # Esperar respuesta de UnbelievaBoat (5 segundos)
                def check(m):
                    return (m.author.name == "UnbelievaBoat" or "UnbelievaBoat" in str(m.author)) and user_mention in m.content
                
                try:
                    respuesta = await bot.wait_for('message', timeout=5.0, check=check)
                    contenido = respuesta.content.lower()
                    print(f"📊 Respuesta de UnbelievaBoat: {contenido}")
                    
                    # ========== PALABRAS CLAVE DE RECHAZO ==========
                    rechazo = [
                        "don't have that much money",
                        "insufficient",
                        "not enough",
                        "you don't have",
                        "you have insufficient",
                        "you currently have",
                        "you only have",
                        "don't have enough",
                        "you do not have"
                    ]
                    
                    # ========== PALABRAS CLAVE DE ÉXITO ==========
                    exito = [
                        "sent",
                        "paid",
                        "success",
                        "transferred",
                        "gave",
                        "✅",
                        "successfully",
                        "completed"
                    ]
                    
                    # Verificar si fue rechazado
                    if any(word in contenido for word in rechazo):
                        await message.channel.send(
                            f"{user_mention} ❌ **PAGO RECHAZADO POR UNBELIEVABOAT**\n"
                            f"No tienes suficiente dinero en mano para pagar **${monto}**.\n"
                            f"💰 Tu saldo actual es de **$0** en mano.\n"
                            f"🏦 **Alternativas:** Retira dinero del banco con `!withdraw [cantidad]`"
                        )
                        # ELIMINAR el pago pendiente
                        if user_id in PAGOS_PENDIENTES:
                            del PAGOS_PENDIENTES[user_id]
                            print(f"❌ Pago rechazado y eliminado para {user_id}")
                        return
                    
                    # Verificar si fue exitoso
                    elif any(word in contenido for word in exito):
                        await message.channel.send(
                            f"{user_mention} ✅ **PAGO EXITOSO**\n"
                            f"Ahora usa `/confirmar_pago` para registrar el pago en el sistema."
                        )
                        return
                    
                    else:
                        await message.channel.send(
                            f"{user_mention} ⚠️ No pude verificar el estado de tu pago automáticamente.\n"
                            f"Si el pago fue exitoso, usa `/confirmar_pago` para registrarlo."
                        )
                        return
                        
                except TimeoutError:
                    print("⏰ No se recibió respuesta de UnbelievaBoat.")
                    await message.channel.send(
                        f"{user_mention} ⚠️ No pude verificar tu pago automáticamente.\n"
                        f"Si el pago fue exitoso, usa `/confirmar_pago` para registrarlo.\n"
                        f"Si no tienes suficiente dinero, el pago fue rechazado."
                    )
                    return
                except Exception as e:
                    print(f"❌ Error al procesar pago: {e}")
                    return
    
    await bot.process_commands(message)

# ==================== INICIAR ====================
print("🚀 Intentando conectar a Discord...")
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ ERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
