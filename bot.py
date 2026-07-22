"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
------------------------------------------
Funciones:
  /crear_dni       -> Crea el DNI (ficha de identidad) de tu personaje
  /ver_dni         -> Muestra tu DNI o el de otro usuario
  /eliminar_dni    -> Borra tu propio DNI
  /abrir_escena    -> Abre una sesión de rol en el canal actual
  /cerrar_escena   -> Cierra la sesión activa y menciona al host
  /evaluar_staff   -> Abre un formulario para calificar la atención de un staff
  /votacion_sesion -> Abre una votación con botones asistir/no asistir
  /cerrar_votacion -> Cierra una votación de asistencia activa

Los datos se guardan en archivos JSON locales (dnis.json, escenas.json,
evaluaciones.json, votaciones.json), así que no necesitas ninguna base de
datos externa.
"""

import json
import os
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

# Nombre que aparece en el mensaje de inicio de sesión.
NOMBRE_SERVIDOR = "DISTRICT 99"


# ---------- Utilidades para leer/guardar JSON ----------

def cargar(archivo: str) -> dict:
    if not os.path.exists(archivo):
        return {}
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar(archivo: str, data: dict) -> None:
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generar_numero_dni(user_id: str) -> str:
    # Genera un número de DNI simple y estable a partir del ID de Discord
    return f"{int(user_id) % 100000000:08d}"


# ---------- Configuración del bot ----------

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Sesión iniciada como {bot.user}. {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# ---------- Comandos de DNI ----------

@bot.tree.command(name="crear_dni", description="Crea el DNI de tu personaje de rol")
@app_commands.describe(
    nombre="Nombre del personaje",
    apellidos="Apellidos del personaje",
    fecha_nacimiento="Fecha de nacimiento del personaje (ej: 12/05/1998)",
    edad="Edad del personaje",
    ocupacion="Ocupación u oficio del personaje (opcional)",
)
async def crear_dni(
    interaction: discord.Interaction,
    nombre: str,
    apellidos: str,
    fecha_nacimiento: str,
    edad: int,
    ocupacion: str = "Sin especificar",
):
    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)

    dnis[user_id] = {
        "nombre": nombre,
        "apellidos": apellidos,
        "fecha_nacimiento": fecha_nacimiento,
        "edad": edad,
        "ocupacion": ocupacion,
        "numero_dni": generar_numero_dni(user_id),
        "fecha_expedicion": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
    }
    guardar(DNI_FILE, dnis)

    await interaction.response.send_message(
        embed=_embed_dni(interaction.user, dnis[user_id])
    )


@bot.tree.command(name="ver_dni", description="Muestra tu DNI o el de otro usuario")
@app_commands.describe(usuario="Usuario del que quieres ver el DNI (opcional)")
async def ver_dni(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    dnis = cargar(DNI_FILE)
    datos = dnis.get(str(objetivo.id))

    if not datos:
        await interaction.response.send_message(
            f"🕵️ {objetivo.mention} todavía no tiene un DNI creado. Usa `/crear_dni` para sacar el suyo.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(embed=_embed_dni(objetivo, datos))


@bot.tree.command(name="eliminar_dni", description="Elimina tu propio DNI")
async def eliminar_dni(interaction: discord.Interaction):
    dnis = cargar(DNI_FILE)
    user_id = str(interaction.user.id)

    if user_id not in dnis:
        await interaction.response.send_message("🤔 No tienes ningún DNI creado todavía.", ephemeral=True)
        return

    del dnis[user_id]
    guardar(DNI_FILE, dnis)
    await interaction.response.send_message("🗑️ Tu DNI fue eliminado correctamente.")


def _embed_dni(usuario: discord.abc.User, datos: dict) -> discord.Embed:
    embed = discord.Embed(title="📋 Documento Nacional de Identidad (RP)", color=discord.Color.blue())
    embed.set_thumbnail(url=usuario.display_avatar.url)
    embed.add_field(name="Nombre", value=datos["nombre"], inline=True)
    embed.add_field(name="Apellidos", value=datos["apellidos"], inline=True)
    embed.add_field(name="Edad", value=str(datos["edad"]), inline=True)
    embed.add_field(name="Fecha de nacimiento", value=datos["fecha_nacimiento"], inline=True)
    embed.add_field(name="Ocupación", value=datos["ocupacion"], inline=True)
    embed.add_field(name="Nº de DNI", value=datos["numero_dni"], inline=True)
    embed.set_footer(text=f"Expedido el {datos['fecha_expedicion']} · Jugador: {usuario}")
    return embed


# ---------- Comandos de sesión ----------

def _embed_sesion(escena: dict) -> discord.Embed:
    descripcion = (
        "¡Atención, ciudadanos! 🚨\n"
        "El equipo de hosts ya tiene los motores encendidos y estamos listos para "
        "arrancar con nuestra sesión de rol. 🏎️💨\n\n"
        "🔹 **Estado del servidor:** ABIERTO ✅\n\n"
        f"🔹 **Vías:** {escena['vias']}\n\n"
        f"🔹 **Adelantamiento:** {escena['adelantamiento']}\n\n"
        f"🔹 **Velocidad máxima:** {escena['velocidad_maxima']}\n\n"
        f"🔹 **User:** {escena['host']}\n\n"
        f"🔗 **Link del servidor:** {escena['link_servidor']}\n\n"
        "¡Recuerden que para participar es obligatorio tener su DNI! "
        "Los esperamos en las calles. 🏙️⚖️"
    )

    embed = discord.Embed(
        title=f"📢 | INICIO DE SESIÓN OFICIAL - {NOMBRE_SERVIDOR}",
        description=descripcion,
        color=discord.Color.gold(),
    )
    return embed


@bot.tree.command(name="abrir_escena", description="Abre una sesión de rol en este canal")
@app_commands.describe(
    vias="Estado de las vías",
    adelantamiento="Reglas de adelantamiento",
    velocidad_maxima="Velocidad máxima permitida",
    link_servidor="Link para unirse al servidor/juego",
)
async def abrir_escena(
    interaction: discord.Interaction,
    vias: str,
    adelantamiento: str,
    velocidad_maxima: str,
    link_servidor: str,
):
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)

    if channel_id in escenas:
        await interaction.response.send_message(
            "⚠️ Ya hay una sesión abierta en este canal. Ciérrala primero con `/cerrar_escena`.",
            ephemeral=True,
        )
        return

    escena = {
        "vias": vias,
        "adelantamiento": adelantamiento,
        "velocidad_maxima": velocidad_maxima,
        "link_servidor": link_servidor,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    escenas[channel_id] = escena
    guardar(ESCENAS_FILE, escenas)

    await interaction.response.send_message(embed=_embed_sesion(escena))


@bot.tree.command(name="cerrar_escena", description="Cierra la sesión de rol activa en este canal")
async def cerrar_escena(interaction: discord.Interaction):
    escenas = cargar(ESCENAS_FILE)
    channel_id = str(interaction.channel_id)
    escena = escenas.get(channel_id)

    if not escena:
        await interaction.response.send_message(
            "🚫 No hay ninguna sesión abierta en este canal.", ephemeral=True
        )
        return

    inicio = datetime.fromisoformat(escena["inicio"])
    duracion = datetime.now(timezone.utc) - inicio
    horas, resto = divmod(int(duracion.total_seconds()), 3600)
    minutos = resto // 60

    del escenas[channel_id]
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(
        title="🔒 | SESIÓN FINALIZADA",
        description=(
            f"La sesión en **{NOMBRE_SERVIDOR}** ha llegado a su fin. ¡Buen rol, ciudadanos! 🏁🎉\n\n"
            "⭐ No olviden calificar la atención de su host con `/evaluar_staff`, "
            "¡su opinión nos ayuda a mejorar! ⭐"
        ),
        color=discord.Color.red(),
    )
    embed.add_field(name="🧑‍✈️ Host", value=escena["host"], inline=True)
    embed.add_field(name="🔐 Cerrada por", value=str(interaction.user), inline=True)
    embed.add_field(name="⏱️ Duración", value=f"{horas}h {minutos}m", inline=True)

    host_id = escena.get("host_id")
    contenido = f"📣 <@{host_id}> ¡tu sesión fue cerrada! 👇" if host_id else None
    await interaction.response.send_message(content=contenido, embed=embed)


# ---------- Evaluación de staff ----------

class EvaluacionModal(discord.ui.Modal, title="Evaluación de Staff"):
    que_hizo = discord.ui.TextInput(
        label="¿Qué hizo? (Sesión, duda, reporte)", max_length=100
    )
    calificacion = discord.ui.TextInput(
        label="Atención del 1 al 10", placeholder="Ej: 9", max_length=2
    )
    amable_resolvio = discord.ui.TextInput(
        label="¿Fue amable/profesional y resolvió?",
        placeholder="Ej: Sí, fue amable y resolvió mi duda",
        max_length=150,
    )
    queja_sugerencia = discord.ui.TextInput(
        label="Queja o sugerencia (opcional)",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=300,
    )

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
                "⚠️ La calificación debe ser un número del 1 al 10. Vuelve a intentarlo.",
                ephemeral=True,
            )
            return

        evaluaciones = cargar(EVALUACIONES_FILE)
        clave_staff = str(self.staff.id)
        evaluaciones.setdefault(clave_staff, []).append(
            {
                "nombre_staff": str(self.staff),
                "evaluador": str(interaction.user),
                "que_hizo": self.que_hizo.value,
                "calificacion": nota,
                "amable_resolvio": self.amable_resolvio.value,
                "queja_sugerencia": self.queja_sugerencia.value or "Ninguna",
                "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"),
            }
        )
        guardar(EVALUACIONES_FILE, evaluaciones)

        estrellas = "⭐" * round(nota / 2) or "✩"
        embed = discord.Embed(
            title="📝 | NUEVA EVALUACIÓN DE STAFF",
            description=f"¡Gracias por tu opinión, {interaction.user.mention}! 🙌",
            color=discord.Color.purple(),
        )
        embed.add_field(name="🧑‍✈️ Staff evaluado", value=self.staff.mention, inline=False)
        embed.add_field(name="📋 ¿Qué hizo?", value=self.que_hizo.value, inline=False)
        embed.add_field(name="📊 Atención", value=f"{estrellas} ({nota}/10)", inline=True)
        embed.add_field(name="🤝 ¿Amable/profesional y resolvió?", value=self.amable_resolvio.value, inline=True)
        embed.add_field(
            name="💬 Queja o sugerencia adicional",
            value=self.queja_sugerencia.value or "Ninguna",
            inline=False,
        )
        embed.set_footer(text=f"Evaluado por {interaction.user}")
        await interaction.response.send_message(content=self.staff.mention, embed=embed)


@bot.tree.command(name="evaluar_staff", description="Evalúa la atención que te dio un miembro del staff")
@app_commands.describe(staff="Selecciona al staff que quieres evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvaluacionModal(staff))


# ---------- Votación de asistencia ----------

def _embed_votacion(votacion: dict) -> discord.Embed:
    asistentes = votacion.get("asistentes", [])
    no_asistentes = votacion.get("no_asistentes", [])

    embed = discord.Embed(
        title="🗳️ | ¿ABRIMOS SESIÓN? — VOTACIÓN DE ASISTENCIA",
        description=(
            "🏁 El host está midiendo el ambiente antes de arrancar motores.\n\n"
            f"🎯 **Meta:** {votacion['votos_requeridos']} votos para abrir la sesión\n"
            "👇 Toca un botón para decir si te apuntas"
        ),
        color=discord.Color.orange(),
    )
    embed.add_field(
        name=f"✅ Asistirán ({len(asistentes)}/{votacion['votos_requeridos']})",
        value="\n".join(f"<@{u}>" for u in asistentes) or "Nadie todavía",
        inline=True,
    )
    embed.add_field(
        name=f"❌ No asistirán ({len(no_asistentes)})",
        value="\n".join(f"<@{u}>" for u in no_asistentes) or "Nadie todavía",
        inline=True,
    )
    embed.set_footer(text=f"🧑‍✈️ Host: {votacion['host']}")
    return embed


class VotacionView(discord.ui.View):
    """Botones Asistir / No asistir para la votación previa a abrir sesión."""

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
            await interaction.response.send_message("⛔ Esta votación ya no está activa.", ephemeral=True)
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
                f"🎉🏁 <@{votacion['host_id']}> ¡Se alcanzó el mínimo de "
                f"**{votacion['votos_requeridos']} votos**! Ya puedes abrir la sesión con `/abrir_escena` 🚦"
            )


@bot.tree.command(name="votacion_sesion", description="Abre una votación para ver cuántos asistirán a la próxima sesión")
@app_commands.describe(votos_requeridos="Cantidad de votos que necesitas para abrir la sesión")
async def votacion_sesion(interaction: discord.Interaction, votos_requeridos: int):
    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)

    if channel_id in votaciones:
        await interaction.response.send_message(
            "⚠️ Ya hay una votación activa en este canal. Ciérrala con `/cerrar_votacion`.",
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


@bot.tree.command(name="cerrar_votacion", description="Cierra la votación de asistencia activa en este canal")
async def cerrar_votacion(interaction: discord.Interaction):
    votaciones = cargar(VOTACIONES_FILE)
    channel_id = str(interaction.channel_id)

    if channel_id not in votaciones:
        await interaction.response.send_message("🚫 No hay ninguna votación activa en este canal.", ephemeral=True)
        return

    del votaciones[channel_id]
    guardar(VOTACIONES_FILE, votaciones)
    await interaction.response.send_message("🔒 Votación cerrada.")


bot.run(TOKEN)
