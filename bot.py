"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
CÓDIGO COMPLETO - PARTE 1/7
"""

import json
import os
import re
import asyncio
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"🔍 TOKEN: {TOKEN[:10] if TOKEN else 'NO ENCONTRADO'}...")

if not TOKEN:
    print("❌ TOKEN NO ENCONTRADO")
    exit(1)

# ==================== ARCHIVOS JSON ====================
DNI_FILE = "dnis.json"
ESCENAS_FILE = "escenas.json"
EVALUACIONES_FILE = "evaluaciones.json"
VOTACIONES_FILE = "votaciones.json"
AUTOS_FILE = "autos.json"
MULTAS_FILE = "multas.json"
LICENCIAS_FILE = "licencias.json"
TURNOS_FILE = "turnos.json"

# ==================== CONFIGURACIÓN DEL SERVIDOR ====================
NOMBRE_SERVIDOR = "DISTRICT 99"
LOGO_SERVIDOR = "https://cdn.discordapp.com/attachments/1530830750310596618/1531040035552366592/1785098676803.png?ex=6a67c3a5&is=6a667225&hm=f6a7491ca085f5e2cbb89f0892ff6be638242f65b0785311df8a9dae181c1b76&"
FECHA_CREACION = datetime(2026, 7, 7)

# ==================== URLS DE IMÁGENES ====================
URL_SESION = "https://cdn.discordapp.com/attachments/1530830750310596618/1531040035552366592/1785098676803.png?ex=6a67c3a5&is=6a667225&hm=f6a7491ca085f5e2cbb89f0892ff6be638242f65b0785311df8a9dae181c1b76&"
URL_SESION_CERRADA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531077254862475419/1785107374573.png?ex=6a67e64f&is=6a6694cf&hm=2874cbcafaaa8d20a2c8790f333aa4ebb3a5397d0c5b975fd838e4f93657dbf5&"
URL_VOTACION_ABIERTA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531051469783044339/17851013550952.png?ex=6a67ce4b&is=6a667ccb&hm=aeb75fbbd6517e9b757c1f5f7c49ec919f823c0f9a9a35d226c7bff7746caa8d&"
URL_VOTACION_CERRADA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531051478922559638/17851013857782.png?ex=6a67ce4e&is=6a667cce&hm=e959c873a7934248c6c080cdddb4f72b12387b564de42feeb0e5e47f9322c9ab&"
URL_TURNOS = "https://cdn.discordapp.com/attachments/1530830750310596618/1531055540514455572/17851021019872.png?ex=6a67d216&is=6a668096&hm=3bddae490796415f8448684f03e7932e64264750921009730b84f3ecfbd4f75a&"
URL_MULTA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531055546965430323/17851021478742.png?ex=6a67d218&is=6a668098&hm=2216204e8e15107614ff02bea59d14010c2707dbec46a71e57b6bdc3afdbb9bd&"
URL_GREENVILLE = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192419599646861/CIUDAD_20260727_002853_0000.gif?ex=6a685191&is=6a670011&hm=832b3f6bf1e256982b0dbbd7fa8281278b2a533726cbfaada976a6673bffbb81"
URL_HORTON = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192061502689280/CIUDAD_20260727_002438_0000.gif?ex=6a68513b&is=6a66ffbb&hm=4456b6abef72efa13b52de84e80590589badb480923ddd52c9996829032a3868"
URL_BROOKMERE = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192290465415188/CIUDAD_20260727_002733_0000.gif?ex=6a685172&is=6a66fff2&hm=02e727a19459e9f1bfa13f001214b6270e4ecbcde608e7ad35bee717d2582a71"
URL_1VIA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192775813500968/DISTRICT_99_20260727_004421_0000.gif?ex=6a6851e5&is=6a670065&hm=2a1675b2b3a494012932aaa3f23116efcfbbd9e2671e2907255ec84dedbb12f7"
URL_2VIAS = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192488964915280/DISTRICT_99_20260727_003731_0000.gif?ex=6a6851a1&is=6a670021&hm=9a1eeff6b027a816bd60b81b0cb2742f83d8ba8a40ea788c1ecb19baa787c624"

# ==================== URLS DE IMÁGENES DE SESIÓN (NUEVAS) ====================
URL_SESION_ABIERTA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531365771786059846/District_99_20260727_121958_0000.gif"
URL_SESION_CERRADA_NUEVA = "https://cdn.discordapp.com/attachments/1530830726939934933/1531366374318805285/District_99_20260727_120442_0000.gif"

# ==================== CONFIGURACIÓN DE CANALES ====================
CANAL_PAGOS_ID = 1529957306198917200
CANAL_CREAR_LICENCIAS_ID = 1530408543784669256
CANAL_REGISTRO_LICENCIAS_ID = 1530408361802334341
CANAL_LOGS_ID = 1530830726939934933
CANAL_ANUNCIOS_ID = 1524525824869666856
CANAL_GENERAL_ID = 1524200579297972336
CANAL_SESIONES_ID = 1525377180622786701

# ==================== ROLES ====================
ROL_HOST_NOMBRE = "Host│🎮"
ROL_POLICIA_NOMBRE = "Wsp│👮"
ROL_DNI_NOMBRE = "Dni│🪪"
ROL_LICENCIA_NOMBRE = "Licencia│🚗"

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

# ==================== FUNCIÓN PARA LOGS ====================
async def enviar_log(mensaje, color=discord.Color.blue(), mencionar=None):
    canal = bot.get_channel(CANAL_LOGS_ID)
    if canal:
        embed = discord.Embed(
            description=mensaje,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        content = f"<@{mencionar}>" if mencionar else None
        await canal.send(content=content, embed=embed)
    else:
        print(f"❌ No se encontró el canal de logs (ID: {CANAL_LOGS_ID})")
      # ==================== BOT ====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Crear archivos
ARCHIVOS_JSON = [DNI_FILE, ESCENAS_FILE, EVALUACIONES_FILE, VOTACIONES_FILE, AUTOS_FILE, MULTAS_FILE, LICENCIAS_FILE, TURNOS_FILE]
for archivo in ARCHIVOS_JSON:
    if not os.path.exists(archivo):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump({}, f)
        print(f"✅ Creado: {archivo}")

# ==================== TAREAS PROGRAMADAS ====================
@tasks.loop(hours=24)
async def recordatorio_multas():
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    
    usuarios_multas = {}
    for multa in historial:
        if not multa.get('pagada', False):
            user_id = multa.get('infractor_id')
            if user_id:
                if user_id not in usuarios_multas:
                    usuarios_multas[user_id] = []
                usuarios_multas[user_id].append(multa)
    
    for user_id, multas_user in usuarios_multas.items():
        try:
            user = await bot.fetch_user(int(user_id))
            if user:
                total = sum(m.get('precio', 0) for m in multas_user)
                embed = discord.Embed(
                    title="📢 **RECORDATORIO DE MULTAS**",
                    description=f"Tienes {len(multas_user)} multas sin pagar.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="💸 **Total adeudado**", value=f"**${total}**", inline=True)
                embed.add_field(name="📌 **Multas pendientes**", value=str(len(multas_user)), inline=True)
                embed.add_field(name="📢 **¿Cómo pagar?**", value=f"Ve a <#{CANAL_PAGOS_ID}> y escribe `!pay District 99 Bot [monto]`", inline=False)
                embed.set_thumbnail(url=LOGO_SERVIDOR)
                embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
                await user.send(embed=embed)
        except:
            pass
    
    await enviar_log(f"📢 Recordatorio de multas enviado a {len(usuarios_multas)} usuarios", discord.Color.orange())

@tasks.loop(hours=24)
async def verificar_morosidad():
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    licencias = cargar(LICENCIAS_FILE)
    
    morosos = {}
    for multa in historial:
        if not multa.get('pagada', False):
            user_id = multa.get('infractor_id')
            if user_id:
                morosos[user_id] = morosos.get(user_id, 0) + 1
    
    for user_id, count in morosos.items():
        if count >= 3 and user_id in licencias:
            del licencias[user_id]
            guardar(LICENCIAS_FILE, licencias)
            
            try:
                user = await bot.fetch_user(int(user_id))
                if user:
                    guild = bot.get_guild(1524200578291597375)
                    if guild:
                        member = guild.get_member(int(user_id))
                        if member:
                            rol = discord.utils.get(guild.roles, name=ROL_LICENCIA_NOMBRE)
                            if rol and rol in member.roles:
                                await member.remove_roles(rol)
                    
                    embed = discord.Embed(
                        title="🚨 **LICENCIA REVOCADA**",
                        description=f"**{user.name}** has perdido tu licencia de conducir.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="📌 **Motivo**", value=f"Tienes {count} multas sin pagar", inline=False)
                    embed.add_field(name="📢 **¿Cómo recuperarla?**", value="Paga todas tus multas y usa `/solicitar_licencia` de nuevo", inline=False)
                    embed.set_thumbnail(url=LOGO_SERVIDOR)
                    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
                    await user.send(embed=embed)
                    await enviar_log(f"🚨 Licencia revocada a **{user.mention}** por {count} multas sin pagar", discord.Color.red())
            except:
                pass

@tasks.loop(hours=24)
async def verificar_cumpleanos():
    hoy = datetime.now(timezone.utc)
    if hoy.month == FECHA_CREACION.month and hoy.day == FECHA_CREACION.day:
        anios = hoy.year - FECHA_CREACION.year
        canal = bot.get_channel(CANAL_ANUNCIOS_ID)
        if canal:
            embed = discord.Embed(
                title="🎉 **¡FELIZ ANIVERSARIO DISTRICT 99!**",
                description=f"Hoy cumplimos **{anios} años** de rol, multas, escenas y buenos momentos.\n\nGracias a todos los ciudadanos, policías y hosts que hacen de este servidor un lugar increíble.\n\n¡Que vengan muchos años más! 🥳🚔",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=LOGO_SERVIDOR)
            embed.set_footer(text=f"DISTRICT 99 - GVRP © 2026")
            await canal.send("@everyone", embed=embed)

@tasks.loop(hours=24)
async def mensaje_buenos_dias():
    ahora = datetime.now(timezone.utc)
    hora_local = ahora - timedelta(hours=6)
    if hora_local.hour == 8 and hora_local.minute == 0:
        canal = bot.get_channel(CANAL_GENERAL_ID)
        if canal:
            embed = discord.Embed(
                title="🌅 **¡Buenos días, ciudadanos de DISTRICT 99!**",
                description="Un nuevo día comienza en la ciudad. Recuerden respetar las normas de tránsito y disfrutar del rol.",
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url=LOGO_SERVIDOR)
            embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
            await canal.send(embed=embed)
          # ==================== EVENTO ON_READY ====================
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
        print(f"   🔹 Licencia: {ROL_LICENCIA_NOMBRE}")
        print(f"✅ Canales configurados:")
        print(f"   🔹 Pagos: {CANAL_PAGOS_ID}")
        print(f"   🔹 Crear Licencias: {CANAL_CREAR_LICENCIAS_ID}")
        print(f"   🔹 Registro Licencias: {CANAL_REGISTRO_LICENCIAS_ID}")
        print(f"   🔹 Logs: {CANAL_LOGS_ID}")
        print(f"   🔹 Anuncios: {CANAL_ANUNCIOS_ID}")
        print(f"   🔹 General: {CANAL_GENERAL_ID}")
        print(f"   🔹 Sesiones: {CANAL_SESIONES_ID}")
        
        if not recordatorio_multas.is_running():
            recordatorio_multas.start()
        if not verificar_morosidad.is_running():
            verificar_morosidad.start()
        if not verificar_cumpleanos.is_running():
            verificar_cumpleanos.start()
        if not mensaje_buenos_dias.is_running():
            mensaje_buenos_dias.start()
        
        print("✅ Tareas programadas iniciadas")
        await enviar_log("✅ Bot iniciado correctamente", discord.Color.green())
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
        title="🪪 **DNI CREADO**",
        description=f"{interaction.user.mention} tu DNI ha sido creado exitosamente.",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 **Nombre**", value=nombre, inline=True)
    embed.add_field(name="👥 **Apellidos**", value=apellidos, inline=True)
    embed.add_field(name="🎂 **Edad**", value=str(edad), inline=True)
    embed.add_field(name="📅 **Nacimiento**", value=fecha_nacimiento, inline=True)
    embed.add_field(name="🔢 **Número DNI**", value=numero_dni, inline=True)
    embed.add_field(name="📆 **Expedición**", value=dnis[user_id]["fecha_expedicion"], inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"DNI registrado en {NOMBRE_SERVIDOR}")
    
    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_DNI_NOMBRE)
        if rol:
            if interaction.guild.me.guild_permissions.manage_roles:
                await interaction.user.add_roles(rol)
                embed.add_field(name="✅ **Rol**", value=f"Rol {ROL_DNI_NOMBRE} asignado", inline=False)
            else:
                embed.add_field(name="⚠️ **Rol**", value="No tengo permisos para asignar el rol", inline=False)
        else:
            embed.add_field(name="⚠️ **Rol**", value=f"No encontré el rol '{ROL_DNI_NOMBRE}'", inline=False)
    except Exception as e:
        embed.add_field(name="⚠️ **Rol**", value=f"Error al asignar: {e}", inline=False)
    
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🪪 **{interaction.user.mention}** creó su DNI (Nº {numero_dni})", discord.Color.green())

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
        title=f"🪪 **DNI DE {objetivo.name.upper()}**",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 **Nombre**", value=datos["nombre"], inline=True)
    embed.add_field(name="👥 **Apellidos**", value=datos["apellidos"], inline=True)
    embed.add_field(name="🎂 **Edad**", value=str(datos["edad"]), inline=True)
    embed.add_field(name="📅 **Nacimiento**", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="🔢 **Número DNI**", value=datos["numero_dni"], inline=True)
    embed.add_field(name="📆 **Expedición**", value=datos.get("fecha_expedicion", "Desconocida"), inline=True)
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
    await enviar_log(f"🗑️ **{interaction.user.mention}** eliminó su DNI", discord.Color.red())
  # ==================== SESIONES (COMANDO CON IMÁGENES) ====================
@bot.tree.command(name="abrir_sesion", description="🎬 Abrir sesión - SOLO HOSTS")
@app_commands.describe(
    ciudad="Elige la ciudad",
    vias="Número de vías (1 o 2)",
    velocidad_maxima="Límite de velocidad (mph)",
    adelantamientos="¿Se permiten adelantamientos?",
    link="Link del servidor"
)
@app_commands.choices(
    ciudad=[
        app_commands.Choice(name="🌆 Greenville", value="greenville"),
        app_commands.Choice(name="🌆 Horton", value="horton"),
        app_commands.Choice(name="🌆 Brookmere", value="brookmere"),
    ],
    vias=[
        app_commands.Choice(name="1 Vía", value="1"),
        app_commands.Choice(name="2 Vías", value="2"),
    ],
    adelantamientos=[
        app_commands.Choice(name="✅ Sí", value="si"),
        app_commands.Choice(name="❌ No", value="no"),
    ]
)
async def abrir_sesion(
    interaction: discord.Interaction,
    ciudad: app_commands.Choice[str],
    vias: app_commands.Choice[str],
    velocidad_maxima: str,
    adelantamientos: app_commands.Choice[str],
    link: str
):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo **HOSTS** pueden usar este comando.", ephemeral=True)
        return

    if not velocidad_maxima.isdigit():
        await interaction.response.send_message("⚠️ La velocidad debe ser un número.", ephemeral=True)
        return

    velocidad_adelanto = None
    if adelantamientos.value == "si":
        class AdelantoModal(discord.ui.Modal, title="🚀 Velocidad de Adelantamiento"):
            velocidad_adelanto = discord.ui.TextInput(
                label="Velocidad de Adelantamiento (mph)",
                placeholder="Ej: 100",
                required=True,
                max_length=10
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                if not self.velocidad_adelanto.value.isdigit():
                    await modal_interaction.response.send_message("⚠️ La velocidad de adelantamiento debe ser un número.", ephemeral=True)
                    return

                await enviar_sesion(
                    modal_interaction,
                    ciudad=ciudad.value,
                    vias=vias.value,
                    velocidad_maxima=velocidad_maxima,
                    adelantamientos=adelantamientos.value,
                    link=link,
                    velocidad_adelanto=self.velocidad_adelanto.value
                )

        await interaction.response.send_modal(AdelantoModal())
        return

    await enviar_sesion(
        interaction,
        ciudad=ciudad.value,
        vias=vias.value,
        velocidad_maxima=velocidad_maxima,
        adelantamientos=adelantamientos.value,
        link=link,
        velocidad_adelanto=None
    )

async def enviar_sesion(
    interaction: discord.Interaction,
    ciudad: str,
    vias: str,
    velocidad_maxima: str,
    adelantamientos: str,
    link: str,
    velocidad_adelanto: str = None
):
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id in escenas:
        await interaction.response.send_message("⚠️ Ya hay una sesión abierta en este canal.", ephemeral=True)
        return
    
    escenas[channel_id] = {
        "ciudad": ciudad,
        "vias": vias,
        "velocidad_maxima": velocidad_maxima,
        "adelantamientos": adelantamientos == "si",
        "velocidad_adelanto": velocidad_adelanto if velocidad_adelanto else "No aplica",
        "link_servidor": link,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🏁 **SESIÓN ABIERTA**",
        description=f"**{NOMBRE_SERVIDOR}**",
        color=discord.Color.gold()
    )
    
    embed.set_image(url=URL_SESION_ABIERTA)

    adelanto_texto = "✅ Permitidos" if adelantamientos == "si" else "❌ No permitidos"
    
    detalles = (
        f"🌆 **Ciudad:** {ciudad.capitalize()}\n"
        f"🛣️ **Vías:** {vias} vías\n"
        f"🚗 **Velocidad Máx:** {velocidad_maxima} mph\n"
        f"🏁 **Adelantamientos:** {adelanto_texto}\n"
    )
    
    if adelantamientos == "si" and velocidad_adelanto:
        detalles += f"🚀 **Vel. Adelanto:** {velocidad_adelanto} mph\n"
    
    detalles += (
        f"👑 **Host:** {interaction.user.mention}\n"
        f"🔗 **Link:** [🌐 Haz clic aquí]({link})"
    )
    
    embed.add_field(
        name="📋 **DETALLES**",
        value=detalles,
        inline=False
    )
    embed.set_footer(
        text=f"Sesión iniciada por {interaction.user.name} • {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}",
        icon_url=interaction.user.display_avatar.url
    )

    canal_sesiones = bot.get_channel(CANAL_SESIONES_ID)
    if canal_sesiones:
        await canal_sesiones.send(embed=embed)
        await interaction.response.send_message("✅ ¡Sesión enviada al canal de sesiones!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No encontré el canal de sesiones.", ephemeral=True)

    await enviar_log(f"🎬 **{interaction.user.mention}** abrió sesión (Ciudad: {ciudad.capitalize()}, Vías: {vias})", discord.Color.gold())

@bot.tree.command(name="cerrar_sesion", description="🔒 Cerrar sesión - SOLO HOSTS")
async def cerrar_sesion(interaction: discord.Interaction):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo **HOSTS** pueden usar este comando.", ephemeral=True)
        return

    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    
    if channel_id not in escenas:
        await interaction.response.send_message("❌ No hay una sesión activa en este canal.", ephemeral=True)
        return

    escena = escenas[channel_id]
    inicio = datetime.fromisoformat(escena["inicio"])
    duracion = datetime.now(timezone.utc) - inicio
    horas, resto = divmod(int(duracion.total_seconds()), 3600)
    minutos = resto // 60

    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🔒 **SESIÓN CERRADA**",
        description=f"**¡Buen rol!** 👏\n⏱️ Duración: {horas}h {minutos}m",
        color=discord.Color.red()
    )
    embed.set_image(url=URL_SESION_CERRADA_NUEVA)
    embed.set_footer(
        text=f"Sesión cerrada por {interaction.user.name} • {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}",
        icon_url=interaction.user.display_avatar.url
    )

    canal_sesiones = bot.get_channel(CANAL_SESIONES_ID)
    if canal_sesiones:
        await canal_sesiones.send(embed=embed)
        await interaction.response.send_message("✅ ¡Sesión cerrada!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No encontré el canal de sesiones.", ephemeral=True)

    await enviar_log(f"🔒 **{interaction.user.mention}** cerró sesión (Duración: {horas}h {minutos}m)", discord.Color.red())
  # ==================== VOTACIONES (SIN MINIATURA) ====================
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
            title="🗳️ **VOTACIÓN**",
            description=f"✅ Asistirán: {len(asist)}/{votacion['votos_requeridos']}\n❌ No asistirán: {len(no_asist)}",
            color=discord.Color.orange()
        )
        embed.add_field(name="✅", value="\n".join(f"<@{u}>" for u in asist) or "Nadie", inline=False)
        embed.add_field(name="❌", value="\n".join(f"<@{u}>" for u in no_asist) or "Nadie", inline=False)
        embed.set_image(url=URL_VOTACION_ABIERTA)  # ✅ SOLO IMAGEN PRINCIPAL, SIN MINIATURA
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        if len(asist) == votacion["votos_requeridos"]:
            await interaction.channel.send(f"🎉 <@{votacion['host_id']}> ¡Meta alcanzada! Abre con `/abrir_sesion`")

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
        title="🗳️ **¿ABRIMOS SESIÓN?**",
        description=f"Necesitan {votos_requeridos} votos",
        color=discord.Color.orange()
    )
    embed.add_field(name="✅ **Asistentes**", value="Nadie", inline=False)
    embed.add_field(name="❌ **No asistentes**", value="Nadie", inline=False)
    embed.set_image(url=URL_VOTACION_ABIERTA)  # ✅ SOLO IMAGEN PRINCIPAL, SIN MINIATURA
    embed.set_footer(text=f"Host: {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed, view=VotoView(interaction.channel_id))
    await enviar_log(f"🗳️ **{interaction.user.mention}** creó votación (Meta: {votos_requeridos} votos)", discord.Color.orange())

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
    
    embed = discord.Embed(
        title="🔒 **VOTACIÓN CERRADA**",
        description=f"**Votación finalizada.**",
        color=discord.Color.red()
    )
    embed.set_image(url=URL_VOTACION_CERRADA)  # ✅ SOLO IMAGEN PRINCIPAL, SIN MINIATURA
    embed.set_footer(text=f"Cerrada por {interaction.user.name} • {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🔒 **{interaction.user.mention}** cerró votación", discord.Color.red())

# ==================== AUTOS (SIN MINIATURA) ====================
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
    autos = cargar(AUTOS_FILE)
    user_id = str(interaction.user.id)
    
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
        title="🚗 **VEHÍCULO REGISTRADO**",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 **Usuario Discord**", value=interaction.user.mention, inline=False)
    embed.add_field(name="🎮 **Usuario Roblox**", value=usuario_roblox, inline=False)
    embed.add_field(name="📋 **Modelo**", value=modelo, inline=True)
    embed.add_field(name="🎨 **Color**", value=color, inline=True)
    embed.add_field(name="🅿️ **Placa**", value=placa, inline=True)
    embed.set_image(url=foto.url)  # ✅ SOLO IMAGEN PRINCIPAL, SIN MINIATURA
    embed.set_footer(text=f"Registrado por {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🚗 **{interaction.user.mention}** registró un vehículo (Placa: {placa}, Modelo: {modelo})", discord.Color.green())

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
        title=f"🚗 **AUTOS DE {objetivo.name.upper()}**",
        color=discord.Color.blue()
    )
    
    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"🚘 **Auto #{i}**",
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
            embed.set_image(url=auto['foto'])  # ✅ SOLO IMAGEN PRINCIPAL, SIN MINIATURA
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_auto", description="🗑️ Eliminar un auto registrado")
@app_commands.describe(
    numero_auto="Número del auto a eliminar (1, 2, 3...)"
)
async def eliminar_auto(interaction: discord.Interaction, numero_auto: int):
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
        title="🗑️ **AUTO ELIMINADO**",
        description=f"{interaction.user.mention} has eliminado tu auto.",
        color=discord.Color.red()
    )
    embed.add_field(name="📋 **Modelo**", value=auto_eliminado.get('modelo', 'Desconocido'), inline=True)
    embed.add_field(name="🅿️ **Placa**", value=auto_eliminado.get('placa', 'Desconocida'), inline=True)
    embed.add_field(name="🎨 **Color**", value=auto_eliminado.get('color', 'Desconocido'), inline=True)
    embed.set_footer(text=f"Auto eliminado el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🗑️ **{interaction.user.mention}** eliminó un vehículo (Placa: {auto_eliminado.get('placa', 'N/A')})", discord.Color.red())
  # ==================== MULTAS ====================
@bot.tree.command(name="registrar_multa", description="🚨 Registrar multa - SOLO POLICIA")
@app_commands.describe(
    infractor="Usuario infractor",
    infraccion="Infraccion cometida",
    precio="Monto de la multa ($)",
    testigos="Testigos de la infracción (opcional - menciona a los usuarios)",
    foto="Foto de la evidencia (opcional - adjunta una imagen)"
)
async def registrar_multa(
    interaction: discord.Interaction,
    infractor: discord.Member,
    infraccion: str,
    precio: str,
    testigos: str = None,
    foto: discord.Attachment = None
):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICIA pueden usar este comando", ephemeral=True)
        return
    
    if not precio.isdigit():
        await interaction.response.send_message("⚠️ Monto: numero", ephemeral=True)
        return
    
    testigos_mentions = []
    if testigos:
        mentions = re.findall(r'<@!?(\d+)>', testigos)
        for user_id in mentions:
            try:
                user = await bot.fetch_user(int(user_id))
                testigos_mentions.append(user.mention)
            except:
                pass
    
    multas = cargar(MULTAS_FILE)
    multas.setdefault("historial", []).append({
        "oficial_id": str(interaction.user.id),
        "oficial": str(interaction.user),
        "infractor_id": str(infractor.id),
        "infractor": str(infractor),
        "infraccion": infraccion,
        "precio": int(precio),
        "pagada": False,
        "testigos": testigos_mentions,
        "foto": foto.url if foto else None,
        "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
    })
    guardar(MULTAS_FILE, multas)
    
    embed = discord.Embed(
        title="🚨 **MULTA REGISTRADA**",
        color=discord.Color.red()
    )
    embed.add_field(name="👮 **Oficial**", value=interaction.user.mention, inline=False)
    embed.add_field(name="👤 **Infractor**", value=infractor.mention, inline=False)
    embed.add_field(name="⚖️ **Infracción**", value=infraccion, inline=False)
    embed.add_field(name="💰 **Monto**", value=f"**${precio}**", inline=True)
    if testigos_mentions:
        embed.add_field(name="👀 **Testigos**", value=", ".join(testigos_mentions), inline=False)
    embed.add_field(name="📌 **Estado**", value="❌ Sin pagar", inline=True)
    if foto:
        embed.set_image(url=foto.url)
    else:
        embed.set_image(url=URL_MULTA)
    embed.set_footer(text=f"Registrada el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    mensaje = f"{infractor.mention} ¡Has recibido una multa!\n"
    mensaje += f"📢 **Para pagar:** Ve a <#{CANAL_PAGOS_ID}> y escribe `!pay District 99 Bot {precio}`"
    
    if testigos_mentions:
        mensaje += f"\n👀 **Testigos:** {', '.join(testigos_mentions)}"
    
    await interaction.response.send_message(content=mensaje, embed=embed)
    await enviar_log(f"🚨 **{interaction.user.mention}** multó a **{infractor.mention}** por ${precio} (Infracción: {infraccion})", discord.Color.red())
    
    historial = multas.get("historial", [])
    multas_usuario = [m for m in historial if m.get('infractor_id') == str(infractor.id) and not m.get('pagada', False)]
    if len(multas_usuario) >= 3:
        licencias = cargar(LICENCIAS_FILE)
        if str(infractor.id) in licencias:
            del licencias[str(infractor.id)]
            guardar(LICENCIAS_FILE, licencias)
            
            try:
                rol = discord.utils.get(interaction.guild.roles, name=ROL_LICENCIA_NOMBRE)
                if rol and rol in infractor.roles:
                    await infractor.remove_roles(rol)
            except:
                pass
            
            await interaction.channel.send(
                f"🚨 **{infractor.mention}** ha perdido su licencia por acumular {len(multas_usuario)} multas sin pagar.\n"
                f"📢 Para recuperarla, paga todas tus multas y usa `/solicitar_licencia` de nuevo."
            )
            await enviar_log(f"🚨 Licencia revocada a **{infractor.mention}** por {len(multas_usuario)} multas sin pagar", discord.Color.red())

# ==================== HISTORIAL MULTAS ====================
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
        titulo = f"🚨 **MULTAS DE {usuario.name.upper()}**"
    else:
        titulo = "🚨 **HISTORIAL DE MULTAS (TODOS)**"
    
    embed = discord.Embed(title=titulo, color=discord.Color.red())
    
    for i, multa in enumerate(historial[-10:], 1):
        estado = "✅ Pagada" if multa.get('pagada', False) else "❌ Sin pagar"
        testigos = multa.get('testigos', [])
        testigos_texto = ", ".join(testigos) if testigos else "Ninguno"
        embed.add_field(
            name=f"📌 **Multa #{i}**",
            value=(
                f"👮 **Oficial:** {multa['oficial']}\n"
                f"👤 **Infractor:** {multa['infractor']}\n"
                f"⚖️ **Infracción:** {multa['infraccion']}\n"
                f"💰 **Monto:** ${multa['precio']}\n"
                f"👀 **Testigos:** {testigos_texto}\n"
                f"📌 **Estado:** {estado}\n"
                f"📅 **Fecha:** {multa['fecha']}"
            ),
            inline=False
        )
        if multa.get('foto'):
            embed.set_image(url=multa['foto'])
    
    embed.set_footer(text="Mostrando últimas 10 multas")
    await interaction.response.send_message(embed=embed)

# ==================== MIS MULTAS ====================
@bot.tree.command(name="mis_multas", description="📋 Ver tu historial de multas")
async def mis_multas(interaction: discord.Interaction):
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    user_id = str(interaction.user.id)
    
    mis_multas = [m for m in historial if m.get('infractor_id') == user_id]
    
    if not mis_multas:
        await interaction.response.send_message("📋 No tienes multas registradas", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🚨 **TUS MULTAS**",
        description=f"Total: {len(mis_multas)} multas",
        color=discord.Color.orange()
    )
    
    total = 0
    for i, multa in enumerate(mis_multas[-10:], 1):
        total += multa.get('precio', 0)
        estado = "✅ Pagada" if multa.get('pagada', False) else "❌ Sin pagar"
        testigos = multa.get('testigos', [])
        testigos_texto = ", ".join(testigos) if testigos else "Ninguno"
        embed.add_field(
            name=f"📌 **Multa #{i}**",
            value=(
                f"👮 **Oficial:** {multa['oficial']}\n"
                f"⚖️ **Infracción:** {multa['infraccion']}\n"
                f"💰 **Monto:** ${multa['precio']}\n"
                f"👀 **Testigos:** {testigos_texto}\n"
                f"📌 **Estado:** {estado}\n"
                f"📅 **Fecha:** {multa['fecha']}"
            ),
            inline=False
        )
        if multa.get('foto'):
            embed.set_image(url=multa['foto'])
    
    embed.add_field(name="💸 **TOTAL ADEUDADO**", value=f"**${total}**", inline=False)
    embed.set_footer(text="Mostrando últimas 10 multas")
    
    await interaction.response.send_message(embed=embed)

# ==================== CONFIRMAR PAGO ====================
@bot.tree.command(name="confirmar_pago", description="👮 Confirmar pago de un ciudadano - SOLO POLICIA")
@app_commands.describe(
    usuario="Usuario que pagó (menciona o escribe el nombre)",
    monto="Monto que pagó"
)
async def confirmar_pago(
    interaction: discord.Interaction,
    usuario: str,
    monto: int
):
    if not es_policia(interaction.user):
        await interaction.response.send_message("⛔ Solo POLICIA pueden usar este comando", ephemeral=True)
        return

    miembro = None
    
    if usuario.startswith('<@') and usuario.endswith('>'):
        user_id = usuario.replace('<@', '').replace('>', '').replace('!', '')
        miembro = interaction.guild.get_member(int(user_id))
    
    if not miembro:
        for member in interaction.guild.members:
            if member.name.lower() == usuario.lower() or member.display_name.lower() == usuario.lower():
                miembro = member
                break
            if member.nick and member.nick.lower() == usuario.lower():
                miembro = member
                break

    if not miembro:
        await interaction.response.send_message(f"⚠️ No encontré al usuario `{usuario}`. Usa el nombre exacto (sin punto) o la mención.", ephemeral=True)
        return

    user_id = str(miembro.id)
    user_mention = miembro.mention

    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])

    multa_encontrada = False
    oficial_id = None
    infraccion = None
    foto_url = None

    for i, multa in enumerate(historial):
        if multa.get('infractor_id') == user_id and not multa.get('pagada', False) and multa.get('precio') == monto:
            historial[i]['pagada'] = True
            historial[i]['fecha_pago'] = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
            multa_encontrada = True
            oficial_id = multa.get('oficial_id')
            infraccion = multa.get('infraccion')
            foto_url = multa.get('foto')
            break

    if not multa_encontrada:
        await interaction.response.send_message(f"⚠️ No encontré una multa de **${monto}** para {user_mention}", ephemeral=True)
        return

    guardar(MULTAS_FILE, multas)

    embed = discord.Embed(
        title="💰 **PAGO CONFIRMADO POR OFICIAL**",
        description=f"{user_mention} ha pagado su multa.",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 **Monto**", value=f"**${monto}**", inline=True)
    embed.add_field(name="⚖️ **Infracción**", value=infraccion, inline=True)
    embed.add_field(name="👮 **Confirmado por**", value=interaction.user.mention, inline=True)
    embed.add_field(name="📅 **Fecha de pago**", value=datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"), inline=True)
    if foto_url:
        embed.set_image(url=foto_url)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")

    await interaction.response.send_message(embed=embed)

    await interaction.channel.send(
        f"{user_mention} ✅ Tu pago de **${monto}** ha sido confirmado por {interaction.user.mention}."
    )

    await enviar_log(f"💰 **{user_mention}** pagó su multa de ${monto} (Confirmado por {interaction.user.mention})", discord.Color.green())

# ==================== EVALUAR STAFF ====================
class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
    que_hizo = discord.ui.TextInput(
        label="¿Qué hizo el staff?",
        placeholder="Ej: Ayudó con el rol, fue muy atento...",
        max_length=200
    )
    calificacion = discord.ui.TextInput(
        label="Calificación (1-10)",
        placeholder="Ej: 8",
        max_length=2
    )
    amable = discord.ui.TextInput(
        label="¿Fue amable?",
        placeholder="Ej: Sí, muy amable",
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
            await interaction.response.send_message("⚠️ Calificación inválida. Usa un número del 1 al 10", ephemeral=True)
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
            title="📝 **EVALUACIÓN REGISTRADA**",
            description=f"**Staff evaluado:** {self.staff.mention}",
            color=discord.Color.purple()
        )
        embed.add_field(name="⭐ **Calificación**", value=f"{estrellas} ({nota}/10)", inline=False)
        embed.add_field(name="🤝 **Amabilidad**", value=self.amable.value, inline=False)
        embed.add_field(name="📌 **Acción**", value=self.que_hizo.value, inline=False)
        embed.add_field(name="💬 **Sugerencias**", value=self.queja.value or "Ninguna", inline=False)
        embed.set_footer(text=f"Evaluado por {interaction.user.name}")
        
        await interaction.response.send_message(
            content=f"{self.staff.mention} ¡Has recibido una evaluación! ⭐",
            embed=embed
        )
        await enviar_log(f"⭐ **{interaction.user.mention}** evaluó a **{self.staff.mention}** con nota {nota}/10", discord.Color.purple())

@bot.tree.command(name="evaluar_staff", description="⭐ Evaluar al staff")
@app_commands.describe(staff="Staff a evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvalModal(staff))
    # ==================== PANEL DE LICENCIAS (CORREGIDO) ====================
class PanelLicenciasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Crear Licencia", style=discord.ButtonStyle.success, custom_id="crear_licencia")
    async def crear_licencia(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel.id != CANAL_CREAR_LICENCIAS_ID:
            await interaction.response.send_message(f"⚠️ Este panel solo funciona en <#{CANAL_CREAR_LICENCIAS_ID}>", ephemeral=True)
            return

        class LicenciaModal(discord.ui.Modal, title="📝 Solicitar Licencia"):
            nombre = discord.ui.TextInput(label="Nombre", placeholder="Ej: Juan", max_length=50, required=True)
            apellidos = discord.ui.TextInput(label="Apellidos", placeholder="Ej: Pérez García", max_length=50, required=True)
            edad = discord.ui.TextInput(label="Edad", placeholder="Ej: 25", max_length=3, required=True)
            oficio = discord.ui.TextInput(label="Oficio", placeholder="Ej: Conductor", max_length=50, required=True)
            user_roblox = discord.ui.TextInput(label="User de Roblox", placeholder="Ej: Juanito_99", max_length=50, required=True)

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    licencias = cargar(LICENCIAS_FILE)
                    user_id = str(modal_interaction.user.id)
                    
                    if user_id in licencias:
                        await modal_interaction.response.send_message("⚠️ Ya tienes una licencia activa.", ephemeral=True)
                        return

                    dnis = cargar(DNI_FILE)
                    if user_id not in dnis:
                        await modal_interaction.response.send_message("⚠️ Necesitas tener un DNI antes de solicitar licencia. Usa `/crear_dni`", ephemeral=True)
                        return

                    num_licencia = len(licencias) + 1
                    licencia_id = f"LIC-2026-{num_licencia:04d}"

                    datos_licencia = {
                        "nombre": self.nombre.value,
                        "apellidos": self.apellidos.value,
                        "edad": self.edad.value,
                        "oficio": self.oficio.value,
                        "user_roblox": self.user_roblox.value,
                        "user_discord": str(modal_interaction.user),
                        "dni": dnis[user_id]["numero_dni"],
                        "fecha_nacimiento": dnis[user_id]["fecha_nacimiento"],
                        "licencia_id": licencia_id,
                        "fecha_expedicion": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
                        "fecha_expiracion": (datetime.now(timezone.utc) + timedelta(days=730)).strftime("%d/%m/%Y"),
                        "estado": "Activa"
                    }
                    licencias[user_id] = datos_licencia
                    guardar(LICENCIAS_FILE, licencias)

                    try:
                        rol = discord.utils.get(modal_interaction.guild.roles, name=ROL_LICENCIA_NOMBRE)
                        if rol:
                            await modal_interaction.user.add_roles(rol)
                    except:
                        pass

                    # Generar la imagen de la licencia
                    archivo_licencia = await generar_licencia(modal_interaction.user, datos_licencia)
                    if archivo_licencia is None:
                        await modal_interaction.response.send_message("❌ Error al generar la imagen de la licencia.", ephemeral=True)
                        return

                    # Crear embed con la imagen generada
                    embed = discord.Embed(
                        title="🪪 **LICENCIA GENERADA**",
                        description=f"{modal_interaction.user.mention}",
                        color=discord.Color.gold()
                    )
                    embed.set_image(url="attachment://licencia.png")
                    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")

                    canal_registro = bot.get_channel(CANAL_REGISTRO_LICENCIAS_ID)
                    if canal_registro:
                        await canal_registro.send(
                            content=f"📢 **Nueva licencia generada para {modal_interaction.user.mention}**",
                            embed=embed,
                            file=archivo_licencia
                        )
                        await modal_interaction.response.send_message("✅ **¡Licencia creada exitosamente!**", ephemeral=True)
                    else:
                        await modal_interaction.response.send_message("❌ No se encontró el canal de registro de licencias.", ephemeral=True)

                    await enviar_log(f"🪪 **{modal_interaction.user.mention}** creó su licencia (Nº {licencia_id})", discord.Color.gold())

                except Exception as e:
                    print(f"❌ Error en el panel de licencias: {e}")
                    await modal_interaction.response.send_message(f"❌ Error al crear la licencia: {e}", ephemeral=True)

        await interaction.response.send_modal(LicenciaModal())

@bot.tree.command(name="panel_licencias", description="📋 Panel para solicitar licencias - SOLO ADMIN/HOST")
async def panel_licencias(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    if interaction.channel.id != CANAL_CREAR_LICENCIAS_ID:
        await interaction.response.send_message(f"⚠️ Este comando solo funciona en <#{CANAL_CREAR_LICENCIAS_ID}>", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📋 **PANEL DE LICENCIAS**",
        description=(
            "Presiona el botón para completar tus datos y generar tu licencia de conducir de **DISTRICT 99 - GVRP**.\n\n"
            "📌 **Datos solicitados:**\n"
            "• Nombre\n"
            "• Apellidos\n"
            "• Edad\n"
            "• Oficio\n"
            "• User de Roblox\n\n"
            "⚠️ **Requisitos:**\n"
            "• Debes tener un DNI creado (`/crear_dni`)\n\n"
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    
    view = PanelLicenciasView()
    await interaction.response.send_message(embed=embed, view=view)

# ==================== VER LICENCIA ====================
@bot.tree.command(name="ver_licencia", description="🪪 Ver la licencia de un usuario")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_licencia(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    licencias = cargar(LICENCIAS_FILE)
    datos = licencias.get(str(objetivo.id))
    
    if not datos:
        await interaction.response.send_message(f"❌ {objetivo.mention} no tiene licencia.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🪪 **LICENCIA DE CONDUCIR**",
        description=f"{objetivo.mention}",
        color=discord.Color.gold()
    )
    embed.add_field(name="📋 **Licencia**", value=datos.get("licencia_id", "N/A"), inline=False)
    embed.add_field(name="👤 **Nombre**", value=datos.get("nombre", "N/A"), inline=True)
    embed.add_field(name="👥 **Apellidos**", value=datos.get("apellidos", "N/A"), inline=True)
    embed.add_field(name="🎂 **Edad**", value=datos.get("edad", "N/A"), inline=True)
    embed.add_field(name="💼 **Oficio**", value=datos.get("oficio", "N/A"), inline=True)
    embed.add_field(name="🎮 **Roblox**", value=datos.get("user_roblox", "N/A"), inline=True)
    embed.add_field(name="🔢 **DNI**", value=datos.get("dni", "N/A"), inline=True)
    embed.add_field(name="📅 **Expedición**", value=datos.get("fecha_expedicion", "N/A"), inline=True)
    embed.add_field(name="📅 **Expiración**", value=datos.get("fecha_expiracion", "N/A"), inline=True)
    embed.add_field(name="📌 **Estado**", value="🟢 ACTIVA", inline=True)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    await interaction.response.send_message(embed=embed)

# ==================== ELIMINAR LICENCIA ====================
@bot.tree.command(name="eliminar_licencia", description="🗑️ Eliminar licencia de un usuario - SOLO ADMIN/HOST")
@app_commands.describe(
    usuario="Usuario a eliminar licencia",
    motivo="Motivo de la eliminación (opcional)"
)
async def eliminar_licencia(
    interaction: discord.Interaction,
    usuario: discord.Member,
    motivo: str = None
):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    licencias = cargar(LICENCIAS_FILE)
    user_id = str(usuario.id)
    
    if user_id not in licencias:
        await interaction.response.send_message(f"❌ {usuario.mention} no tiene licencia activa.", ephemeral=True)
        return
    
    datos_licencia = licencias[user_id]
    licencia_id = datos_licencia.get("licencia_id", "N/A")
    nombre = datos_licencia.get("nombre", "N/A")
    apellidos = datos_licencia.get("apellidos", "N/A")
    
    del licencias[user_id]
    guardar(LICENCIAS_FILE, licencias)
    
    try:
        rol = discord.utils.get(interaction.guild.roles, name=ROL_LICENCIA_NOMBRE)
        if rol and rol in usuario.roles:
            await usuario.remove_roles(rol)
    except:
        pass
    
    embed = discord.Embed(
        title="🗑️ **LICENCIA ELIMINADA**",
        description=f"{usuario.mention} ya no tiene licencia de conducir.",
        color=discord.Color.red()
    )
    embed.add_field(name="📋 **Licencia**", value=licencia_id, inline=True)
    embed.add_field(name="👤 **Nombre**", value=f"{nombre} {apellidos}", inline=True)
    embed.add_field(name="👮 **Eliminado por**", value=interaction.user.mention, inline=False)
    if motivo:
        embed.add_field(name="📌 **Motivo**", value=motivo, inline=False)
    embed.set_footer(text=f"Eliminado el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    await interaction.response.send_message(embed=embed)
    
    canal_registro = bot.get_channel(CANAL_REGISTRO_LICENCIAS_ID)
    if canal_registro:
        await canal_registro.send(
            f"📢 **Licencia eliminada**\n"
            f"👤 Usuario: {usuario.mention}\n"
            f"📋 Licencia: {licencia_id}\n"
            f"👮 Eliminado por: {interaction.user.mention}\n"
            f"📌 Motivo: {motivo if motivo else 'No especificado'}"
        )
    
    await enviar_log(f"🗑️ **{interaction.user.mention}** eliminó la licencia de **{usuario.mention}** (Motivo: {motivo if motivo else 'No especificado'})", discord.Color.red())
  # ==================== STATS ====================
@bot.tree.command(name="stats", description="📊 Estadísticas del bot - SOLO ADMINS")
async def stats(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Admins** pueden usar este comando.", ephemeral=True)
        return
    
    dnis = cargar(DNI_FILE)
    licencias = cargar(LICENCIAS_FILE)
    multas = cargar(MULTAS_FILE)
    autos = cargar(AUTOS_FILE)
    escenas = cargar(ESCENAS_FILE)
    evaluaciones = cargar(EVALUACIONES_FILE)
    
    historial = multas.get("historial", [])
    total_multas = len(historial)
    pagadas = sum(1 for m in historial if m.get('pagada', False))
    no_pagadas = total_multas - pagadas
    
    total_autos = sum(len(v) for v in autos.values())
    
    embed = discord.Embed(
        title="📊 **ESTADÍSTICAS DEL BOT**",
        description=f"**{NOMBRE_SERVIDOR}**",
        color=discord.Color.blue()
    )
    embed.add_field(name="🪪 **DNIs creados**", value=str(len(dnis)), inline=True)
    embed.add_field(name="🪪 **Licencias activas**", value=str(len(licencias)), inline=True)
    embed.add_field(name="🚗 **Autos registrados**", value=str(total_autos), inline=True)
    embed.add_field(name="🚨 **Multas totales**", value=str(total_multas), inline=True)
    embed.add_field(name="✅ **Multas pagadas**", value=str(pagadas), inline=True)
    embed.add_field(name="❌ **Multas pendientes**", value=str(no_pagadas), inline=True)
    embed.add_field(name="🎬 **Escenas abiertas**", value=str(len(escenas)), inline=True)
    embed.add_field(name="⭐ **Evaluaciones**", value=str(len(evaluaciones)), inline=True)
    embed.set_footer(text=f"Actualizado: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"📊 **{interaction.user.mention}** usó /stats", discord.Color.blue())

# ==================== EVENTO ON_MESSAGE (DETECTAR !pay) ====================
@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    
    if message.channel.id != CANAL_PAGOS_ID:
        await bot.process_commands(message)
        return
    
    if message.content.lower().startswith("!pay"):
        partes = message.content.split()
        if len(partes) >= 2:
            monto = None
            for parte in partes:
                if parte.isdigit():
                    monto = int(parte)
                    break
            
            if monto is None:
                await bot.process_commands(message)
                return
            
            user_id = str(message.author.id)
            user_mention = message.author.mention
            user_name = message.author.name
            
            print(f"🔍 Pago detectado: {user_name} intentó pagar ${monto}")
            
            multas = cargar(MULTAS_FILE)
            historial = multas.get("historial", [])
            
            tiene_pendientes = False
            oficial_id = None
            infraccion = None
            
            for multa in historial:
                if multa.get('infractor_id') == user_id and not multa.get('pagada', False):
                    tiene_pendientes = True
                    if multa.get('precio') == monto:
                        oficial_id = multa.get('oficial_id')
                        infraccion = multa.get('infraccion')
                    break
            
            if not tiene_pendientes:
                await message.channel.send(
                    f"{user_mention} ✅ No tienes multas pendientes. ¡Estás al día!"
                )
                await bot.process_commands(message)
                return
            
            if not oficial_id:
                for multa in historial:
                    if multa.get('infractor_id') == user_id and not multa.get('pagada', False) and multa.get('precio') == monto:
                        oficial_id = multa.get('oficial_id')
                        infraccion = multa.get('infraccion')
                        break
            
            await message.channel.send(
                f"{user_mention} ✅ He detectado tu pago de **${monto}**.\n"
                f"⏳ Espera a que un oficial verifique y confirme el pago."
            )
            
            if oficial_id:
                await message.channel.send(
                    f"👮 <@{oficial_id}> El ciudadano {user_mention} dice que pagó su multa de **${monto}**.\n"
                    f"📌 **Infracción:** {infraccion}\n"
                    f"✅ Verifica en UnbelievaBoat y usa `/confirmar_pago {user_name} {monto}`"
                )
            else:
                await message.channel.send(
                    f"📢 **ATENCIÓN POLICÍAS:** {user_mention} dice que pagó **${monto}**.\n"
                    f"Verifiquen en UnbelievaBoat y usen `/confirmar_pago {user_name} {monto}`"
                )
            
            await bot.process_commands(message)
            return
    
    await bot.process_commands(message)

# ==================== INICIAR BOT ====================
print("🚀 Intentando conectar a Discord...")
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ ERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
