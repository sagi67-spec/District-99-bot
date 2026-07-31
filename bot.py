"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
CÓDIGO COMPLETO - PARTE 1/12
"""

import json
import os
import re
import asyncio
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

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
URL_TURNOS = "https://cdn.discordapp.com/attachments/1530830750310596618/1531055540514455572/17851021019872.png?ex=6a67d216&is=6a668096&hm=3bddae490796415f8448684f03e7932e64264750921009730b84f3ecfbd4f75a&"
URL_MULTA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531055546965430323/17851021478742.png?ex=6a67d218&is=6a668098&hm=2216204e8e15107614ff02bea59d14010c2707dbec46a71e57b6bdc3afdbb9bd&"
URL_GREENVILLE = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192419599646861/CIUDAD_20260727_002853_0000.gif?ex=6a685191&is=6a670011&hm=832b3f6bf1e256982b0dbbd7fa8281278b2a533726cbfaada976a6673bffbb81"
URL_HORTON = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192061502689280/CIUDAD_20260727_002438_0000.gif?ex=6a68513b&is=6a66ffbb&hm=4456b6abef72efa13b52de84e80590589badb480923ddd52c9996829032a3868"
URL_BROOKMERE = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192290465415188/CIUDAD_20260727_002733_0000.gif?ex=6a685172&is=6a66fff2&hm=02e727a19459e9f1bfa13f001214b6270e4ecbcde608e7ad35bee717d2582a71"
URL_1VIA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192775813500968/DISTRICT_99_20260727_004421_0000.gif?ex=6a6851e5&is=6a670065&hm=2a1675b2b3a494012932aaa3f23116efcfbbd9e2671e2907255ec84dedbb12f7"
URL_2VIAS = "https://cdn.discordapp.com/attachments/1530830750310596618/1531192488964915280/DISTRICT_99_20260727_003731_0000.gif?ex=6a6851a1&is=6a670021&hm=9a1eeff6b027a816bd60b81b0cb2742f83d8ba8a40ea788c1ecb19baa787c624"

# ==================== URLS DE IMÁGENES DE SESIÓN ====================
URL_SESION_ABIERTA = "https://cdn.discordapp.com/attachments/1530830750310596618/1531365771786059846/District_99_20260727_121958_0000.gif"
URL_SESION_CERRADA_NUEVA = "https://cdn.discordapp.com/attachments/1530830726939934933/1531366374318805285/District_99_20260727_120442_0000.gif"

# ==================== URLS DE IMÁGENES DE PANELES ====================
URL_IMG_WSP = "https://cdn.discordapp.com/attachments/1530830750310596618/1532508289747910866/17854478075312.png?ex=6a6d1b10&is=6a6bc990&hm=67bda4b88223643be3ecebfff9fc007dcd7f049e7044cab616c00f180dd6797e&"
URL_IMG_EMS = "https://cdn.discordapp.com/attachments/1530830750310596618/1532508289386942464/17854474035892.png?ex=6a6d1b10&is=6a6bc990&hm=d82847fc25e82511b3c7b46f09bed4940b1082e102ef7562cf1a17fc9bd5705f&"
URL_IMG_DOT = "https://cdn.discordapp.com/attachments/1530830750310596618/1532508288946536609/17854473803762.png?ex=6a6d1b10&is=6a6bc990&hm=ef438544563e9fe07ee4625f2ffcd2114a679ecc7ca79835fe229653a00793ee&"

# ==================== CONFIGURACIÓN DE CANALES ====================
CANAL_PAGOS_ID = 1529957306198917200
CANAL_CREAR_LICENCIAS_ID = 1530408543784669256
CANAL_REGISTRO_LICENCIAS_ID = 1530416508969287700
CANAL_REGISTRO_DNI_ID = 1525919490041319477
CANAL_LOGS_ID = 1530830726939934933
CANAL_ANUNCIOS_ID = 1524525824869666856
CANAL_GENERAL_ID = 1524200579297972336
CANAL_SESIONES_ID = 1525377180622786701

# ==================== ROLES ====================
ROL_HOST_NOMBRE = "Host│🎮"
ROL_POLICIA_NOMBRE = "Wsp│👮"
ROL_DNI_NOMBRE = "Dni│🪪"
ROL_LICENCIA_NOMBRE = "Licencia│🚗"
ROL_TRABAJANDO_NOMBRE = "Trabajando│🛠️"
ROL_EMS_NOMBRE = "Ems│ 🚑"
ROL_DOT_NOMBRE = "Dot│🚧"

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

def es_ems(member):
    return tiene_rol(member, ROL_EMS_NOMBRE)

def es_dot(member):
    return tiene_rol(member, ROL_DOT_NOMBRE)

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
        # ==================== FUNCIÓN PARA GENERAR LICENCIA ====================
async def generar_licencia(usuario: discord.Member, datos_licencia: dict):
    try:
        W, H = 1200, 750
        img = Image.new('RGB', (W, H), color=(18, 18, 22))
        draw = ImageDraw.Draw(img)

        # ========== COLORES ==========
        DORADO = (212, 175, 90)
        DORADO_CLARO = (235, 205, 140)
        BLANCO = (255, 255, 255)
        GRIS = (160, 165, 175)
        NEGRO_CARD = (22, 22, 26)
        VERDE = (60, 210, 100)

        # ========== FONDO ==========
        for i in range(H):
            t = i / H
            r = int(150 + 60 * abs(0.5 - t) * 2)
            g = int(155 + 60 * abs(0.5 - t) * 2)
            b = int(165 + 60 * abs(0.5 - t) * 2)
            draw.line([(0, i), (W, i)], fill=(r, g, b))

        margen = 22
        draw.rectangle([margen, margen, W - margen, H - margen], fill=NEGRO_CARD)

        # ========== FUENTES ==========
        try:
            font_logo = ImageFont.truetype("arial.ttf", 60)
            font_logo_sub = ImageFont.truetype("arial.ttf", 26)
            font_title = ImageFont.truetype("arial.ttf", 42)
            font_sub = ImageFont.truetype("arial.ttf", 20)
            font_lic_num = ImageFont.truetype("arial.ttf", 22)
            font_valid = ImageFont.truetype("arial.ttf", 15)
            font_label = ImageFont.truetype("arial.ttf", 17)
            font_value = ImageFont.truetype("arial.ttf", 27)
            font_status = ImageFont.truetype("arial.ttf", 26)
            font_footer = ImageFont.truetype("arial.ttf", 14)
            font_avatar_label = ImageFont.truetype("arial.ttf", 17)
        except:
            font_logo = font_logo_sub = font_title = font_sub = font_lic_num = font_valid = font_label = font_value = font_status = font_footer = font_avatar_label = ImageFont.load_default()

        # ========== ESQUINAS ==========
        esquina = 45
        grosor = 4
        bx1, by1, bx2, by2 = margen + 12, margen + 12, W - margen - 12, H - margen - 12
        for (cx, cy, dx, dy) in [(bx1, by1, 1, 1), (bx2, by1, -1, 1), (bx1, by2, 1, -1), (bx2, by2, -1, -1)]:
            draw.line([(cx, cy), (cx + esquina * dx, cy)], fill=DORADO, width=grosor)
            draw.line([(cx, cy), (cx, cy + esquina * dy)], fill=DORADO, width=grosor)

        # ========== LOGO ==========
        draw.text((60, 40), "99", fill=DORADO, font=font_logo)
        draw.text((60, 108), "GVRP", fill=DORADO_CLARO, font=font_logo_sub)

        # ========== TÍTULO ==========
        draw.text((W // 2, 42), "LICENCIA DE CONDUCIR", fill=BLANCO, font=font_title, anchor="mt")
        draw.text((W // 2, 96), "DISTRICT 99 - GVRP", fill=GRIS, font=font_sub, anchor="mt")

        # ========== Nº LICENCIA ==========
        licencia_id = datos_licencia.get('licencia_id', 'LIC-0000')
        draw.text((W - 60, 40), f"#{licencia_id}", fill=DORADO, font=font_lic_num, anchor="rt")
        draw.text((W - 60, 68), "VALID", fill=GRIS, font=font_valid, anchor="rt")
        draw.line([60, 165, W - 60, 165], fill=DORADO, width=2)

        # ========== ICONOS ==========
        def icono_persona(cx, cy, s, color):
            draw.ellipse([cx - s*0.3, cy - s*0.5, cx + s*0.3, cy], outline=color, width=2)
            draw.arc([cx - s*0.5, cy - s*0.05, cx + s*0.5, cy + s*0.9], 180, 360, fill=color, width=2)

        def icono_pastel(cx, cy, s, color):
            draw.rectangle([cx - s*0.4, cy, cx + s*0.4, cy + s*0.35], outline=color, width=2)
            for dx in (-0.25, 0, 0.25):
                draw.line([cx + dx*s, cy, cx + dx*s, cy - s*0.2], fill=color, width=2)
                draw.ellipse([cx + dx*s - 2, cy - s*0.28, cx + dx*s + 2, cy - s*0.2], fill=color)

        def icono_maletin(cx, cy, s, color):
            draw.rectangle([cx - s*0.4, cy - s*0.1, cx + s*0.4, cy + s*0.35], outline=color, width=2)
            draw.arc([cx - s*0.18, cy - s*0.32, cx + s*0.18, cy - s*0.05], 180, 360, fill=color, width=2)
            draw.line([cx - s*0.4, cy + s*0.1, cx + s*0.4, cy + s*0.1], fill=color, width=1)

        def icono_gamepad(cx, cy, s, color):
            draw.rounded_rectangle([cx - s*0.45, cy - s*0.2, cx + s*0.45, cy + s*0.2], radius=int(s*0.2), outline=color, width=2)
            draw.line([cx - s*0.3, cy, cx - s*0.15, cy], fill=color, width=2)
            draw.line([cx - s*0.225, cy - s*0.08, cx - s*0.225, cy + s*0.08], fill=color, width=2)
            draw.ellipse([cx + s*0.15, cy - s*0.08, cx + s*0.22, cy - s*0.01], outline=color, width=1)
            draw.ellipse([cx + s*0.28, cy + s*0.02, cx + s*0.35, cy + s*0.09], outline=color, width=1)

        def icono_tarjeta(cx, cy, s, color):
            draw.rounded_rectangle([cx - s*0.45, cy - s*0.3, cx + s*0.45, cy + s*0.3], radius=4, outline=color, width=2)
            draw.line([cx - s*0.45, cy - s*0.05, cx + s*0.45, cy - s*0.05], fill=color, width=1)
            draw.ellipse([cx - s*0.3, cy + s*0.05, cx - s*0.12, cy + s*0.2], outline=color, width=1)

        def icono_calendario(cx, cy, s, color):
            draw.rounded_rectangle([cx - s*0.4, cy - s*0.35, cx + s*0.4, cy + s*0.35], radius=3, outline=color, width=2)
            draw.line([cx - s*0.4, cy - s*0.1, cx + s*0.4, cy - s*0.1], fill=color, width=2)
            draw.line([cx - s*0.2, cy - s*0.48, cx - s*0.2, cy - s*0.3], fill=color, width=2)
            draw.line([cx + s*0.2, cy - s*0.48, cx + s*0.2, cy - s*0.3], fill=color, width=2)

        # ========== AVATAR DISCORD ==========
        avatar_size = 175
        avatar_x, avatar_y = 70, 200
        try:
            avatar_response = requests.get(usuario.display_avatar.url, timeout=5)
            avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA").resize((avatar_size, avatar_size))
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
            circular = Image.new('RGBA', (avatar_size, avatar_size))
            circular.paste(avatar_img, (0, 0), mask)
            img.paste(circular, (avatar_x, avatar_y), circular)
        except:
            pass
        draw.ellipse([avatar_x - 4, avatar_y - 4, avatar_x + avatar_size + 4, avatar_y + avatar_size + 4], outline=DORADO, width=4)
        draw.text((avatar_x + avatar_size // 2, avatar_y + avatar_size + 14), "DISCORD", fill=GRIS, font=font_avatar_label, anchor="mt")

        # ========== AVATAR ROBLOX ==========
        avatar_x2, avatar_y2 = 70, 445
        try:
            user_roblox = datos_licencia.get('user_roblox', '')
            search_url = f"https://users.roblox.com/v1/users/search?keyword={user_roblox}"
            search_data = requests.get(search_url, timeout=5).json()
            if search_data.get('data'):
                rid = search_data['data'][0]['id']
                thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={rid}&size=420x420&format=Png"
                thumb_data = requests.get(thumb_url, timeout=5).json()
                foto_url = thumb_data['data'][0]['imageUrl']
                foto_img = Image.open(BytesIO(requests.get(foto_url, timeout=5).content)).convert("RGBA").resize((avatar_size, avatar_size))
                mask = Image.new('L', (avatar_size, avatar_size), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
                circular = Image.new('RGBA', (avatar_size, avatar_size))
                circular.paste(foto_img, (0, 0), mask)
                img.paste(circular, (avatar_x2, avatar_y2), circular)
        except:
            pass
        draw.ellipse([avatar_x2 - 4, avatar_y2 - 4, avatar_x2 + avatar_size + 4, avatar_y2 + avatar_size + 4], outline=DORADO, width=4)
        draw.text((avatar_x2 + avatar_size // 2, avatar_y2 + avatar_size + 14), "ROBLOX", fill=GRIS, font=font_avatar_label, anchor="mt")

        # ========== TARJETA DE DATOS ==========
        card_x1, card_y1 = 320, 195
        card_x2, card_y2 = W - 60, 610
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=18, fill=(32, 32, 38), outline=DORADO, width=2)

        # ========== TABLA DE DATOS ==========
        table_x = card_x1 + 40
        col2_x = card_x1 + (card_x2 - card_x1) // 2 + 30
        y_start = card_y1 + 35
        row_h = 75
        icon_x_offset = -34
        icon_size = 26

        datos_izq = [
            ("NOMBRE COMPLETO", f"{datos_licencia.get('nombre', '')} {datos_licencia.get('apellidos', '')}", icono_persona),
            ("EDAD", f"{datos_licencia.get('edad', '')} AÑOS", icono_pastel),
            ("OFICIO", datos_licencia.get('oficio', ''), icono_maletin),
            ("ROBLOX", datos_licencia.get('user_roblox', ''), icono_gamepad),
            ("DNI", datos_licencia.get('dni', ''), icono_tarjeta),
        ]
        datos_der = [
            ("LICENCIA", licencia_id, icono_tarjeta),
            ("EXPEDICIÓN", datos_licencia.get('fecha_expedicion', ''), icono_calendario),
            ("EXPIRACIÓN", datos_licencia.get('fecha_expiracion', ''), icono_calendario),
        ]

        y = y_start
        for i in range(max(len(datos_izq), len(datos_der))):
            if i < len(datos_izq):
                label, value, icono_fn = datos_izq[i]
                icono_fn(table_x + icon_x_offset + icon_size // 2, y + 14, icon_size, DORADO)
                draw.text((table_x, y), label, fill=DORADO, font=font_label)
                draw.text((table_x, y + 24), value, fill=BLANCO, font=font_value)
            if i < len(datos_der):
                label, value, icono_fn = datos_der[i]
                icono_fn(col2_x + icon_x_offset + icon_size // 2, y + 14, icon_size, DORADO)
                draw.text((col2_x, y), label, fill=DORADO, font=font_label)
                draw.text((col2_x, y + 24), value, fill=BLANCO, font=font_value)
            if i < max(len(datos_izq), len(datos_der)) - 1:
                draw.line([table_x, y + 62, card_x2 - 40, y + 62], fill=(55, 50, 40), width=1)
            y += row_h

        # ========== RECUADRO ESTADO ==========
        estado_y1 = y_start + 4 * row_h - 10
        draw.rounded_rectangle([col2_x - 34, estado_y1, card_x2 - 40, estado_y1 + 55], radius=12,
                                fill=(20, 45, 30), outline=VERDE, width=2)
        draw.ellipse([col2_x - 14, estado_y1 + 19, col2_x + 4, estado_y1 + 37], fill=VERDE)
        draw.text((col2_x + 20, estado_y1 + 13), "ESTADO: ACTIVA", fill=VERDE, font=font_status, anchor="lt")

        # ========== PIE DE PÁGINA ==========
        draw.line([60, H - 70, W - 60, H - 70], fill=DORADO, width=1)
        draw.text((W // 2, H - 50), "DISTRICT 99 - GVRP © 2026", fill=GRIS, font=font_footer, anchor="mt")

        # ========== GUARDAR ==========
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG', quality=95)
        img_bytes.seek(0)
        return discord.File(img_bytes, filename="licencia.png")

    except Exception as e:
        print(f"❌ Error al generar la licencia: {e}")
        import traceback
        traceback.print_exc()
        return None
# ==================== FUNCIÓN PARA GENERAR DNI (PROVISIONAL) ====================
async def generar_dni(usuario: discord.Member, datos_dni: dict):
    try:
        W, H = 600, 420
        img = Image.new('RGB', (W, H), color=(18, 18, 22))
        draw = ImageDraw.Draw(img)

        # ========== COLORES ==========
        DORADO = (212, 175, 90)
        BLANCO = (255, 255, 255)
        GRIS = (160, 165, 175)
        VERDE = (60, 210, 100)

        # ========== FONDO ==========
        for i in range(H):
            t = i / H
            r = int(150 + 60 * abs(0.5 - t) * 2)
            g = int(155 + 60 * abs(0.5 - t) * 2)
            b = int(165 + 60 * abs(0.5 - t) * 2)
            draw.line([(0, i), (W, i)], fill=(r, g, b))

        margen = 15
        draw.rectangle([margen, margen, W - margen, H - margen], fill=(22, 22, 26))

        # ========== FUENTES ==========
        try:
            font_title = ImageFont.truetype("arial.ttf", 24)
            font_sub = ImageFont.truetype("arial.ttf", 14)
            font_label = ImageFont.truetype("arial.ttf", 12)
            font_value = ImageFont.truetype("arial.ttf", 18)
            font_footer = ImageFont.truetype("arial.ttf", 10)
            font_status = ImageFont.truetype("arial.ttf", 16)
        except:
            font_title = font_sub = font_label = font_value = font_footer = font_status = ImageFont.load_default()

        # ========== ESQUINAS ==========
        esquina = 25
        bx1, by1, bx2, by2 = margen + 8, margen + 8, W - margen - 8, H - margen - 8
        for (cx, cy, dx, dy) in [(bx1, by1, 1, 1), (bx2, by1, -1, 1), (bx1, by2, 1, -1), (bx2, by2, -1, -1)]:
            draw.line([(cx, cy), (cx + esquina * dx, cy)], fill=DORADO, width=2)
            draw.line([(cx, cy), (cx, cy + esquina * dy)], fill=DORADO, width=2)

        # ========== TÍTULO ==========
        draw.text((W // 2, 25), "DOCUMENTO NACIONAL DE IDENTIDAD", fill=BLANCO, font=font_title, anchor="mt")
        draw.text((W // 2, 52), "DISTRICT 99 - GVRP", fill=GRIS, font=font_sub, anchor="mt")

        # ========== Nº DNI ==========
        draw.text((W - 25, 18), f"#{datos_dni.get('numero_dni', '00000000')}", fill=DORADO, font=font_sub, anchor="rt")
        draw.line([30, 72, W - 30, 72], fill=DORADO, width=1)

        # ========== AVATAR ==========
        avatar_size = 75
        avatar_x, avatar_y = 25, 90
        try:
            avatar_response = requests.get(usuario.display_avatar.url, timeout=5)
            avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA").resize((avatar_size, avatar_size))
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
            circular = Image.new('RGBA', (avatar_size, avatar_size))
            circular.paste(avatar_img, (0, 0), mask)
            img.paste(circular, (avatar_x, avatar_y), circular)
        except:
            pass
        draw.ellipse([avatar_x - 3, avatar_y - 3, avatar_x + avatar_size + 3, avatar_y + avatar_size + 3], outline=DORADO, width=2)

        # ========== DATOS ==========
        table_x = 125
        y_start = 90
        spacing = 38

        datos = [
            ("NOMBRE", f"{datos_dni.get('nombre', '')} {datos_dni.get('apellidos', '')}"),
            ("EDAD", f"{datos_dni.get('edad', '')} AÑOS"),
            ("NACIMIENTO", datos_dni.get('fecha_nacimiento', '')),
            ("OFICIO", datos_dni.get('oficio', '')),
            ("DNI", datos_dni.get('numero_dni', '')),
            ("EXPEDICIÓN", datos_dni.get('fecha_expedicion', '')),
        ]

        y = y_start
        for label, value in datos:
            draw.text((table_x, y), label, fill=GRIS, font=font_label)
            draw.text((table_x, y + 16), value, fill=BLANCO, font=font_value)
            draw.line([table_x, y + 34, W - 20, y + 34], fill=(40, 40, 45), width=1)
            y += spacing

        # ========== ESTADO ==========
        status_y = H - 45
        draw.line([30, status_y - 5, W - 30, status_y - 5], fill=(40, 40, 45), width=1)
        draw.ellipse([W // 2 - 55, status_y, W // 2 - 41, status_y + 14], fill=VERDE)
        draw.text((W // 2 - 28, status_y + 2), "VÁLIDO", fill=VERDE, font=font_status, anchor="lt")

        # ========== PIE ==========
        draw.text((W // 2, H - 16), "DISTRICT 99 - GVRP © 2026", fill=(70, 75, 85), font=font_footer, anchor="mt")

        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG', quality=95)
        img_bytes.seek(0)
        return discord.File(img_bytes, filename="dni.png")

    except Exception as e:
        print(f"❌ Error al generar DNI: {e}")
        import traceback
        traceback.print_exc()
        return None
        # ==================== BOT ====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Crear archivos
ARCHIVOS_JSON = [DNI_FILE, ESCENAS_FILE, EVALUACIONES_FILE, AUTOS_FILE, MULTAS_FILE, LICENCIAS_FILE, TURNOS_FILE]
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
                    embed.add_field(name="📢 **¿Cómo recuperarla?**", value="Paga todas tus multas y usa el panel de licencias de nuevo", inline=False)
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
        print(f"   🔹 Trabajando: {ROL_TRABAJANDO_NOMBRE}")
        print(f"   🔹 EMS: {ROL_EMS_NOMBRE}")
        print(f"   🔹 DOT: {ROL_DOT_NOMBRE}")
        print(f"✅ Canales configurados:")
        print(f"   🔹 Pagos: {CANAL_PAGOS_ID}")
        print(f"   🔹 Crear Licencias: {CANAL_CREAR_LICENCIAS_ID}")
        print(f"   🔹 Registro Licencias: {CANAL_REGISTRO_LICENCIAS_ID}")
        print(f"   🔹 Registro DNI: {CANAL_REGISTRO_DNI_ID}")
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

# ==================== COMANDO DE SINCRONIZACIÓN ====================
@bot.tree.command(name="sync", description="🔄 Sincronizar comandos - SOLO ADMINS")
async def sync(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo Admins pueden usar este comando.", ephemeral=True)
        return
    
    try:
        await bot.tree.sync()
        await interaction.response.send_message("✅ **Comandos sincronizados correctamente.**", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al sincronizar: {e}", ephemeral=True)
        # ==================== PANEL DE DNI ====================
class PanelDNIView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🪪 Crear DNI", style=discord.ButtonStyle.success)
    async def crear_dni(self, interaction: discord.Interaction, button: discord.ui.Button):
        class DNIModal(discord.ui.Modal, title="🪪 Crear DNI"):
            nombre = discord.ui.TextInput(
                label="Nombre",
                placeholder="Ej: Juan",
                max_length=50,
                required=True
            )
            apellidos = discord.ui.TextInput(
                label="Apellidos",
                placeholder="Ej: Pérez García",
                max_length=50,
                required=True
            )
            fecha_nacimiento = discord.ui.TextInput(
                label="📅 Fecha de Nacimiento (DD/MM/YYYY) - Edad se calcula automáticamente",
                placeholder="Ej: 15/05/1998",
                max_length=10,
                required=True
            )
            oficio = discord.ui.TextInput(
                label="Oficio",
                placeholder="Ej: Conductor",
                max_length=50,
                required=True
            )
            user_roblox = discord.ui.TextInput(
                label="Usuario de Roblox",
                placeholder="Ej: Juanito_99",
                max_length=50,
                required=True
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    user_id = str(modal_interaction.user.id)

                    if not validar_fecha(self.fecha_nacimiento.value):
                        await modal_interaction.response.send_message("⚠️ Formato de fecha inválido. Usa DD/MM/YYYY", ephemeral=True)
                        return

                    try:
                        fecha_parts = self.fecha_nacimiento.value.split("/")
                        año_nacimiento = int(fecha_parts[2])
                        edad = datetime.now().year - año_nacimiento
                    except:
                        edad = "No calculada"

                    dnis = cargar(DNI_FILE)
                    if user_id in dnis:
                        await modal_interaction.response.send_message("⚠️ Ya tienes un DNI creado.", ephemeral=True)
                        return

                    numero_dni = generar_numero_dni(user_id)

                    datos_dni = {
                        "nombre": self.nombre.value,
                        "apellidos": self.apellidos.value,
                        "fecha_nacimiento": self.fecha_nacimiento.value,
                        "edad": edad,
                        "numero_dni": numero_dni,
                        "fecha_expedicion": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
                        "oficio": self.oficio.value,
                        "user_roblox": self.user_roblox.value,
                        "usuario_discord": str(modal_interaction.user)
                    }
                    dnis[user_id] = datos_dni
                    guardar(DNI_FILE, dnis)

                    try:
                        rol = discord.utils.get(modal_interaction.guild.roles, name=ROL_DNI_NOMBRE)
                        if rol:
                            await modal_interaction.user.add_roles(rol)
                    except:
                        pass

                    archivo_dni = await generar_dni(modal_interaction.user, datos_dni)
                    if archivo_dni is None:
                        await modal_interaction.response.send_message("❌ Error al generar la imagen del DNI.", ephemeral=True)
                        return

                    embed = discord.Embed(
                        title="🪪 **DNI GENERADO**",
                        description=f"{modal_interaction.user.mention}",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="attachment://dni.png")
                    embed.add_field(
                        name="📌 ¿Dónde se envió?",
                        value=f"Este DNI se ha enviado al canal <#{CANAL_REGISTRO_DNI_ID}>",
                        inline=False
                    )
                    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")

                    canal_dni = bot.get_channel(CANAL_REGISTRO_DNI_ID)
                    if canal_dni:
                        await canal_dni.send(
                            content=f"📢 **Nuevo DNI generado para {modal_interaction.user.mention}**",
                            embed=embed,
                            file=archivo_dni
                        )
                        await modal_interaction.response.send_message(
                            f"✅ **¡DNI creado exitosamente!**\nSe ha enviado al canal <#{CANAL_REGISTRO_DNI_ID}>.",
                            ephemeral=True
                        )
                    else:
                        await modal_interaction.response.send_message("❌ No se encontró el canal de registro de DNI.", ephemeral=True)

                    await enviar_log(f"🪪 **{modal_interaction.user.mention}** creó su DNI (Nº {numero_dni})", discord.Color.blue())

                except Exception as e:
                    print(f"❌ Error en el panel de DNI: {e}")
                    await modal_interaction.response.send_message(f"❌ Error al crear el DNI: {e}", ephemeral=True)

        await interaction.response.send_modal(DNIModal())
        # ==================== PANEL DE LICENCIAS ====================
class PanelLicenciasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Crear Licencia", style=discord.ButtonStyle.success)
    async def crear_licencia(self, interaction: discord.Interaction, button: discord.ui.Button):
        dnis = cargar(DNI_FILE)
        user_id = str(interaction.user.id)
        
        if user_id not in dnis:
            await interaction.response.send_message("⚠️ Necesitas tener un DNI antes de solicitar licencia. Usa el panel de DNI.", ephemeral=True)
            return

        licencias = cargar(LICENCIAS_FILE)
        if user_id in licencias:
            await interaction.response.send_message("⚠️ Ya tienes una licencia activa.", ephemeral=True)
            return

        class LicenciaModal(discord.ui.Modal, title="📝 Solicitar Licencia"):
            nombre = discord.ui.TextInput(label="Nombre", placeholder="Ej: Juan", max_length=50, required=True)
            apellidos = discord.ui.TextInput(label="Apellidos", placeholder="Ej: Pérez García", max_length=50, required=True)
            fecha_nacimiento = discord.ui.TextInput(label="📅 Fecha de Nacimiento (DD/MM/YYYY) - Edad se calcula automáticamente", placeholder="Ej: 15/05/1998", max_length=10, required=True)
            oficio = discord.ui.TextInput(label="Oficio", placeholder="Ej: Conductor", max_length=50, required=True)
            user_roblox = discord.ui.TextInput(label="Usuario de Roblox", placeholder="Ej: Juanito_99", max_length=50, required=True)

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    user_id = str(modal_interaction.user.id)

                    if not validar_fecha(self.fecha_nacimiento.value):
                        await modal_interaction.response.send_message("⚠️ Formato de fecha inválido. Usa DD/MM/YYYY", ephemeral=True)
                        return

                    try:
                        fecha_parts = self.fecha_nacimiento.value.split("/")
                        año_nacimiento = int(fecha_parts[2])
                        edad = datetime.now().year - año_nacimiento
                    except:
                        edad = "No calculada"

                    licencias = cargar(LICENCIAS_FILE)
                    if user_id in licencias:
                        await modal_interaction.response.send_message("⚠️ Ya tienes una licencia activa.", ephemeral=True)
                        return

                    dnis = cargar(DNI_FILE)
                    if user_id not in dnis:
                        await modal_interaction.response.send_message("⚠️ Necesitas tener un DNI antes de solicitar licencia.", ephemeral=True)
                        return

                    num_licencia = len(licencias) + 1
                    licencia_id = f"LIC-2026-{num_licencia:04d}"

                    datos_licencia = {
                        "nombre": self.nombre.value,
                        "apellidos": self.apellidos.value,
                        "fecha_nacimiento": self.fecha_nacimiento.value,
                        "edad": str(edad),
                        "oficio": self.oficio.value,
                        "user_roblox": self.user_roblox.value,
                        "user_discord": str(modal_interaction.user),
                        "dni": dnis[user_id]["numero_dni"],
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

                    archivo_licencia = await generar_licencia(modal_interaction.user, datos_licencia)
                    if archivo_licencia is None:
                        await modal_interaction.response.send_message("❌ Error al generar la imagen de la licencia.", ephemeral=True)
                        return

                    embed = discord.Embed(
                        title="🪪 **LICENCIA GENERADA**",
                        description=f"{modal_interaction.user.mention}",
                        color=discord.Color.gold()
                    )
                    embed.set_image(url="attachment://licencia.png")
                    embed.add_field(
                        name="📌 ¿Dónde se envió?",
                        value=f"Esta licencia se ha enviado al canal <#{CANAL_REGISTRO_LICENCIAS_ID}>",
                        inline=False
                    )
                    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")

                    canal_registro = bot.get_channel(CANAL_REGISTRO_LICENCIAS_ID)
                    if canal_registro:
                        await canal_registro.send(
                            content=f"📢 **Nueva licencia generada para {modal_interaction.user.mention}**",
                            embed=embed,
                            file=archivo_licencia
                        )
                        await modal_interaction.response.send_message(
                            f"✅ **¡Licencia creada exitosamente!**\nSe ha enviado al canal <#{CANAL_REGISTRO_LICENCIAS_ID}>.",
                            ephemeral=True
                        )
                    else:
                        await modal_interaction.response.send_message("❌ No se encontró el canal de registro de licencias.", ephemeral=True)

                    await enviar_log(f"🪪 **{modal_interaction.user.mention}** creó su licencia (Nº {licencia_id})", discord.Color.gold())

                except Exception as e:
                    print(f"❌ Error en el panel de licencias: {e}")
                    await modal_interaction.response.send_message(f"❌ Error al crear la licencia: {e}", ephemeral=True)

        await interaction.response.send_modal(LicenciaModal())
        # ==================== PANEL DE WSP (POLICÍA) ====================
class PanelWSPView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🚔 Selecciona una opción",
        options=[
            discord.SelectOption(label="🚔 Iniciar Turno", value="iniciar", emoji="🚔"),
            discord.SelectOption(label="🛑 Finalizar Turno", value="finalizar", emoji="🛑"),
            discord.SelectOption(label="📋 Turnos Activos", value="activos", emoji="📋"),
        ]
    )
    async def wsp_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        opcion = select.values[0]
        
        if opcion == "iniciar":
            if not es_policia(interaction.user):
                await interaction.response.send_message("⛔ Solo **POLICIA** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id in turnos and turnos[user_id].get("activo", False):
                await interaction.response.send_message("⚠️ Ya tienes un turno activo. Usa la opción **Finalizar Turno**.", ephemeral=True)
                return
            
            try:
                rol_trabajando = discord.utils.get(interaction.guild.roles, name=ROL_TRABAJANDO_NOMBRE)
                if rol_trabajando:
                    await interaction.user.add_roles(rol_trabajando)
            except:
                pass
            
            turnos[user_id] = {
                "policia_id": user_id,
                "policia_nombre": str(interaction.user),
                "inicio": datetime.now(timezone.utc).isoformat(),
                "activo": True,
                "tipo": "wsp"
            }
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(
                title="🚔 **TURNO INICIADO**",
                description=f"{interaction.user.mention} ha comenzado su patrullaje.",
                color=discord.Color.green()
            )
            embed.add_field(name="👮 **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="📋 **Estado**", value="🟢 EN SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_WSP)
            embed.set_footer(text="¡Buena suerte en tu patrullaje! 🚓")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚔 **{interaction.user.mention}** inició turno de patrullaje", discord.Color.green())

        elif opcion == "finalizar":
            if not es_policia(interaction.user):
                await interaction.response.send_message("⛔ Solo **POLICIA** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id not in turnos or not turnos[user_id].get("activo", False):
                await interaction.response.send_message("❌ No tienes un turno activo. Usa la opción **Iniciar Turno**.", ephemeral=True)
                return
            
            try:
                rol_trabajando = discord.utils.get(interaction.guild.roles, name=ROL_TRABAJANDO_NOMBRE)
                if rol_trabajando and rol_trabajando in interaction.user.roles:
                    await interaction.user.remove_roles(rol_trabajando)
            except:
                pass
            
            turno = turnos[user_id]
            inicio = datetime.fromisoformat(turno["inicio"])
            duracion = datetime.now(timezone.utc) - inicio
            horas, resto = divmod(int(duracion.total_seconds()), 3600)
            minutos = resto // 60
            
            turnos[user_id]["activo"] = False
            turnos[user_id]["fin"] = datetime.now(timezone.utc).isoformat()
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(
                title="🚔 **TURNO FINALIZADO**",
                description=f"{interaction.user.mention} ha terminado su patrullaje.",
                color=discord.Color.red()
            )
            embed.add_field(name="👮 **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=inicio.strftime("%H:%M hs"), inline=True)
            embed.add_field(name="🕐 **Fin**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="⏱️ **Duración**", value=f"{horas}h {minutos}m", inline=False)
            embed.add_field(name="📋 **Estado**", value="🔴 FUERA DE SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_WSP)
            embed.set_footer(text="¡Buen trabajo oficial! 🌟")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚔 **{interaction.user.mention}** finalizó turno (Duración: {horas}h {minutos}m)", discord.Color.red())

        elif opcion == "activos":
            if not es_policia(interaction.user):
                await interaction.response.send_message("⛔ Solo **POLICIA** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            activos = []
            
            for user_id, turno in turnos.items():
                if turno.get("activo", False) and turno.get("tipo") == "wsp":
                    inicio = datetime.fromisoformat(turno["inicio"])
                    duracion = datetime.now(timezone.utc) - inicio
                    horas, resto = divmod(int(duracion.total_seconds()), 3600)
                    minutos = resto // 60
                    activos.append({
                        "nombre": turno["policia_nombre"],
                        "id": user_id,
                        "horas": horas,
                        "minutos": minutos
                    })
            
            if not activos:
                await interaction.response.send_message("📋 No hay policias en servicio actualmente.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🚓 **POLICIAS EN SERVICIO**",
                description=f"Total: {len(activos)} oficiales",
                color=discord.Color.blue()
            )
            
            for policia in activos:
                embed.add_field(
                    name=f"👮 {policia['nombre']}",
                    value=f"🕐 {policia['horas']}h {policia['minutos']}m activo",
                    inline=False
                )
            
            embed.set_image(url=URL_IMG_WSP)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # ==================== PANEL DE EMS ====================
class PanelEMSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🚑 Selecciona una opción",
        options=[
            discord.SelectOption(label="🚨 Iniciar Servicio", value="iniciar", emoji="🚨"),
            discord.SelectOption(label="🛑 Finalizar Servicio", value="finalizar", emoji="🛑"),
            discord.SelectOption(label="📋 EMS Activos", value="activos", emoji="📋"),
        ]
    )
    async def ems_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        opcion = select.values[0]
        
        if opcion == "iniciar":
            if not es_ems(interaction.user):
                await interaction.response.send_message("⛔ Solo **EMS** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id in turnos and turnos[user_id].get("activo", False):
                await interaction.response.send_message("⚠️ Ya tienes un servicio activo.", ephemeral=True)
                return
            
            try:
                rol_trabajando = discord.utils.get(interaction.guild.roles, name=ROL_TRABAJANDO_NOMBRE)
                if rol_trabajando:
                    await interaction.user.add_roles(rol_trabajando)
            except:
                pass
            
            turnos[user_id] = {
                "usuario_id": user_id,
                "usuario_nombre": str(interaction.user),
                "inicio": datetime.now(timezone.utc).isoformat(),
                "activo": True,
                "tipo": "ems"
            }
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(
                title="🚑 **SERVICIO DE EMS INICIADO**",
                description=f"{interaction.user.mention} ha comenzado su servicio de emergencias.",
                color=discord.Color.green()
            )
            embed.add_field(name="🚑 **Servicio**", value="EMS ACTIVO", inline=False)
            embed.add_field(name="👨‍⚕️ **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="📋 **Estado**", value="🟢 EN SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_EMS)
            embed.set_footer(text="¡Buena suerte en tu servicio! 🚑")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚑 **{interaction.user.mention}** inició servicio de EMS", discord.Color.green())

        elif opcion == "finalizar":
            if not es_ems(interaction.user):
                await interaction.response.send_message("⛔ Solo **EMS** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id not in turnos or not turnos[user_id].get("activo", False):
                await interaction.response.send_message("❌ No tienes un servicio activo.", ephemeral=True)
                return
            
            try:
                rol_trabajando = discord.utils.get(interaction.guild.roles, name=ROL_TRABAJANDO_NOMBRE)
                if rol_trabajando and rol_trabajando in interaction.user.roles:
                    await interaction.user.remove_roles(rol_trabajando)
            except:
                pass
            
            turno = turnos[user_id]
            inicio = datetime.fromisoformat(turno["inicio"])
            duracion = datetime.now(timezone.utc) - inicio
            horas, resto = divmod(int(duracion.total_seconds()), 3600)
            minutos = resto // 60
            
            turnos[user_id]["activo"] = False
            turnos[user_id]["fin"] = datetime.now(timezone.utc).isoformat()
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(
                title="🚑 **SERVICIO DE EMS FINALIZADO**",
                description=f"{interaction.user.mention} ha terminado su servicio de emergencias.",
                color=discord.Color.red()
            )
            embed.add_field(name="🚑 **Servicio**", value="EMS FINALIZADO", inline=False)
            embed.add_field(name="👨‍⚕️ **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=inicio.strftime("%H:%M hs"), inline=True)
            embed.add_field(name="🕐 **Fin**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="⏱️ **Duración**", value=f"{horas}h {minutos}m", inline=False)
            embed.add_field(name="📋 **Estado**", value="🔴 FUERA DE SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_EMS)
            embed.set_footer(text="¡Buen trabajo! 🌟")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚑 **{interaction.user.mention}** finalizó servicio de EMS (Duración: {horas}h {minutos}m)", discord.Color.red())

        elif opcion == "activos":
            if not es_ems(interaction.user):
                await interaction.response.send_message("⛔ Solo **EMS** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            activos = []
            
            for user_id, turno in turnos.items():
                if turno.get("activo", False) and turno.get("tipo") == "ems":
                    inicio = datetime.fromisoformat(turno["inicio"])
                    duracion = datetime.now(timezone.utc) - inicio
                    horas, resto = divmod(int(duracion.total_seconds()), 3600)
                    minutos = resto // 60
                    activos.append({
                        "nombre": turno["usuario_nombre"],
                        "id": user_id,
                        "horas": horas,
                        "minutos": minutos
                    })
            
            if not activos:
                await interaction.response.send_message("📋 No hay EMS en servicio actualmente.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🚑 **EMS EN SERVICIO**",
                description=f"Total: {len(activos)} personal médico",
                color=discord.Color.green()
            )
            
            for ems in activos:
                embed.add_field(
                    name=f"🚑 {ems['nombre']}",
                    value=f"🕐 {ems['horas']}h {ems['minutos']}m activo",
                    inline=False
                )
            
            embed.set_image(url=URL_IMG_EMS)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # ==================== PANEL DE DOT ====================
class PanelDOTView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🚦 Selecciona una opción",
        options=[
            discord.SelectOption(label="🚦 Iniciar Servicio", value="iniciar", emoji="🚦"),
            discord.SelectOption(label="🛑 Finalizar Servicio", value="finalizar", emoji="🛑"),
            discord.SelectOption(label="📋 DOT Activos", value="activos", emoji="📋"),
        ]
    )
    async def dot_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        opcion = select.values[0]
        
        if opcion == "iniciar":
            if not es_dot(interaction.user):
                await interaction.response.send_message("⛔ Solo **DOT** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id in turnos and turnos[user_id].get("activo", False):
                await interaction.response.send_message("⚠️ Ya tienes un servicio activo.", ephemeral=True)
                return
            
            try:
                rol_trabajando = discord.utils.get(interaction.guild.roles, name=ROL_TRABAJANDO_NOMBRE)
                if rol_trabajando:
                    await interaction.user.add_roles(rol_trabajando)
            except:
                pass
            
            turnos[user_id] = {
                "usuario_id": user_id,
                "usuario_nombre": str(interaction.user),
                "inicio": datetime.now(timezone.utc).isoformat(),
                "activo": True,
                "tipo": "dot"
            }
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(
                title="🚦 **SERVICIO DE DOT INICIADO**",
                description=f"{interaction.user.mention} ha comenzado su servicio de tránsito.",
                color=discord.Color.green()
            )
            embed.add_field(name="🚦 **Servicio**", value="DOT ACTIVO", inline=False)
            embed.add_field(name="👷 **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="📋 **Estado**", value="🟢 EN SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_DOT)
            embed.set_footer(text="¡Buena suerte en tu servicio! 🚦")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚦 **{interaction.user.mention}** inició servicio de DOT", discord.Color.green())

        elif opcion == "finalizar":
            if not es_dot(interaction.user):
                await interaction.response.send_message("⛔ Solo **DOT** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id not in turnos or not turnos[user_id].get("activo", False):
                await interaction.response.send_message("❌ No tienes un servicio activo.", ephemeral=True)
                return
            
            try:
                rol_trabajando = discord.utils.get(interaction.guild.roles, name=ROL_TRABAJANDO_NOMBRE)
                if rol_trabajando and rol_trabajando in interaction.user.roles:
                    await interaction.user.remove_roles(rol_trabajando)
            except:
                pass
            
            turno = turnos[user_id]
            inicio = datetime.fromisoformat(turno["inicio"])
            duracion = datetime.now(timezone.utc) - inicio
            horas, resto = divmod(int(duracion.total_seconds()), 3600)
            minutos = resto // 60
            
            turnos[user_id]["activo"] = False
            turnos[user_id]["fin"] = datetime.now(timezone.utc).isoformat()
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(
                title="🚦 **SERVICIO DE DOT FINALIZADO**",
                description=f"{interaction.user.mention} ha terminado su servicio de tránsito.",
                color=discord.Color.red()
            )
            embed.add_field(name="🚦 **Servicio**", value="DOT FINALIZADO", inline=False)
            embed.add_field(name="👷 **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=inicio.strftime("%H:%M hs"), inline=True)
            embed.add_field(name="🕐 **Fin**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="⏱️ **Duración**", value=f"{horas}h {minutos}m", inline=False)
            embed.add_field(name="📋 **Estado**", value="🔴 FUERA DE SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_DOT)
            embed.set_footer(text="¡Buen trabajo! 🌟")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚦 **{interaction.user.mention}** finalizó servicio de DOT (Duración: {horas}h {minutos}m)", discord.Color.red())

        elif opcion == "activos":
            if not es_dot(interaction.user):
                await interaction.response.send_message("⛔ Solo **DOT** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            activos = []
            
            for user_id, turno in turnos.items():
                if turno.get("activo", False) and turno.get("tipo") == "dot":
                    inicio = datetime.fromisoformat(turno["inicio"])
                    duracion = datetime.now(timezone.utc) - inicio
                    horas, resto = divmod(int(duracion.total_seconds()), 3600)
                    minutos = resto // 60
                    activos.append({
                        "nombre": turno["usuario_nombre"],
                        "id": user_id,
                        "horas": horas,
                        "minutos": minutos
                    })
            
            if not activos:
                await interaction.response.send_message("📋 No hay DOT en servicio actualmente.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🚦 **DOT EN SERVICIO**",
                description=f"Total: {len(activos)} personal de tránsito",
                color=discord.Color.green()
            )
            
            for dot in activos:
                embed.add_field(
                    name=f"🚦 {dot['nombre']}",
                    value=f"🕐 {dot['horas']}h {dot['minutos']}m activo",
                    inline=False
                )
            
            embed.set_image(url=URL_IMG_DOT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # ==================== COMANDOS DE PANELES ====================
@bot.tree.command(name="panel_dni", description="🪪 Panel para crear DNI - SOLO ADMIN/HOST")
async def panel_dni(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🪪 **PANEL DE DNI**",
        description=(
            "Presiona el botón para crear tu **Documento Nacional de Identidad**.\n\n"
            "📝 **Crear DNI** → Completa el formulario y genera tu DNI.\n\n"
            "⚠️ **Requisitos:**\n"
            "• No debes tener un DNI previo.\n"
            "• Solo puedes tener **UN** DNI por persona.\n\n"
            "📌 **Importante:**\n"
            "• Este DNI es **personal e intransferible**.\n"
            "• La edad se calcula automáticamente.\n\n"
            "🖼️ **Tu DNI se generará automáticamente** y se enviará al canal de registro."
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    
    view = PanelDNIView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="panel_licencias", description="📋 Panel para solicitar licencias - SOLO ADMIN/HOST")
async def panel_licencias(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📋 **PANEL DE LICENCIAS**",
        description=(
            "Presiona el botón para solicitar tu **Licencia de Conducir**.\n\n"
            "📝 **Crear Licencia** → Completa el formulario y genera tu licencia.\n\n"
            "⚠️ **Requisitos:**\n"
            "• Debes tener un DNI creado (usa el panel de DNI).\n"
            "• Solo puedes tener **UNA** licencia activa por persona.\n\n"
            "📌 **Importante:**\n"
            "• Esta licencia es **personal e intransferible**.\n"
            "• Si pierdes tu licencia, deberás solicitar una nueva.\n"
            "• La licencia tiene una vigencia de **2 años**.\n\n"
            "🖼️ **Tu licencia se generará automáticamente** y se enviará al canal de registro."
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    
    view = PanelLicenciasView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="panel_wsp", description="📋 Panel para gestionar turnos de policía - SOLO ADMIN/HOST")
async def panel_wsp(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🚔 **PANEL DE WSP**",
        description=(
            "Selecciona una opción del menú para gestionar tu patrullaje.\n\n"
            "🚔 **Iniciar Turno** → Comienza tu patrullaje.\n"
            "🛑 **Finalizar Turno** → Termina tu patrullaje.\n"
            "📋 **Turnos Activos** → Ver policías en servicio.\n\n"
            "⚠️ **Requisitos:** Debes tener el rol **Wsp│👮** para usar estas opciones.\n"
            "🔒 **Privacidad:** Las respuestas solo las verás tú.\n"
            f"🔄 **Rol automático:** Al iniciar turno, se te asignará el rol **{ROL_TRABAJANDO_NOMBRE}**."
        ),
        color=discord.Color.blue()
    )
    embed.set_image(url=URL_IMG_WSP)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    
    view = PanelWSPView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="panel_ems", description="🚑 Panel para gestionar servicios de EMS - SOLO ADMIN/HOST")
async def panel_ems(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🚑 **PANEL DE EMS**",
        description=(
            "Selecciona una opción del menú para gestionar tu servicio de emergencias.\n\n"
            "🚨 **Iniciar Servicio** → Comienza tu servicio de EMS.\n"
            "🛑 **Finalizar Servicio** → Termina tu servicio.\n"
            "📋 **EMS Activos** → Ver personal médico en servicio.\n\n"
            "⚠️ **Requisitos:** Debes tener el rol **Ems│🚑** para usar estas opciones.\n"
            "🔒 **Privacidad:** Las respuestas solo las verás tú.\n"
            f"🔄 **Rol automático:** Al iniciar servicio, se te asignará el rol **{ROL_TRABAJANDO_NOMBRE}**."
        ),
        color=discord.Color.green()
    )
    embed.set_image(url=URL_IMG_EMS)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    
    view = PanelEMSView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="panel_dot", description="🚦 Panel para gestionar servicios de DOT - SOLO ADMIN/HOST")
async def panel_dot(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🚦 **PANEL DE DOT**",
        description=(
            "Selecciona una opción del menú para gestionar tu servicio de tránsito.\n\n"
            "🚦 **Iniciar Servicio** → Comienza tu servicio de DOT.\n"
            "🛑 **Finalizar Servicio** → Termina tu servicio.\n"
            "📋 **DOT Activos** → Ver personal de tránsito en servicio.\n\n"
            "⚠️ **Requisitos:** Debes tener el rol **Dot│🚧** para usar estas opciones.\n"
            "🔒 **Privacidad:** Las respuestas solo las verás tú.\n"
            f"🔄 **Rol automático:** Al iniciar servicio, se te asignará el rol **{ROL_TRABAJANDO_NOMBRE}**."
        ),
        color=discord.Color.orange()
    )
    embed.set_image(url=URL_IMG_DOT)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    
    view = PanelDOTView()
    await interaction.response.send_message(embed=embed, view=view)
    # ==================== COMANDOS EXISTENTES ====================
# Aquí van todos los comandos que ya tenías:
# - registrar_multa
# - historial_multas
# - mis_multas
# - confirmar_pago
# - registrar_auto
# - ver_autos
# - eliminar_auto
# - abrir_sesion
# - cerrar_sesion
# - evaluar_staff
# - enviar_mensaje
# - stats

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
