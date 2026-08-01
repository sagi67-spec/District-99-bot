"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
CÓDIGO COMPLETO - PARTE 1/16
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
        # ==================== FUNCIÓN PARA GENERAR DNI (CLAUDE) ====================
async def generar_dni(usuario: discord.Member, datos_dni: dict):
    try:
        W, H = 1200, 750
        img = Image.new('RGB', (W, H), color=(15, 15, 18))
        draw = ImageDraw.Draw(img)

        # ========== COLORES ==========
        BLANCO = (255, 255, 255)
        GRIS = (150, 155, 165)
        GRIS_LABEL = (140, 145, 155)
        VERDE = (60, 210, 130)
        LINEA = (48, 48, 55)

        # ========== FONDO DEGRADADO SUAVE ==========
        radio_card = 30
        draw.rounded_rectangle([0, 0, W, H], radius=radio_card, fill=(20, 20, 24))
        overlay = Image.new('L', (W, H), 0)
        overlay_draw = ImageDraw.Draw(overlay)
        for i in range(H):
            val = int(10 * (1 - i / H))
            overlay_draw.line([(0, i), (W, i)], fill=val)
        img = Image.composite(Image.new('RGB', (W, H), (35, 35, 42)), img, overlay)
        draw = ImageDraw.Draw(img)
        mask_final = Image.new('L', (W, H), 0)
        ImageDraw.Draw(mask_final).rounded_rectangle([0, 0, W, H], radius=radio_card, fill=255)
        fondo_negro = Image.new('RGB', (W, H), (10, 10, 12))
        img = Image.composite(img, fondo_negro, mask_final)
        draw = ImageDraw.Draw(img)

        # ========== FUENTES ==========
        FUENTE_BASE = "fonts/Montserrat-Bold.ttf"
        FUENTE_NORMAL = "fonts/Montserrat-Regular.ttf"
        try:
            font_title = ImageFont.truetype(FUENTE_BASE, 34)
            font_sub = ImageFont.truetype(FUENTE_NORMAL, 20)
            font_num = ImageFont.truetype(FUENTE_BASE, 22)
            font_label = ImageFont.truetype(FUENTE_NORMAL, 17)
            font_value = ImageFont.truetype(FUENTE_BASE, 27)
            font_status = ImageFont.truetype(FUENTE_BASE, 30)
            font_footer = ImageFont.truetype(FUENTE_NORMAL, 15)
        except Exception as e:
            print(f"⚠️ Error cargando fuentes: {e}")
            font_title = font_sub = font_num = font_label = font_value = font_status = font_footer = ImageFont.load_default()

        # ========== TÍTULO ==========
        draw.text((W // 2, 45), "DOCUMENTO NACIONAL DE IDENTIDAD", fill=BLANCO, font=font_title, anchor="mt")
        draw.text((W // 2, 90), "DISTRICT 99 - GVRP", fill=GRIS, font=font_sub, anchor="mt")

        # ========== Nº DNI ==========
        numero_dni = datos_dni.get('numero_dni', '00000000')
        draw.text((W - 60, 55), f"DNI #{numero_dni}", fill=BLANCO, font=font_num, anchor="rt")

        # ========== AVATAR ==========
        avatar_size = 320
        avatar_x = 60
        avatar_y = (H - 120 - avatar_size) // 2 + 20

        try:
            avatar_response = requests.get(usuario.display_avatar.url, timeout=5)
            avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA").resize((avatar_size, avatar_size))
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
            circular = Image.new('RGBA', (avatar_size, avatar_size))
            circular.paste(avatar_img, (0, 0), mask)
            img.paste(circular, (avatar_x, avatar_y), circular)
        except Exception as e:
            print(f"⚠️ Error avatar: {e}")
        draw.ellipse([avatar_x - 3, avatar_y - 3, avatar_x + avatar_size + 3, avatar_y + avatar_size + 3], outline=(70, 70, 78), width=3)

        # ========== TARJETA DE DATOS ==========
        card_x1 = avatar_x + avatar_size + 50
        card_y1 = 150
        card_x2 = W - 60
        card_y2 = H - 150
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, outline=(70, 70, 78), width=2)

        pad = 35
        col_w = (card_x2 - card_x1 - pad * 2) // 2
        col1_x = card_x1 + pad
        col2_x = card_x1 + pad + col_w + 20

        y = card_y1 + 28
        draw.text((col1_x, y), "NOMBRE", fill=GRIS_LABEL, font=font_label)
        draw.text((col1_x, y + 24), f"{datos_dni.get('nombre', '')} {datos_dni.get('apellidos', '')}".upper(), fill=BLANCO, font=font_value)
        y += 70
        draw.line([col1_x, y, card_x2 - pad, y], fill=LINEA, width=1)
        y += 24

        draw.text((col1_x, y), "EDAD", fill=GRIS_LABEL, font=font_label)
        draw.text((col1_x, y + 24), f"{datos_dni.get('edad', '')} AÑOS", fill=BLANCO, font=font_value)
        draw.text((col2_x, y), "NACIMIENTO", fill=GRIS_LABEL, font=font_label)
        draw.text((col2_x, y + 24), datos_dni.get('fecha_nacimiento', ''), fill=BLANCO, font=font_value)
        y += 70
        draw.line([col1_x, y, card_x2 - pad, y], fill=LINEA, width=1)
        y += 24

        draw.text((col1_x, y), "OFICIO", fill=GRIS_LABEL, font=font_label)
        draw.text((col1_x, y + 24), datos_dni.get('oficio', 'Ciudadano'), fill=BLANCO, font=font_value)
        draw.text((col2_x, y), "DNI", fill=GRIS_LABEL, font=font_label)
        draw.text((col2_x, y + 24), numero_dni, fill=BLANCO, font=font_value)
        y += 70
        draw.line([col1_x, y, card_x2 - pad, y], fill=LINEA, width=1)
        y += 24

        draw.text((col1_x, y), "EXPEDICIÓN", fill=GRIS_LABEL, font=font_label)
        draw.text((col1_x, y + 24), datos_dni.get('fecha_expedicion', ''), fill=BLANCO, font=font_value)
        if datos_dni.get('fecha_expiracion'):
            draw.text((col2_x, y), "EXPIRACIÓN", fill=GRIS_LABEL, font=font_label)
            draw.text((col2_x, y + 24), datos_dni.get('fecha_expiracion', ''), fill=BLANCO, font=font_value)

        # ========== BARRA DE ESTADO ==========
        barra_y1 = H - 115
        barra_y2 = H - 40
        draw.rounded_rectangle([40, barra_y1, W - 40, barra_y2], radius=14, fill=(24, 24, 28))
        cx_dot = W // 2 - 90
        cy_dot = (barra_y1 + barra_y2) // 2
        draw.ellipse([cx_dot - 14, cy_dot - 14, cx_dot + 14, cy_dot + 14], fill=VERDE)
        draw.text((cx_dot + 30, cy_dot), "VÁLIDO", fill=VERDE, font=font_status, anchor="lm")

        # ========== PIE ==========
        draw.text((W // 2, H - 28), "DISTRICT 99 - GVRP © 2026", fill=GRIS, font=font_footer, anchor="mm")

        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG', quality=95)
        img_bytes.seek(0)
        return discord.File(img_bytes, filename="dni.png")

    except Exception as e:
        print(f"❌ Error al generar DNI: {e}")
        import traceback
        traceback.print_exc()
        return None
        # ==================== FUNCIÓN PARA GENERAR LICENCIA (CLAUDE) ====================
async def generar_licencia(usuario: discord.Member, datos_licencia: dict):
    try:
        W, H = 1200, 750
        img = Image.new('RGB', (W, H), color=(8, 8, 10))
        draw = ImageDraw.Draw(img)

        # ========== COLORES ==========
        NEGRO_CARD = (14, 14, 17)
        DORADO = (198, 162, 90)
        DORADO_CLARO = (228, 198, 135)
        DORADO_OSCURO = (120, 95, 45)
        BLANCO = (240, 240, 238)
        GRIS_TEXTO = (150, 150, 158)
        GRIS_LABEL = (120, 118, 128)
        LINEA = (45, 43, 40)
        VERDE = (80, 220, 150)

        # ========== SOMBRA + TARJETA REDONDEADA ==========
        draw.rounded_rectangle([14, 14, W - 6, H - 6], radius=26, fill=(0, 0, 0))
        draw.rounded_rectangle([6, 6, W - 14, H - 14], radius=26, fill=NEGRO_CARD)

        # ========== FRANJA HOLOGRÁFICA IZQUIERDA (dorado/negro metálico) ==========
        strip_w = 34
        for x in range(strip_w):
            t = x / strip_w
            r = int(60 + 120 * abs(0.5 - (t * 3) % 1 - 0.5))
            g = int(50 + 95 * abs(0.5 - (t * 2.3 + 0.3) % 1 - 0.5))
            b = int(20 + 40 * abs(0.5 - (t * 2.7 + 0.6) % 1 - 0.5))
            draw.line([(6 + x, 6), (6 + x, H - 14)], fill=(r, g, b))
        for i in range(-H, W, 16):
            draw.line([(6 + i, 6), (6 + i + H, H - 14)], fill=(255, 235, 190), width=1)

        # ========== FUENTES ==========
        FUENTE_BASE = "fonts/Montserrat-Bold.ttf"
        FUENTE_NORMAL = "fonts/Montserrat-Regular.ttf"
        try:
            font_title = ImageFont.truetype(FUENTE_BASE, 38)
            font_sub = ImageFont.truetype(FUENTE_NORMAL, 18)
            font_label = ImageFont.truetype(FUENTE_BASE, 16)
            font_value = ImageFont.truetype(FUENTE_NORMAL, 23)
            font_footer = ImageFont.truetype(FUENTE_NORMAL, 14)
            font_footer_b = ImageFont.truetype(FUENTE_BASE, 15)
            font_status = ImageFont.truetype(FUENTE_BASE, 20)
            font_num = ImageFont.truetype(FUENTE_BASE, 17)
            font_avatar_label = ImageFont.truetype(FUENTE_BASE, 14)
            font_watermark = ImageFont.truetype(FUENTE_BASE, 140)
            font_logo = ImageFont.truetype(FUENTE_BASE, 28)
        except Exception as e:
            print(f"⚠️ Error cargando fuentes: {e}")
            font_title = font_sub = font_label = font_value = font_footer = font_footer_b = font_status = font_num = font_avatar_label = font_watermark = font_logo = ImageFont.load_default()

        # ========== WATERMARK CENTRAL "99" (muy sutil, dorado tenue) ==========
        wm_cx, wm_cy, wm_r = 780, 400, 175
        wm_color = (28, 26, 22)
        draw.ellipse([wm_cx - wm_r, wm_cy - wm_r, wm_cx + wm_r, wm_cy + wm_r], outline=(35, 32, 26), width=2)
        draw.text((wm_cx, wm_cy), "99", fill=wm_color, font=font_watermark, anchor="mm")

        # ========== HEADER: LOGO CIRCULAR + TÍTULO ==========
        logo_x = strip_w + 45
        draw.ellipse([logo_x, 42, logo_x + 76, 118], outline=DORADO, width=3)
        draw.text((logo_x + 38, 80), "99", fill=DORADO, font=font_logo, anchor="mm")

        draw.text((logo_x + 98, 42), "LICENCIA DE CONDUCIR", fill=DORADO_CLARO, font=font_title)
        draw.text((logo_x + 98, 86), "DISTRICT 99  •  GVRP", fill=GRIS_TEXTO, font=font_sub)

        # ========== BANNER NEGRO/DORADO ESQUINA SUP. DERECHA ==========
        banner_pts = [(W - 265, 40), (W - 40, 40), (W - 40, 100), (W - 90, 130), (W - 265, 130)]
        draw.polygon(banner_pts, fill=(20, 19, 16))
        draw.polygon(banner_pts, outline=DORADO, width=2)
        licencia_id = datos_licencia.get('licencia_id', 'LIC-0000')
        draw.text((W - 152, 65), f"#{licencia_id}", fill=DORADO_CLARO, font=font_num, anchor="mm")
        draw.text((W - 152, 95), "VALID", fill=DORADO_OSCURO, font=font_footer, anchor="mm")

        # ========== LÍNEA SEPARADORA ==========
        draw.line([strip_w + 45, 150, W - 45, 150], fill=DORADO, width=2)

        # ========== AVATAR DISCORD (esquinas redondeadas, borde dorado) ==========
        avatar_size = 165
        avatar_x = strip_w + 45
        avatar_y = 185

        try:
            avatar_response = requests.get(usuario.display_avatar.url, timeout=5)
            avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA").resize((avatar_size, avatar_size))
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, avatar_size, avatar_size), radius=16, fill=255)
            recortado = Image.new('RGBA', (avatar_size, avatar_size))
            recortado.paste(avatar_img, (0, 0), mask)
            img.paste(recortado, (avatar_x, avatar_y), recortado)
        except Exception as e:
            print(f"⚠️ Error avatar discord: {e}")
        draw.rounded_rectangle([avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size], radius=16, outline=DORADO, width=3)
        draw.text((avatar_x + avatar_size // 2, avatar_y + avatar_size + 12), "DISCORD", fill=GRIS_TEXTO, font=font_avatar_label, anchor="mt")

        # ========== AVATAR ROBLOX (círculo superpuesto, borde dorado) ==========
        avatar_size2 = 92
        avatar_x2 = avatar_x + avatar_size - 32
        avatar_y2 = avatar_y + avatar_size - 32

        try:
            user_roblox = datos_licencia.get('user_roblox', '')
            search_url = f"https://users.roblox.com/v1/users/search?keyword={user_roblox}"
            search_data = requests.get(search_url, timeout=5).json()
            if search_data.get('data'):
                rid = search_data['data'][0]['id']
                thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={rid}&size=420x420&format=Png"
                thumb_data = requests.get(thumb_url, timeout=5).json()
                foto_url = thumb_data['data'][0]['imageUrl']
                foto_img = Image.open(BytesIO(requests.get(foto_url, timeout=5).content)).convert("RGBA").resize((avatar_size2, avatar_size2))
                mask2 = Image.new('L', (avatar_size2, avatar_size2), 0)
                ImageDraw.Draw(mask2).ellipse((0, 0, avatar_size2, avatar_size2), fill=255)
                circ2 = Image.new('RGBA', (avatar_size2, avatar_size2))
                circ2.paste(foto_img, (0, 0), mask2)
                fondo_circ = Image.new('RGBA', (avatar_size2 + 10, avatar_size2 + 10), (0, 0, 0, 0))
                ImageDraw.Draw(fondo_circ).ellipse((0, 0, avatar_size2 + 10, avatar_size2 + 10), fill=NEGRO_CARD + (255,))
                img.paste(fondo_circ, (avatar_x2 - 5, avatar_y2 - 5), fondo_circ)
                img.paste(circ2, (avatar_x2, avatar_y2), circ2)
        except Exception as e:
            print(f"⚠️ Error avatar roblox: {e}")
        draw.ellipse([avatar_x2 - 3, avatar_y2 - 3, avatar_x2 + avatar_size2 + 3, avatar_y2 + avatar_size2 + 3], outline=DORADO, width=3)

        # ========== CAMPOS DE DATOS (columna de labels fija + valores con línea) ==========
        campo_x_label = avatar_x + avatar_size + 55
        campo_x_valor = campo_x_label + 230   # más ancho para que quepa "USUARIO ROBLOX"
        campo_x_fin = W - 60
        y = 200
        row_h = 62

        campos = [
            ("NOMBRE", datos_licencia.get('nombre', '')),
            ("APELLIDOS", datos_licencia.get('apellidos', '')),
            ("EDAD", f"{datos_licencia.get('edad', '')} AÑOS"),
            ("OFICIO", datos_licencia.get('oficio', '')),
            ("USUARIO ROBLOX", datos_licencia.get('user_roblox', '')),
            ("DNI", datos_licencia.get('dni', '')),
        ]

        for label, value in campos:
            draw.text((campo_x_label, y + 5), label, fill=GRIS_LABEL, font=font_label)
            draw.text((campo_x_valor, y - 2), value, fill=BLANCO, font=font_value)
            draw.line([campo_x_valor, y + 24, campo_x_fin, y + 24], fill=LINEA, width=1)
            y += row_h

        # ========== FOOTER BAR (negro con borde dorado) ==========
        footer_y1 = H - 115
        footer_y2 = H - 20
        draw.rectangle([6, footer_y1, W - 14, footer_y2], fill=(16, 15, 13))
        draw.line([6, footer_y1, W - 14, footer_y1], fill=DORADO, width=2)

        fx = strip_w + 60
        draw.text((fx, footer_y1 + 18), "EXPEDICIÓN", fill=DORADO_OSCURO, font=font_footer)
        draw.text((fx, footer_y1 + 38), datos_licencia.get('fecha_expedicion', ''), fill=BLANCO, font=font_footer_b)

        fx2 = fx + 220
        draw.text((fx2, footer_y1 + 18), "EXPIRACIÓN", fill=DORADO_OSCURO, font=font_footer)
        draw.text((fx2, footer_y1 + 38), datos_licencia.get('fecha_expiracion', ''), fill=BLANCO, font=font_footer_b)

        # Estado a la derecha del footer
        estado_x = W - 280
        draw.rounded_rectangle([estado_x, footer_y1 + 15, W - 60, footer_y1 + 65], radius=10, outline=VERDE, width=2)
        draw.ellipse([estado_x + 16, footer_y1 + 32, estado_x + 32, footer_y1 + 48], fill=VERDE)
        draw.text((estado_x + 45, footer_y1 + 22), "ACTIVA", fill=VERDE, font=font_status)

        draw.text((W // 2 + 15, footer_y2 - 14), "DISTRICT 99 - GVRP  •  Documento Oficial de Roleplay", fill=DORADO_OSCURO, font=font_footer, anchor="mm")

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
                label="📅 Fecha Nacimiento (DD/MM/YYYY)",
                placeholder="Ej: 15/05/1998 (Edad automática)",
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
                label="Usuario Roblox",
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
                label="📅 Fecha Nacimiento (DD/MM/YYYY)",
                placeholder="Ej: 15/05/1998 (Edad automática)",
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
                label="Usuario Roblox",
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
        # ==================== PANEL DE WSP ====================
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
                await interaction.response.send_message("⚠️ Ya tienes un turno activo.", ephemeral=True)
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
            embed.set_footer(text="¡Buena suerte! 🚓")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚔 **{interaction.user.mention}** inició turno", discord.Color.green())

        elif opcion == "finalizar":
            if not es_policia(interaction.user):
                await interaction.response.send_message("⛔ Solo **POLICIA** pueden usar esta opción.", ephemeral=True)
                return
            
            turnos = cargar(TURNOS_FILE)
            user_id = str(interaction.user.id)
            
            if user_id not in turnos or not turnos[user_id].get("activo", False):
                await interaction.response.send_message("❌ No tienes un turno activo.", ephemeral=True)
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
            embed.set_footer(text="¡Buen trabajo! 🌟")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚔 **{interaction.user.mention}** finalizó turno ({horas}h {minutos}m)", discord.Color.red())

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
                await interaction.response.send_message("📋 No hay policias en servicio.", ephemeral=True)
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
                description=f"{interaction.user.mention} ha comenzado su servicio.",
                color=discord.Color.green()
            )
            embed.add_field(name="🚑 **Servicio**", value="EMS ACTIVO", inline=False)
            embed.add_field(name="👨‍⚕️ **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="📋 **Estado**", value="🟢 EN SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_EMS)
            embed.set_footer(text="¡Buena suerte! 🚑")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚑 **{interaction.user.mention}** inició servicio EMS", discord.Color.green())

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
                description=f"{interaction.user.mention} ha terminado su servicio.",
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
            await enviar_log(f"🚑 **{interaction.user.mention}** finalizó EMS ({horas}h {minutos}m)", discord.Color.red())

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
                await interaction.response.send_message("📋 No hay EMS en servicio.", ephemeral=True)
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
                description=f"{interaction.user.mention} ha comenzado su servicio.",
                color=discord.Color.green()
            )
            embed.add_field(name="🚦 **Servicio**", value="DOT ACTIVO", inline=False)
            embed.add_field(name="👷 **Oficial**", value=interaction.user.mention, inline=False)
            embed.add_field(name="🕐 **Inicio**", value=datetime.now(timezone.utc).strftime("%H:%M hs"), inline=True)
            embed.add_field(name="📋 **Estado**", value="🟢 EN SERVICIO", inline=True)
            embed.set_image(url=URL_IMG_DOT)
            embed.set_footer(text="¡Buena suerte! 🚦")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await enviar_log(f"🚦 **{interaction.user.mention}** inició servicio DOT", discord.Color.green())

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
                description=f"{interaction.user.mention} ha terminado su servicio.",
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
            await enviar_log(f"🚦 **{interaction.user.mention}** finalizó DOT ({horas}h {minutos}m)", discord.Color.red())

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
                await interaction.response.send_message("📋 No hay DOT en servicio.", ephemeral=True)
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
    # ==================== COMANDOS DE MULTAS ====================
@bot.tree.command(name="registrar_multa", description="🚨 Registrar multa - SOLO POLICIA")
@app_commands.describe(
    infractor="Usuario infractor",
    infraccion="Infraccion cometida",
    precio="Monto de la multa ($)",
    testigos="Testigos (opcional - menciona)",
    foto="Foto de evidencia (opcional)"
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
    
    embed = discord.Embed(title="🚨 **MULTA REGISTRADA**", color=discord.Color.red())
    embed.add_field(name="👮 **Oficial**", value=interaction.user.mention, inline=False)
    embed.add_field(name="👤 **Infractor**", value=infractor.mention, inline=False)
    embed.add_field(name="⚖️ **Infracción**", value=infraccion, inline=False)
    embed.add_field(name="💰 **Monto**", value=f"**${precio}**", inline=True)
    if testigos_mentions:
        embed.add_field(name="👀 **Testigos**", value=", ".join(testigos_mentions), inline=False)
    embed.add_field(name="📌 **Estado**", value="❌ Sin pagar", inline=True)
    if foto:
        embed.set_image(url=foto.url)
    embed.set_footer(text=f"Registrada el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}")
    
    mensaje = f"{infractor.mention} ¡Has recibido una multa!\n📢 Para pagar: Ve a <#{CANAL_PAGOS_ID}> y escribe `!pay District 99 Bot {precio}`"
    if testigos_mentions:
        mensaje += f"\n👀 **Testigos:** {', '.join(testigos_mentions)}"
    
    await interaction.response.send_message(content=mensaje, embed=embed)
    await enviar_log(f"🚨 **{interaction.user.mention}** multó a **{infractor.mention}** por ${precio}", discord.Color.red())

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
            await interaction.response.send_message(f"📋 {usuario.name} no tiene multas", ephemeral=True)
            return
        titulo = f"🚨 **MULTAS DE {usuario.name.upper()}**"
    else:
        titulo = "🚨 **HISTORIAL DE MULTAS**"
    
    embed = discord.Embed(title=titulo, color=discord.Color.red())
    for i, multa in enumerate(historial[-10:], 1):
        estado = "✅ Pagada" if multa.get('pagada', False) else "❌ Sin pagar"
        embed.add_field(
            name=f"📌 **Multa #{i}**",
            value=f"👮 **Oficial:** {multa['oficial']}\n⚖️ **Infracción:** {multa['infraccion']}\n💰 **Monto:** ${multa['precio']}\n📌 **Estado:** {estado}\n📅 **Fecha:** {multa['fecha']}",
            inline=False
        )
    embed.set_footer(text="Mostrando últimas 10 multas")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mis_multas", description="📋 Ver tu historial de multas")
async def mis_multas(interaction: discord.Interaction):
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    user_id = str(interaction.user.id)
    
    mis_multas = [m for m in historial if m.get('infractor_id') == user_id]
    if not mis_multas:
        await interaction.response.send_message("📋 No tienes multas", ephemeral=True)
        return
    
    embed = discord.Embed(title=f"🚨 **TUS MULTAS**", description=f"Total: {len(mis_multas)}", color=discord.Color.orange())
    total = 0
    for i, multa in enumerate(mis_multas[-10:], 1):
        total += multa.get('precio', 0)
        estado = "✅ Pagada" if multa.get('pagada', False) else "❌ Sin pagar"
        embed.add_field(
            name=f"📌 **Multa #{i}**",
            value=f"👮 **Oficial:** {multa['oficial']}\n⚖️ **Infracción:** {multa['infraccion']}\n💰 **Monto:** ${multa['precio']}\n📌 **Estado:** {estado}",
            inline=False
        )
    embed.add_field(name="💸 **TOTAL ADEUDADO**", value=f"**${total}**", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="confirmar_pago", description="👮 Confirmar pago - SOLO POLICIA")
@app_commands.describe(usuario="Usuario que pagó", monto="Monto que pagó")
async def confirmar_pago(interaction: discord.Interaction, usuario: str, monto: int):
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

    if not miembro:
        await interaction.response.send_message(f"⚠️ No encontré al usuario `{usuario}`.", ephemeral=True)
        return

    user_id = str(miembro.id)
    multas = cargar(MULTAS_FILE)
    historial = multas.get("historial", [])
    
    multa_encontrada = False
    for i, multa in enumerate(historial):
        if multa.get('infractor_id') == user_id and not multa.get('pagada', False) and multa.get('precio') == monto:
            historial[i]['pagada'] = True
            historial[i]['fecha_pago'] = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
            multa_encontrada = True
            break

    if not multa_encontrada:
        await interaction.response.send_message(f"⚠️ No encontré multa de **${monto}** para {miembro.mention}", ephemeral=True)
        return

    guardar(MULTAS_FILE, multas)
    embed = discord.Embed(title="💰 **PAGO CONFIRMADO**", description=f"{miembro.mention} pagó su multa.", color=discord.Color.green())
    embed.add_field(name="💰 **Monto**", value=f"**${monto}**", inline=True)
    embed.add_field(name="👮 **Confirmado por**", value=interaction.user.mention, inline=True)
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"💰 **{miembro.mention}** pagó multa de ${monto} (Confirmado por {interaction.user.mention})", discord.Color.green())
    # ==================== COMANDOS DE AUTOS ====================
@bot.tree.command(name="registrar_auto", description="🚗 Registrar tu vehiculo con foto")
@app_commands.describe(
    usuario_roblox="Tu usuario de Roblox",
    placa="Placa del vehiculo",
    modelo="Modelo/Marca del vehiculo",
    color="Color del vehiculo",
    foto="Sube una foto del vehiculo"
)
async def registrar_auto(
    interaction: discord.Interaction,
    usuario_roblox: str,
    placa: str,
    modelo: str,
    color: str,
    foto: discord.Attachment
):
    if not foto.content_type or not foto.content_type.startswith('image/'):
        await interaction.response.send_message("⚠️ Debe ser una imagen", ephemeral=True)
        return
    
    autos = cargar(AUTOS_FILE)
    user_id = str(interaction.user.id)
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
    
    embed = discord.Embed(title="🚗 **VEHÍCULO REGISTRADO**", color=discord.Color.green())
    embed.add_field(name="👤 **Usuario**", value=interaction.user.mention, inline=False)
    embed.add_field(name="📋 **Modelo**", value=modelo, inline=True)
    embed.add_field(name="🎨 **Color**", value=color, inline=True)
    embed.add_field(name="🅿️ **Placa**", value=placa, inline=True)
    embed.set_image(url=foto.url)
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🚗 **{interaction.user.mention}** registró un vehículo (Placa: {placa})", discord.Color.green())

@bot.tree.command(name="ver_autos", description="🚗 Ver autos de un usuario")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE)
    user_autos = autos.get(str(objetivo.id), [])
    
    if not user_autos:
        await interaction.response.send_message(f"❌ {objetivo.name} no tiene autos registrados", ephemeral=True)
        return
    
    embed = discord.Embed(title=f"🚗 **AUTOS DE {objetivo.name.upper()}**", color=discord.Color.blue())
    for i, auto in enumerate(user_autos, 1):
        embed.add_field(
            name=f"🚘 **Auto #{i}**",
            value=f"👤 **Discord:** {auto['usuario_discord']}\n🎮 **Roblox:** {auto['usuario_roblox']}\n📋 **Modelo:** {auto['modelo']}\n🎨 **Color:** {auto['color']}\n🅿️ **Placa:** {auto['placa']}\n📅 **Registro:** {auto['fecha']}",
            inline=False
        )
        if auto.get('foto'):
            embed.set_image(url=auto['foto'])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_auto", description="🗑️ Eliminar un auto registrado")
@app_commands.describe(numero_auto="Número del auto a eliminar (1, 2, 3...)")
async def eliminar_auto(interaction: discord.Interaction, numero_auto: int):
    autos = cargar(AUTOS_FILE)
    user_id = str(interaction.user.id)
    
    if user_id not in autos or not autos[user_id]:
        await interaction.response.send_message("❌ No tienes autos registrados", ephemeral=True)
        return
    
    if numero_auto < 1 or numero_auto > len(autos[user_id]):
        await interaction.response.send_message(f"⚠️ Número inválido. Tienes {len(autos[user_id])} autos.", ephemeral=True)
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
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🗑️ **{interaction.user.mention}** eliminó un vehículo (Placa: {auto_eliminado.get('placa', 'N/A')})", discord.Color.red())
    # ==================== COMANDOS DE SESIONES ====================
@bot.tree.command(name="abrir_sesion", description="🎬 Abrir sesión - SOLO HOSTS")
@app_commands.describe(
    ciudad="Elige la ciudad",
    vias="Número de vías (1 o 2)",
    velocidad_maxima="Límite de velocidad (mph)",
    adelantamientos="¿Se permiten adelantamientos?",
    link="Link del servidor",
    velocidad_frp="Límite de velocidad para FRP (opcional)"
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
    link: str,
    velocidad_frp: str = None
):
    if not es_host(interaction.user):
        await interaction.response.send_message("⛔ Solo **HOSTS** pueden usar este comando.", ephemeral=True)
        return

    if not velocidad_maxima.isdigit():
        await interaction.response.send_message("⚠️ La velocidad debe ser un número.", ephemeral=True)
        return

    if velocidad_frp and not velocidad_frp.isdigit():
        await interaction.response.send_message("⚠️ La velocidad FRP debe ser un número.", ephemeral=True)
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
                    velocidad_adelanto=self.velocidad_adelanto.value,
                    velocidad_frp=velocidad_frp
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
        velocidad_adelanto=None,
        velocidad_frp=velocidad_frp
    )

async def enviar_sesion(
    interaction: discord.Interaction,
    ciudad: str,
    vias: str,
    velocidad_maxima: str,
    adelantamientos: str,
    link: str,
    velocidad_adelanto: str = None,
    velocidad_frp: str = None
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
        "velocidad_frp": velocidad_frp if velocidad_frp else "No especificada",
        "link_servidor": link,
        "host": str(interaction.user),
        "host_id": str(interaction.user.id),
        "inicio": datetime.now(timezone.utc).isoformat(),
    }
    guardar(ESCENAS_FILE, escenas)

    embed = discord.Embed(title="🏁 **SESIÓN ABIERTA**", description=f"**{NOMBRE_SERVIDOR}**", color=discord.Color.gold())
    embed.set_image(url=URL_SESION_ABIERTA)

    adelanto_texto = "✅ Permitidos" if adelantamientos == "si" else "❌ No permitidos"
    
    detalles = (
        f"🌆 **Ciudad:** {ciudad.capitalize()}\n"
        f"🛣️ **Vías:** {vias} vías\n"
        f"🚗 **Velocidad Máx:** {velocidad_maxima} mph\n"
        f"🚨 **Vel. FRP:** {velocidad_frp if velocidad_frp else 'No especificada'} mph\n"
        f"🏁 **Adelantamientos:** {adelanto_texto}\n"
    )
    
    if adelantamientos == "si" and velocidad_adelanto:
        detalles += f"🚀 **Vel. Adelanto:** {velocidad_adelanto} mph\n"
    
    detalles += f"👑 **Host:** {interaction.user.mention}\n🔗 **Link:** [🌐 Haz clic aquí]({link})"
    
    embed.add_field(name="📋 **DETALLES**", value=detalles, inline=False)
    embed.set_footer(text=f"Sesión iniciada por {interaction.user.name} • {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.display_avatar.url)

    canal_sesiones = bot.get_channel(CANAL_SESIONES_ID)
    if canal_sesiones:
        await canal_sesiones.send(embed=embed)
        await interaction.response.send_message("✅ ¡Sesión enviada al canal de sesiones!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No encontré el canal de sesiones.", ephemeral=True)

    await enviar_log(f"🎬 **{interaction.user.mention}** abrió sesión (Ciudad: {ciudad.capitalize()})", discord.Color.gold())

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

    embed = discord.Embed(title="🔒 **SESIÓN CERRADA**", description=f"**¡Buen rol!** 👏\n⏱️ Duración: {horas}h {minutos}m", color=discord.Color.red())
    embed.set_image(url=URL_SESION_CERRADA_NUEVA)
    embed.set_footer(text=f"Sesión cerrada por {interaction.user.name} • {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.display_avatar.url)

    canal_sesiones = bot.get_channel(CANAL_SESIONES_ID)
    if canal_sesiones:
        await canal_sesiones.send(embed=embed)
        await interaction.response.send_message("✅ ¡Sesión cerrada!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No encontré el canal de sesiones.", ephemeral=True)

    await enviar_log(f"🔒 **{interaction.user.mention}** cerró sesión (Duración: {horas}h {minutos}m)", discord.Color.red())
    # ==================== EVALUAR STAFF ====================
class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
    que_hizo = discord.ui.TextInput(label="¿Qué hizo el staff?", placeholder="Ej: Ayudó con el rol...", max_length=200)
    calificacion = discord.ui.TextInput(label="Calificación (1-10)", placeholder="Ej: 8", max_length=2)
    amable = discord.ui.TextInput(label="¿Fue amable?", placeholder="Ej: Sí, muy amable", max_length=150)
    queja = discord.ui.TextInput(label="Sugerencias (opcional)", required=False, max_length=300)

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
        
        embed = discord.Embed(title="📝 **EVALUACIÓN REGISTRADA**", description=f"**Staff evaluado:** {self.staff.mention}", color=discord.Color.purple())
        embed.add_field(name="⭐ **Calificación**", value=f"{estrellas} ({nota}/10)", inline=False)
        embed.add_field(name="🤝 **Amabilidad**", value=self.amable.value, inline=False)
        embed.add_field(name="📌 **Acción**", value=self.que_hizo.value, inline=False)
        embed.add_field(name="💬 **Sugerencias**", value=self.queja.value or "Ninguna", inline=False)
        embed.set_footer(text=f"Evaluado por {interaction.user.name}")
        
        await interaction.response.send_message(content=f"{self.staff.mention} ¡Has recibido una evaluación! ⭐", embed=embed)
        await enviar_log(f"⭐ **{interaction.user.mention}** evaluó a **{self.staff.mention}** con nota {nota}/10", discord.Color.purple())

@bot.tree.command(name="evaluar_staff", description="⭐ Evaluar al staff")
@app_commands.describe(staff="Staff a evaluar")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvalModal(staff))

# ==================== ENVIAR MENSAJE ====================
@bot.tree.command(name="enviar", description="📢 Enviar un mensaje como el bot - SOLO ADMINS")
@app_commands.describe(
    titulo="El título del anuncio (opcional)",
    mensaje="El mensaje que quieres que el bot envíe",
    canal="El canal donde quieres enviarlo (opcional - por defecto el canal actual)",
    imagen_principal="Imagen grande - sube una imagen",
    imagen_miniatura="Imagen pequeña - sube una imagen",
    posicion_imagen="¿Dónde quieres la imagen principal?"
)
@app_commands.choices(
    posicion_imagen=[
        app_commands.Choice(name="📷 Abajo (principal)", value="abajo"),
        app_commands.Choice(name="📷 Arriba (miniatura)", value="arriba"),
        app_commands.Choice(name="📷 Ambas (principal + miniatura)", value="ambas"),
    ]
)
async def enviar_mensaje(
    interaction: discord.Interaction,
    mensaje: str,
    titulo: str = None,
    canal: discord.TextChannel = None,
    imagen_principal: discord.Attachment = None,
    imagen_miniatura: discord.Attachment = None,
    posicion_imagen: app_commands.Choice[str] = None
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Admins** pueden usar este comando.", ephemeral=True)
        return

    canal_destino = canal if canal else interaction.channel

    embed = discord.Embed(
        title=titulo if titulo else "📢 ANUNCIO OFICIAL",
        description=mensaje,
        color=discord.Color.gold()
    )
    embed.set_author(name="DISTRICT 99 - GVRP", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    embed.set_footer(text=f"Enviado por {interaction.user.name} • {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.display_avatar.url)

    if posicion_imagen:
        if posicion_imagen.value == "abajo" and imagen_principal:
            embed.set_image(url=imagen_principal.url)
        elif posicion_imagen.value == "arriba" and imagen_principal:
            embed.set_thumbnail(url=imagen_principal.url)
        elif posicion_imagen.value == "ambas":
            if imagen_principal:
                embed.set_image(url=imagen_principal.url)
            if imagen_miniatura:
                embed.set_thumbnail(url=imagen_miniatura.url)
    else:
        if imagen_principal:
            embed.set_image(url=imagen_principal.url)

    try:
        await canal_destino.send(embed=embed)
        await interaction.response.send_message(f"✅ **Mensaje enviado a {canal_destino.mention}**", ephemeral=True)
        await enviar_log(f"📢 **{interaction.user.mention}** envió un anuncio a {canal_destino.mention}", discord.Color.gold())
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al enviar el mensaje: {e}", ephemeral=True)

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
    
    embed = discord.Embed(title="📊 **ESTADÍSTICAS DEL BOT**", description=f"**{NOMBRE_SERVIDOR}**", color=discord.Color.blue())
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
                await message.channel.send(f"{user_mention} ✅ No tienes multas pendientes. ¡Estás al día!")
                await bot.process_commands(message)
                return
            
            if not oficial_id:
                for multa in historial:
                    if multa.get('infractor_id') == user_id and not multa.get('pagada', False) and multa.get('precio') == monto:
                        oficial_id = multa.get('oficial_id')
                        infraccion = multa.get('infraccion')
                        break
            
            await message.channel.send(f"{user_mention} ✅ He detectado tu pago de **${monto}**.\n⏳ Espera a que un oficial verifique y confirme el pago.")
            
            if oficial_id:
                await message.channel.send(f"👮 <@{oficial_id}> El ciudadano {user_mention} dice que pagó su multa de **${monto}**.\n📌 **Infracción:** {infraccion}\n✅ Verifica en UnbelievaBoat y usa `/confirmar_pago {user_name} {monto}`")
            else:
                await message.channel.send(f"📢 **ATENCIÓN POLICÍAS:** {user_mention} dice que pagó **${monto}**.\nVerifiquen en UnbelievaBoat y usen `/confirmar_pago {user_name} {monto}`")
            
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
