"""
Bot de Discord para servidor de rol (RP) — DISTRICT 99
CÓDIGO COMPLETO - PARTE 1/12
"""

import json
import os
import re
import asyncio
import math
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps
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
        # ==================== FUNCIÓN PARA GENERAR DNI ====================
async def generar_dni(usuario: discord.Member, datos_dni: dict):
    try:
        W, H = 1200, 750
        img = Image.new('RGB', (W, H), color=(15, 15, 18))
        draw = ImageDraw.Draw(img)

        BLANCO = (255, 255, 255)
        GRIS = (150, 155, 165)
        GRIS_LABEL = (140, 145, 155)
        VERDE = (60, 210, 130)
        LINEA = (48, 48, 55)

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

        try:
            font_title = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 34)
            font_sub = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 20)
            font_num = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 22)
            font_label = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 17)
            font_value = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 27)
            font_status = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 30)
            font_footer = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 15)
        except:
            font_title = font_sub = font_num = font_label = font_value = font_status = font_footer = ImageFont.load_default()

        draw.text((W // 2, 45), "DOCUMENTO NACIONAL DE IDENTIDAD", fill=BLANCO, font=font_title, anchor="mt")
        draw.text((W // 2, 90), "DISTRICT 99 - GVRP", fill=GRIS, font=font_sub, anchor="mt")

        numero_dni = datos_dni.get('numero_dni', '00000000')
        draw.text((W - 60, 55), f"DNI #{numero_dni}", fill=BLANCO, font=font_num, anchor="rt")

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
        except:
            pass
        draw.ellipse([avatar_x - 3, avatar_y - 3, avatar_x + avatar_size + 3, avatar_y + avatar_size + 3], outline=(70, 70, 78), width=3)

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

        barra_y1 = H - 115
        barra_y2 = H - 40
        draw.rounded_rectangle([40, barra_y1, W - 40, barra_y2], radius=14, fill=(24, 24, 28))
        cx_dot = W // 2 - 90
        cy_dot = (barra_y1 + barra_y2) // 2
        draw.ellipse([cx_dot - 14, cy_dot - 14, cx_dot + 14, cy_dot + 14], fill=VERDE)
        draw.text((cx_dot + 30, cy_dot), "VÁLIDO", fill=VERDE, font=font_status, anchor="lm")

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
        # ==================== CONFIGURACIÓN LICENCIA PREMIUM ====================
class LicenciaConfig:
    WIDTH = 1400
    HEIGHT = 900
    
    COLORES = {
        'fondo_principal': (248, 246, 242),
        'fondo_secundario': (238, 235, 228),
        'fondo_terciario': (225, 222, 215),
        'navy_oscuro': (12, 20, 40),
        'navy_medio': (25, 40, 70),
        'navy_claro': (45, 65, 105),
        'dorado_principal': (185, 150, 65),
        'dorado_claro': (215, 185, 110),
        'dorado_oscuro': (135, 105, 45),
        'texto_principal': (15, 20, 35),
        'texto_secundario': (80, 85, 95),
        'texto_terciario': (130, 135, 145),
        'verde_estado': (30, 160, 90),
        'verde_brillante': (60, 210, 130),
        'verde_oscuro': (20, 100, 60),
        'rojo_seguridad': (180, 40, 45),
        'azul_seguridad': (35, 80, 160),
        'blanco_puro': (255, 255, 255),
        'negro_puro': (0, 0, 0),
    }
    
    FUENTES = {
        'display': 'fonts/Montserrat-Bold.ttf',
        'display_light': 'fonts/Montserrat-Light.ttf',
        'body': 'fonts/Montserrat-Regular.ttf',
        'mono': 'fonts/JetBrainsMono-Regular.ttf',
    }
    
    FONT_SIZES = {
        'title': 48,
        'subtitle': 22,
        'header_label': 16,
        'header_value': 26,
        'body_label': 15,
        'body_value': 24,
        'footer_label': 14,
        'footer_value': 18,
        'mrz': 20,
        'watermark': 200,
    }
    # ==================== FUNCIÓN PARA GENERAR LICENCIA PREMIUM ====================
async def generar_licencia(usuario: discord.Member, datos_licencia: dict):
    try:
        # ========== CONFIGURACIÓN ==========
        W, H = 1100, 700
        img = Image.new('RGB', (W, H), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)

        # ========== PALETA DE COLORES ==========
        NAVY = (10, 25, 50)
        NAVY_CLARO = (25, 50, 95)
        NAVY_OSCURO = (5, 12, 30)
        DORADO = (200, 165, 90)
        DORADO_CLARO = (220, 195, 140)
        BLANCO = (255, 255, 255)
        GRIS = (140, 145, 155)
        GRIS_CLARO = (210, 215, 225)
        GRIS_OSCURO = (80, 85, 95)
        VERDE = (40, 200, 100)
        NEGRO = (15, 15, 20)
        CREMA = (248, 246, 242)

        # ========== FUENTES ==========
        try:
            font_title = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 36)
            font_subtitle = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 18)
            font_label = ImageFont.truetype("fonts/Montserrat-Medium.ttf", 14)
            font_value = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 22)
            font_small = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 12)
            font_serial = ImageFont.truetype("fonts/Montserrat-Medium.ttf", 16)
            font_mrz = ImageFont.truetype("fonts/JetBrainsMono-Regular.ttf", 18)
            font_watermark = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 180)
            font_estado = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 28)
        except:
            font_title = font_subtitle = font_label = font_value = font_small = font_serial = font_mrz = font_watermark = font_estado = ImageFont.load_default()

        # ========== EFECTO PVC: FONDO CON TEXTURA SUTIL ==========
        for i in range(H):
            factor = i / H
            r = int(240 - 8 * factor)
            g = int(240 - 8 * factor)
            b = int(245 - 12 * factor)
            draw.line([(0, i), (W, i)], fill=(r, g, b))

        # Ruido sutil (textura PVC)
        for _ in range(800):
            x = random.randint(0, W)
            y = random.randint(0, H)
            alpha = random.randint(0, 6)
            draw.point((x, y), fill=(200, 200, 210, alpha))

        # ========== BORDE PREMIUM CON SOMBRA ==========
        for i in range(8):
            offset = 12 - i
            draw.rectangle([offset, offset, W - offset, H - offset],
                          outline=(0, 0, 0, 15 - i*2), width=1)

        draw.rectangle([8, 8, W - 8, H - 8], outline=(220, 222, 228), width=1)
        draw.rectangle([12, 12, W - 12, H - 12], outline=(200, 202, 210), width=1)
        draw.rectangle([16, 16, W - 16, H - 16], outline=NAVY, width=3)
        draw.rectangle([22, 22, W - 22, H - 22], outline=DORADO, width=1)
        draw.rectangle([26, 26, W - 26, H - 26], outline=(230, 232, 238), width=1)

        # ========== REFLEJO PLÁSTICO ==========
        for i in range(30, 200, 3):
            alpha = int(12 * (1 - (i - 30) / 170))
            draw.line([(50, i), (W - 50, i)], fill=(255, 255, 255, alpha), width=1)

        # ========== WATERMARK SUTIL "99" ==========
        draw.text((W // 2 + 20, H // 2 + 30), "99",
                 fill=(225, 225, 235, 18), font=font_watermark, anchor="mm")

        # ========== HEADER: BANDA NAVY ==========
        header_y1 = 30
        header_y2 = 115
        draw.rectangle([26, header_y1, W - 26, header_y2], fill=NAVY)
        draw.line([26, header_y2, W - 26, header_y2], fill=DORADO, width=3)
        draw.line([26, header_y2 + 4, W - 26, header_y2 + 4], fill=DORADO_CLARO, width=1)

        # ========== ESCUDO ==========
        escudo_x, escudo_y = 55, 38
        escudo_size = 70

        draw.ellipse([escudo_x + 3, escudo_y + 3, escudo_x + escudo_size + 3, escudo_y + escudo_size + 3],
                    fill=(0, 0, 0, 20))

        draw.ellipse([escudo_x, escudo_y, escudo_x + escudo_size, escudo_y + escudo_size],
                    fill=DORADO_CLARO, outline=DORADO, width=3)

        draw.ellipse([escudo_x + 6, escudo_y + 6, escudo_x + escudo_size - 6, escudo_y + escudo_size - 6],
                    outline=BLANCO, width=1)

        draw.text((escudo_x + escudo_size // 2, escudo_y + escudo_size // 2 + 1),
                 "D99", fill=NAVY, font=font_title, anchor="mm")

        # ========== TÍTULO ==========
        titulo_x = escudo_x + escudo_size + 25
        draw.text((titulo_x, 42), "LICENCIA DE CONDUCIR", fill=BLANCO, font=font_title)
        draw.text((titulo_x, 82), "DISTRICT 99 - GVRP  •  DOCUMENTO OFICIAL",
                 fill=DORADO_CLARO, font=font_subtitle)

        # ========== NÚMERO DE LICENCIA ==========
        licencia_id = datos_licencia.get('licencia_id', 'LIC-0000')
        num_x = W - 180
        num_y = 38

        draw.rectangle([num_x - 20, num_y - 5, num_x + 160, num_y + 70],
                      fill=DORADO_CLARO, outline=DORADO, width=2)

        for i in range(0, 180, 3):
            draw.line([num_x - 20 + i, num_y - 5, num_x - 20 + i, num_y + 70],
                     fill=(240, 230, 210, 20), width=1)

        draw.text((num_x + 70, num_y + 15), f"#{licencia_id}",
                 fill=NAVY, font=font_serial, anchor="mt")
        draw.text((num_x + 70, num_y + 48), "VALID",
                 fill=DORADO, font=font_small, anchor="mt")

        # ========== LÍNEA SEPARADORA ==========
        draw.line([36, 145, W - 36, 145], fill=GRIS_CLARO, width=1)
        # ========== AVATAR DISCORD ==========
avatar_size = 185
avatar_x = 50
avatar_y = 170

draw.rectangle([avatar_x + 4, avatar_y + 4, avatar_x + avatar_size + 4, avatar_y + avatar_size + 4],
              fill=(0, 0, 0, 25))

draw.rounded_rectangle([avatar_x - 4, avatar_y - 4, avatar_x + avatar_size + 4, avatar_y + avatar_size + 4],
                      radius=12, outline=NAVY, width=3)
draw.rounded_rectangle([avatar_x - 1, avatar_y - 1, avatar_x + avatar_size + 1, avatar_y + avatar_size + 1],
                      radius=10, outline=DORADO, width=1)

try:
    avatar_response = requests.get(usuario.display_avatar.url, timeout=5)
    avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
    avatar_img = avatar_img.resize((avatar_size, avatar_size))

    mask = Image.new('L', (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, avatar_size, avatar_size), radius=10, fill=255)

    avatar_recortado = Image.new('RGBA', (avatar_size, avatar_size))
    avatar_recortado.paste(avatar_img, (0, 0), mask)
    img.paste(avatar_recortado, (avatar_x, avatar_y), avatar_recortado)

except:
    draw.rounded_rectangle([avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size],
                          radius=10, fill=GRIS_CLARO,
                          outline=NAVY, width=2)

# ========== NOMBRE ==========
nombre_completo = f"{datos_licencia.get('nombre', '')} {datos_licencia.get('apellidos', '')}".upper()
nombre_x = avatar_x + avatar_size + 35
nombre_y = 175

draw.text((nombre_x, nombre_y), "NOMBRE COMPLETO",
         fill=GRIS, font=font_label)
draw.text((nombre_x, nombre_y + 24), nombre_completo,
         fill=NAVY, font=font_title)

# ========== ESTADO ==========
estado_x = nombre_x + 300
estado_y = 175

draw.ellipse([estado_x + 2, estado_y + 4, estado_x + 18, estado_y + 20],
            fill=VERDE)

draw.text((estado_x + 28, estado_y + 6), "ESTADO: ACTIVA",
         fill=VERDE, font=font_estado)

# ========== LÍNEA SEPARADORA ==========
draw.line([nombre_x, 230, W - 36, 230], fill=GRIS_CLARO, width=1)

# ========== TABLA DE DATOS ==========
col1_x = nombre_x
col2_x = nombre_x + 280
y_start = 250
row_height = 52

campos = [
    ("FECHA NACIMIENTO", datos_licencia.get('fecha_nacimiento', '')),
    ("EDAD", f"{datos_licencia.get('edad', '')} AÑOS"),
    ("OFICIO", datos_licencia.get('oficio', '')),
    ("DNI", datos_licencia.get('dni', '')),
    ("LICENCIA", licencia_id),
    ("EXPEDICIÓN", datos_licencia.get('fecha_expedicion', '')),
    ("EXPIRACIÓN", datos_licencia.get('fecha_expiracion', '')),
]

for i, (label, value) in enumerate(campos):
    if i < 4:
        x = col1_x
    else:
        x = col2_x

    y = y_start + (i % 4) * row_height

    draw.text((x, y), label, fill=GRIS, font=font_label)
    draw.text((x, y + 20), value, fill=NAVY, font=font_value)

    if i < 3:
        draw.line([x, y + 46, x + 260, y + 46], fill=GRIS_CLARO, width=1)

# ========== MICROTEXTO ==========
texto_seguridad = "DISTRICT99 GVRP • DOCUMENTO OFICIAL • VALID LICENSE • "
texto_repetido = (texto_seguridad * 20)[:600]
draw.text((50, H - 50), texto_repetido, fill=(200, 200, 210, 60), font=font_small)
    # ========== FOOTER ==========
    footer_y1 = H - 70
    footer_y2 = H - 20

    draw.rectangle([26, footer_y1, W - 26, footer_y2], fill=NAVY)
    draw.line([26, footer_y1, W - 26, footer_y1], fill=DORADO, width=2)

    # ========== CÓDIGO DE BARRAS ==========
    bar_x = 50
    bar_y = footer_y1 + 12
    bar_w = 140
    bar_h = 30

    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                  fill=BLANCO, outline=(200, 200, 200), width=1)

    for i in range(0, bar_w, 3):
        h = random.randint(10, bar_h)
        draw.rectangle([bar_x + i, bar_y + (bar_h - h),
                       bar_x + i + 1, bar_y + bar_h],
                      fill=NAVY)

    # ========== MRZ ==========
    mrz_x = bar_x + bar_w + 30
    mrz_y = footer_y1 + 18

    nombre = datos_licencia.get('nombre', '').upper()[:15].ljust(15)
    apellido = datos_licencia.get('apellidos', '').upper()[:15].ljust(15)
    dni = datos_licencia.get('dni', '').zfill(8)

    mrz_texto = f"D99<{apellido}<{nombre}<{dni}<<{licencia_id[-6:]}<<<<"
    mrz_texto = mrz_texto[:44].ljust(44)

    draw.text((mrz_x, mrz_y), mrz_texto,
             fill=BLANCO, font=font_mrz)

    # ========== SELLO ==========
    sello_x = W - 170
    sello_y = footer_y1 + 8

    draw.ellipse([sello_x, sello_y, sello_x + 55, sello_y + 55],
                outline=DORADO, width=2, fill=NAVY)
    draw.ellipse([sello_x + 5, sello_y + 5, sello_x + 50, sello_y + 50],
                outline=DORADO_CLARO, width=1)
    draw.text((sello_x + 28, sello_y + 28), "✓",
             fill=DORADO, font=font_serial, anchor="mm")
    draw.text((sello_x + 28, sello_y + 48), "VALID",
             fill=DORADO_CLARO, font=font_small, anchor="mm")

    # ========== FIRMA ==========
    firma = f"{datos_licencia.get('nombre', '')[:1]}{datos_licencia.get('apellidos', '')[:1]} - {datos_licencia.get('dni', '')[-4:]}"
    draw.text((W - 60, footer_y1 + 12), f"__________________ {firma}",
             fill=BLANCO, font=font_small, anchor="rt")

    # ========== QR ==========
    qr_x = W - 340
    qr_y = footer_y1 + 8
    qr_size = 38

    draw.rectangle([qr_x, qr_y, qr_x + qr_size, qr_y + qr_size],
                  fill=BLANCO, outline=GRIS_CLARO, width=1)

    for i in range(0, qr_size, 5):
        for j in range(0, qr_size, 5):
            if (i + j) % 7 == 0 or (i * j) % 13 == 0:
                draw.rectangle([qr_x + i, qr_y + j, qr_x + i + 3, qr_y + j + 3],
                              fill=NAVY)

    for cx, cy in [(qr_x + 2, qr_y + 2), (qr_x + qr_size - 8, qr_y + 2), (qr_x + 2, qr_y + qr_size - 8)]:
        draw.rectangle([cx, cy, cx + 6, cy + 6], fill=NAVY)

    # ========== HOLOGRAMA ==========
    holo_x = W - 110
    holo_y = H - 110
    holo_size = 65

    for i in range(holo_size):
        for j in range(holo_size):
            if (i + j) % 3 == 0:
                r = int(180 + 60 * math.sin(i / 10))
                g = int(200 + 55 * math.sin(j / 10 + 1))
                b = int(220 + 35 * math.sin((i + j) / 12 + 2))
                draw.point((holo_x + i, holo_y + j), fill=(r, g, b, 30))

    draw.ellipse([holo_x - 2, holo_y - 2, holo_x + holo_size + 2, holo_y + holo_size + 2],
                outline=DORADO, width=1)

    draw.text((holo_x + holo_size // 2, holo_y + holo_size // 2),
             "D99", fill=(255, 255, 255, 40), font=font_watermark, anchor="mm")

    # ========== GUARDAR ==========
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG', quality=98)
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
            nombre = discord.ui.TextInput(label="Nombre", placeholder="Ej: Juan", max_length=50, required=True)
            apellidos = discord.ui.TextInput(label="Apellidos", placeholder="Ej: Pérez García", max_length=50, required=True)
            fecha_nacimiento = discord.ui.TextInput(label="📅 Fecha Nacimiento (DD/MM/YYYY)", placeholder="Ej: 15/05/1998 (Edad automática)", max_length=10, required=True)
            oficio = discord.ui.TextInput(label="Oficio", placeholder="Ej: Conductor", max_length=50, required=True)
            user_roblox = discord.ui.TextInput(label="Usuario Roblox", placeholder="Ej: Juanito_99", max_length=50, required=True)

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

                    embed = discord.Embed(title="🪪 **DNI GENERADO**", description=f"{modal_interaction.user.mention}", color=discord.Color.blue())
                    embed.set_image(url="attachment://dni.png")
                    embed.add_field(name="📌 ¿Dónde se envió?", value=f"Este DNI se ha enviado al canal <#{CANAL_REGISTRO_DNI_ID}>", inline=False)
                    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")

                    canal_dni = bot.get_channel(CANAL_REGISTRO_DNI_ID)
                    if canal_dni:
                        await canal_dni.send(content=f"📢 **Nuevo DNI generado para {modal_interaction.user.mention}**", embed=embed, file=archivo_dni)
                        await modal_interaction.response.send_message(f"✅ **¡DNI creado exitosamente!**\nSe ha enviado al canal <#{CANAL_REGISTRO_DNI_ID}>.", ephemeral=True)
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
            fecha_nacimiento = discord.ui.TextInput(label="📅 Fecha Nacimiento (DD/MM/YYYY)", placeholder="Ej: 15/05/1998 (Edad automática)", max_length=10, required=True)
            oficio = discord.ui.TextInput(label="Oficio", placeholder="Ej: Conductor", max_length=50, required=True)
            user_roblox = discord.ui.TextInput(label="Usuario Roblox", placeholder="Ej: Juanito_99", max_length=50, required=True)

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

                    embed = discord.Embed(title="🪪 **LICENCIA GENERADA**", description=f"{modal_interaction.user.mention}", color=discord.Color.gold())
                    embed.set_image(url="attachment://licencia.png")
                    embed.add_field(name="📌 ¿Dónde se envió?", value=f"Esta licencia se ha enviado al canal <#{CANAL_REGISTRO_LICENCIAS_ID}>", inline=False)
                    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")

                    canal_registro = bot.get_channel(CANAL_REGISTRO_LICENCIAS_ID)
                    if canal_registro:
                        await canal_registro.send(content=f"📢 **Nueva licencia generada para {modal_interaction.user.mention}**", embed=embed, file=archivo_licencia)
                        await modal_interaction.response.send_message(f"✅ **¡Licencia creada exitosamente!**\nSe ha enviado al canal <#{CANAL_REGISTRO_LICENCIAS_ID}>.", ephemeral=True)
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

    @discord.ui.select(placeholder="🚔 Selecciona una opción", options=[
        discord.SelectOption(label="🚔 Iniciar Turno", value="iniciar", emoji="🚔"),
        discord.SelectOption(label="🛑 Finalizar Turno", value="finalizar", emoji="🛑"),
        discord.SelectOption(label="📋 Turnos Activos", value="activos", emoji="📋"),
    ])
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
            
            turnos[user_id] = {"policia_id": user_id, "policia_nombre": str(interaction.user), "inicio": datetime.now(timezone.utc).isoformat(), "activo": True, "tipo": "wsp"}
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(title="🚔 **TURNO INICIADO**", description=f"{interaction.user.mention} ha comenzado su patrullaje.", color=discord.Color.green())
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
            
            embed = discord.Embed(title="🚔 **TURNO FINALIZADO**", description=f"{interaction.user.mention} ha terminado su patrullaje.", color=discord.Color.red())
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
                    activos.append({"nombre": turno["policia_nombre"], "id": user_id, "horas": horas, "minutos": minutos})
            
            if not activos:
                await interaction.response.send_message("📋 No hay policias en servicio.", ephemeral=True)
                return
            
            embed = discord.Embed(title="🚓 **POLICIAS EN SERVICIO**", description=f"Total: {len(activos)} oficiales", color=discord.Color.blue())
            for policia in activos:
                embed.add_field(name=f"👮 {policia['nombre']}", value=f"🕐 {policia['horas']}h {policia['minutos']}m activo", inline=False)
            embed.set_image(url=URL_IMG_WSP)
            await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== PANEL DE EMS ====================
class PanelEMSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="🚑 Selecciona una opción", options=[
        discord.SelectOption(label="🚨 Iniciar Servicio", value="iniciar", emoji="🚨"),
        discord.SelectOption(label="🛑 Finalizar Servicio", value="finalizar", emoji="🛑"),
        discord.SelectOption(label="📋 EMS Activos", value="activos", emoji="📋"),
    ])
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
            
            turnos[user_id] = {"usuario_id": user_id, "usuario_nombre": str(interaction.user), "inicio": datetime.now(timezone.utc).isoformat(), "activo": True, "tipo": "ems"}
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(title="🚑 **SERVICIO DE EMS INICIADO**", description=f"{interaction.user.mention} ha comenzado su servicio.", color=discord.Color.green())
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
            
            embed = discord.Embed(title="🚑 **SERVICIO DE EMS FINALIZADO**", description=f"{interaction.user.mention} ha terminado su servicio.", color=discord.Color.red())
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
                    activos.append({"nombre": turno["usuario_nombre"], "id": user_id, "horas": horas, "minutos": minutos})
            
            if not activos:
                await interaction.response.send_message("📋 No hay EMS en servicio.", ephemeral=True)
                return
            
            embed = discord.Embed(title="🚑 **EMS EN SERVICIO**", description=f"Total: {len(activos)} personal médico", color=discord.Color.green())
            for ems in activos:
                embed.add_field(name=f"🚑 {ems['nombre']}", value=f"🕐 {ems['horas']}h {ems['minutos']}m activo", inline=False)
            embed.set_image(url=URL_IMG_EMS)
            await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== PANEL DE DOT ====================
class PanelDOTView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="🚦 Selecciona una opción", options=[
        discord.SelectOption(label="🚦 Iniciar Servicio", value="iniciar", emoji="🚦"),
        discord.SelectOption(label="🛑 Finalizar Servicio", value="finalizar", emoji="🛑"),
        discord.SelectOption(label="📋 DOT Activos", value="activos", emoji="📋"),
    ])
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
            
            turnos[user_id] = {"usuario_id": user_id, "usuario_nombre": str(interaction.user), "inicio": datetime.now(timezone.utc).isoformat(), "activo": True, "tipo": "dot"}
            guardar(TURNOS_FILE, turnos)
            
            embed = discord.Embed(title="🚦 **SERVICIO DE DOT INICIADO**", description=f"{interaction.user.mention} ha comenzado su servicio.", color=discord.Color.green())
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
            
            embed = discord.Embed(title="🚦 **SERVICIO DE DOT FINALIZADO**", description=f"{interaction.user.mention} ha terminado su servicio.", color=discord.Color.red())
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
                    activos.append({"nombre": turno["usuario_nombre"], "id": user_id, "horas": horas, "minutos": minutos})
            
            if not activos:
                await interaction.response.send_message("📋 No hay DOT en servicio.", ephemeral=True)
                return
            
            embed = discord.Embed(title="🚦 **DOT EN SERVICIO**", description=f"Total: {len(activos)} personal de tránsito", color=discord.Color.green())
            for dot in activos:
                embed.add_field(name=f"🚦 {dot['nombre']}", value=f"🕐 {dot['horas']}h {dot['minutos']}m activo", inline=False)
            embed.set_image(url=URL_IMG_DOT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # ==================== COMANDOS DE PANELES ====================
@bot.tree.command(name="panel_dni", description="🪪 Panel para crear DNI - SOLO ADMIN/HOST")
async def panel_dni(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(title="🪪 **PANEL DE DNI**", description=(
        "Presiona el botón para crear tu **Documento Nacional de Identidad**.\n\n"
        "📝 **Crear DNI** → Completa el formulario y genera tu DNI.\n\n"
        "⚠️ **Requisitos:**\n"
        "• No debes tener un DNI previo.\n"
        "• Solo puedes tener **UN** DNI por persona.\n\n"
        "📌 **Importante:**\n"
        "• Este DNI es **personal e intransferible**.\n"
        "• La edad se calcula automáticamente.\n\n"
        "🖼️ **Tu DNI se generará automáticamente** y se enviará al canal de registro."
    ), color=discord.Color.blue())
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    await interaction.response.send_message(embed=embed, view=PanelDNIView())

@bot.tree.command(name="panel_licencias", description="📋 Panel para solicitar licencias - SOLO ADMIN/HOST")
async def panel_licencias(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(title="📋 **PANEL DE LICENCIAS**", description=(
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
    ), color=discord.Color.gold())
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    await interaction.response.send_message(embed=embed, view=PanelLicenciasView())

@bot.tree.command(name="panel_wsp", description="📋 Panel para gestionar turnos de policía - SOLO ADMIN/HOST")
async def panel_wsp(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(title="🚔 **PANEL DE WSP**", description=(
        "Selecciona una opción del menú para gestionar tu patrullaje.\n\n"
        "🚔 **Iniciar Turno** → Comienza tu patrullaje.\n"
        "🛑 **Finalizar Turno** → Termina tu patrullaje.\n"
        "📋 **Turnos Activos** → Ver policías en servicio.\n\n"
        "⚠️ **Requisitos:** Debes tener el rol **Wsp│👮** para usar estas opciones.\n"
        "🔒 **Privacidad:** Las respuestas solo las verás tú.\n"
        f"🔄 **Rol automático:** Al iniciar turno, se te asignará el rol **{ROL_TRABAJANDO_NOMBRE}**."
    ), color=discord.Color.blue())
    embed.set_image(url=URL_IMG_WSP)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    await interaction.response.send_message(embed=embed, view=PanelWSPView())

@bot.tree.command(name="panel_ems", description="🚑 Panel para gestionar servicios de EMS - SOLO ADMIN/HOST")
async def panel_ems(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(title="🚑 **PANEL DE EMS**", description=(
        "Selecciona una opción del menú para gestionar tu servicio de emergencias.\n\n"
        "🚨 **Iniciar Servicio** → Comienza tu servicio de EMS.\n"
        "🛑 **Finalizar Servicio** → Termina tu servicio.\n"
        "📋 **EMS Activos** → Ver personal médico en servicio.\n\n"
        "⚠️ **Requisitos:** Debes tener el rol **Ems│🚑** para usar estas opciones.\n"
        "🔒 **Privacidad:** Las respuestas solo las verás tú.\n"
        f"🔄 **Rol automático:** Al iniciar servicio, se te asignará el rol **{ROL_TRABAJANDO_NOMBRE}**."
    ), color=discord.Color.green())
    embed.set_image(url=URL_IMG_EMS)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    await interaction.response.send_message(embed=embed, view=PanelEMSView())

@bot.tree.command(name="panel_dot", description="🚦 Panel para gestionar servicios de DOT - SOLO ADMIN/HOST")
async def panel_dot(interaction: discord.Interaction):
    if not es_host(interaction.user) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo **Hosts y Admins** pueden usar este comando.", ephemeral=True)
        return
    
    embed = discord.Embed(title="🚦 **PANEL DE DOT**", description=(
        "Selecciona una opción del menú para gestionar tu servicio de tránsito.\n\n"
        "🚦 **Iniciar Servicio** → Comienza tu servicio de DOT.\n"
        "🛑 **Finalizar Servicio** → Termina tu servicio.\n"
        "📋 **DOT Activos** → Ver personal de tránsito en servicio.\n\n"
        "⚠️ **Requisitos:** Debes tener el rol **Dot│🚧** para usar estas opciones.\n"
        "🔒 **Privacidad:** Las respuestas solo las verás tú.\n"
        f"🔄 **Rol automático:** Al iniciar servicio, se te asignará el rol **{ROL_TRABAJANDO_NOMBRE}**."
    ), color=discord.Color.orange())
    embed.set_image(url=URL_IMG_DOT)
    embed.set_footer(text="DISTRICT 99 - GVRP © 2026")
    await interaction.response.send_message(embed=embed, view=PanelDOTView())
    # ==================== COMANDOS DE MULTAS ====================
@bot.tree.command(name="registrar_multa", description="🚨 Registrar multa - SOLO POLICIA")
@app_commands.describe(infractor="Usuario", infraccion="Infraccion", precio="Monto", testigos="Testigos (opcional)", foto="Foto (opcional)")
async def registrar_multa(interaction: discord.Interaction, infractor: discord.Member, infraccion: str, precio: str, testigos: str = None, foto: discord.Attachment = None):
    if not es_policia(interaction.user):
        return await interaction.response.send_message("⛔ Solo POLICIA", ephemeral=True)
    if not precio.isdigit():
        return await interaction.response.send_message("⚠️ Monto: numero", ephemeral=True)
    
    testigos_mentions = []
    if testigos:
        for uid in re.findall(r'<@!?(\d+)>', testigos):
            try:
                testigos_mentions.append((await bot.fetch_user(int(uid))).mention)
            except:
                pass
    
    multas = cargar(MULTAS_FILE)
    multas.setdefault("historial", []).append({
        "oficial_id": str(interaction.user.id), "oficial": str(interaction.user),
        "infractor_id": str(infractor.id), "infractor": str(infractor),
        "infraccion": infraccion, "precio": int(precio), "pagada": False,
        "testigos": testigos_mentions, "foto": foto.url if foto else None,
        "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
    })
    guardar(MULTAS_FILE, multas)
    
    embed = discord.Embed(title="🚨 MULTA REGISTRADA", color=discord.Color.red())
    embed.add_field(name="👮 Oficial", value=interaction.user.mention)
    embed.add_field(name="👤 Infractor", value=infractor.mention)
    embed.add_field(name="⚖️ Infracción", value=infraccion)
    embed.add_field(name="💰 Monto", value=f"**${precio}**")
    if testigos_mentions:
        embed.add_field(name="👀 Testigos", value=", ".join(testigos_mentions))
    if foto:
        embed.set_image(url=foto.url)
    await interaction.response.send_message(content=f"{infractor.mention} ¡Multa! Paga en <#{CANAL_PAGOS_ID}> con `!pay {precio}`", embed=embed)
    await enviar_log(f"🚨 {interaction.user.mention} multó a {infractor.mention} por ${precio}", discord.Color.red())

@bot.tree.command(name="historial_multas", description="📋 Ver historial - SOLO POLICIA")
@app_commands.describe(usuario="Usuario (opcional)")
async def historial_multas(interaction: discord.Interaction, usuario: discord.Member = None):
    if not es_policia(interaction.user):
        return await interaction.response.send_message("⛔ Solo POLICIA", ephemeral=True)
    historial = cargar(MULTAS_FILE).get("historial", [])
    if usuario:
        historial = [m for m in historial if m.get('infractor_id') == str(usuario.id)]
        if not historial:
            return await interaction.response.send_message(f"📋 {usuario.name} no tiene multas", ephemeral=True)
    embed = discord.Embed(title=f"📋 MULTAS", color=discord.Color.red())
    for i, m in enumerate(historial[-10:], 1):
        embed.add_field(name=f"#{i}", value=f"👮 {m['oficial']}\n⚖️ {m['infraccion']}\n💰 ${m['precio']}\n{'✅ Pagada' if m.get('pagada') else '❌ Sin pagar'}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mis_multas", description="📋 Tus multas")
async def mis_multas(interaction: discord.Interaction):
    historial = cargar(MULTAS_FILE).get("historial", [])
    mis = [m for m in historial if m.get('infractor_id') == str(interaction.user.id)]
    if not mis:
        return await interaction.response.send_message("📋 No tienes multas", ephemeral=True)
    embed = discord.Embed(title=f"🚨 TUS MULTAS ({len(mis)})", color=discord.Color.orange())
    total = 0
    for i, m in enumerate(mis[-10:], 1):
        total += m.get('precio', 0)
        embed.add_field(name=f"#{i}", value=f"👮 {m['oficial']}\n⚖️ {m['infraccion']}\n💰 ${m['precio']}\n{'✅ Pagada' if m.get('pagada') else '❌ Sin pagar'}", inline=False)
    embed.add_field(name="💸 TOTAL", value=f"**${total}**")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="confirmar_pago", description="👮 Confirmar pago - SOLO POLICIA")
@app_commands.describe(usuario="Usuario", monto="Monto")
async def confirmar_pago(interaction: discord.Interaction, usuario: str, monto: int):
    if not es_policia(interaction.user):
        return await interaction.response.send_message("⛔ Solo POLICIA", ephemeral=True)
    miembro = None
    if usuario.startswith('<@'):
        miembro = interaction.guild.get_member(int(usuario.replace('<@', '').replace('>', '').replace('!', '')))
    if not miembro:
        for m in interaction.guild.members:
            if m.name.lower() == usuario.lower() or m.display_name.lower() == usuario.lower():
                miembro = m; break
    if not miembro:
        return await interaction.response.send_message(f"⚠️ No encontré a `{usuario}`", ephemeral=True)
    
    historial = cargar(MULTAS_FILE).get("historial", [])
    for i, m in enumerate(historial):
        if m.get('infractor_id') == str(miembro.id) and not m.get('pagada') and m.get('precio') == monto:
            historial[i]['pagada'] = True
            historial[i]['fecha_pago'] = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
            guardar(MULTAS_FILE, {"historial": historial})
            embed = discord.Embed(title="💰 PAGO CONFIRMADO", description=f"{miembro.mention} pagó ${monto}", color=discord.Color.green())
            embed.add_field(name="👮 Confirmado por", value=interaction.user.mention)
            await interaction.response.send_message(embed=embed)
            await enviar_log(f"💰 {miembro.mention} pagó ${monto} (Confirmado por {interaction.user.mention})", discord.Color.green())
            return
    await interaction.response.send_message(f"⚠️ No encontré multa de ${monto} para {miembro.mention}", ephemeral=True)

# ==================== COMANDOS DE AUTOS ====================
@bot.tree.command(name="registrar_auto", description="🚗 Registrar auto con foto")
@app_commands.describe(usuario_roblox="Usuario Roblox", placa="Placa", modelo="Modelo", color="Color", foto="Foto")
async def registrar_auto(interaction: discord.Interaction, usuario_roblox: str, placa: str, modelo: str, color: str, foto: discord.Attachment):
    if not foto.content_type or not foto.content_type.startswith('image/'):
        return await interaction.response.send_message("⚠️ Debe ser imagen", ephemeral=True)
    autos = cargar(AUTOS_FILE)
    autos.setdefault(str(interaction.user.id), []).append({"usuario_discord": str(interaction.user), "usuario_roblox": usuario_roblox, "placa": placa, "modelo": modelo, "color": color, "foto": foto.url, "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y")})
    guardar(AUTOS_FILE, autos)
    embed = discord.Embed(title="🚗 VEHÍCULO REGISTRADO", color=discord.Color.green())
    embed.add_field(name="👤 Usuario", value=interaction.user.mention)
    embed.add_field(name="📋 Modelo", value=modelo, inline=True)
    embed.add_field(name="🎨 Color", value=color, inline=True)
    embed.add_field(name="🅿️ Placa", value=placa, inline=True)
    embed.set_image(url=foto.url)
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🚗 {interaction.user.mention} registró {placa}", discord.Color.green())

@bot.tree.command(name="ver_autos", description="🚗 Ver autos de usuario")
@app_commands.describe(usuario="Usuario (opcional)")
async def ver_autos(interaction: discord.Interaction, usuario: discord.Member = None):
    objetivo = usuario or interaction.user
    autos = cargar(AUTOS_FILE).get(str(objetivo.id), [])
    if not autos:
        return await interaction.response.send_message(f"❌ {objetivo.name} no tiene autos", ephemeral=True)
    embed = discord.Embed(title=f"🚗 AUTOS DE {objetivo.name.upper()}", color=discord.Color.blue())
    for i, a in enumerate(autos, 1):
        embed.add_field(name=f"🚘 Auto #{i}", value=f"🎮 {a['usuario_roblox']}\n📋 {a['modelo']}\n🎨 {a['color']}\n🅿️ {a['placa']}", inline=False)
        if a.get('foto'):
            embed.set_image(url=a['foto'])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="eliminar_auto", description="🗑️ Eliminar auto")
@app_commands.describe(numero_auto="Número del auto")
async def eliminar_auto(interaction: discord.Interaction, numero_auto: int):
    autos = cargar(AUTOS_FILE)
    user_id = str(interaction.user.id)
    if user_id not in autos or not autos[user_id]:
        return await interaction.response.send_message("❌ No tienes autos", ephemeral=True)
    if numero_auto < 1 or numero_auto > len(autos[user_id]):
        return await interaction.response.send_message(f"⚠️ Tienes {len(autos[user_id])} autos", ephemeral=True)
    eliminado = autos[user_id].pop(numero_auto - 1)
    guardar(AUTOS_FILE, autos)
    embed = discord.Embed(title="🗑️ AUTO ELIMINADO", description=f"{interaction.user.mention} eliminó su auto.", color=discord.Color.red())
    embed.add_field(name="📋 Modelo", value=eliminado.get('modelo', 'Desconocido'))
    embed.add_field(name="🅿️ Placa", value=eliminado.get('placa', 'Desconocida'))
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"🗑️ {interaction.user.mention} eliminó {eliminado.get('placa', 'N/A')}", discord.Color.red())
    # ==================== SESIONES ====================
@bot.tree.command(name="abrir_sesion", description="🎬 Abrir sesión - SOLO HOSTS")
@app_commands.choices(ciudad=[app_commands.Choice(name="🌆 Greenville", value="greenville"), app_commands.Choice(name="🌆 Horton", value="horton"), app_commands.Choice(name="🌆 Brookmere", value="brookmere")], vias=[app_commands.Choice(name="1 Vía", value="1"), app_commands.Choice(name="2 Vías", value="2")], adelantamientos=[app_commands.Choice(name="✅ Sí", value="si"), app_commands.Choice(name="❌ No", value="no")])
async def abrir_sesion(interaction: discord.Interaction, ciudad: app_commands.Choice[str], vias: app_commands.Choice[str], velocidad_maxima: str, adelantamientos: app_commands.Choice[str], link: str, velocidad_frp: str = None):
    if not es_host(interaction.user):
        return await interaction.response.send_message("⛔ Solo HOSTS", ephemeral=True)
    if not velocidad_maxima.isdigit() or (velocidad_frp and not velocidad_frp.isdigit()):
        return await interaction.response.send_message("⚠️ Velocidad debe ser número", ephemeral=True)
    if adelantamientos.value == "si":
        class AdelantoModal(discord.ui.Modal, title="🚀 Velocidad Adelantamiento"):
            vel = discord.ui.TextInput(label="Velocidad (mph)", placeholder="100", max_length=10)
            async def on_submit(self, modal: discord.Interaction):
                if not self.vel.value.isdigit():
                    return await modal.response.send_message("⚠️ Número", ephemeral=True)
                await enviar_sesion(modal, ciudad.value, vias.value, velocidad_maxima, adelantamientos.value, link, self.vel.value, velocidad_frp)
        return await interaction.response.send_modal(AdelantoModal())
    await enviar_sesion(interaction, ciudad.value, vias.value, velocidad_maxima, adelantamientos.value, link, None, velocidad_frp)

async def enviar_sesion(i, ciudad, vias, vel_max, adel, link, vel_adel=None, vel_frp=None):
    escenas = cargar(ESCENAS_FILE)
    if str(i.channel_id) in escenas:
        return await i.response.send_message("⚠️ Ya hay sesión", ephemeral=True)
    escenas[str(i.channel_id)] = {"ciudad": ciudad, "vias": vias, "velocidad_maxima": vel_max, "adelantamientos": adel == "si", "velocidad_adelanto": vel_adel or "No aplica", "velocidad_frp": vel_frp or "No especificada", "link_servidor": link, "host": str(i.user), "host_id": str(i.user.id), "inicio": datetime.now(timezone.utc).isoformat()}
    guardar(ESCENAS_FILE, escenas)
    embed = discord.Embed(title="🏁 SESIÓN ABIERTA", description=f"**{NOMBRE_SERVIDOR}**", color=discord.Color.gold()).set_image(url=URL_SESION_ABIERTA)
    detalles = f"🌆 {ciudad.capitalize()}\n🛣️ {vias} vías\n🚗 {vel_max} mph\n🚨 {vel_frp or 'No especificada'} mph\n🏁 {'✅ Permitidos' if adel == 'si' else '❌ No permitidos'}"
    if adel == "si" and vel_adel:
        detalles += f"\n🚀 {vel_adel} mph"
    embed.add_field(name="📋 DETALLES", value=f"{detalles}\n👑 {i.user.mention}\n🔗 [🌐 Haz clic]({link})")
    canal = bot.get_channel(CANAL_SESIONES_ID)
    if canal:
        await canal.send(embed=embed)
        await i.response.send_message("✅ Sesión enviada!", ephemeral=True)
    else:
        await i.response.send_message("❌ No encontré canal", ephemeral=True)
    await enviar_log(f"🎬 {i.user.mention} abrió sesión", discord.Color.gold())

@bot.tree.command(name="cerrar_sesion", description="🔒 Cerrar sesión - SOLO HOSTS")
async def cerrar_sesion(interaction: discord.Interaction):
    if not es_host(interaction.user):
        return await interaction.response.send_message("⛔ Solo HOSTS", ephemeral=True)
    escenas = cargar(ESCENAS_FILE)
    cid = str(interaction.channel_id)
    if cid not in escenas:
        return await interaction.response.send_message("❌ No hay sesión", ephemeral=True)
    escena = escenas[cid]
    duracion = datetime.now(timezone.utc) - datetime.fromisoformat(escena["inicio"])
    h, r = divmod(int(duracion.total_seconds()), 3600)
    m = r // 60
    del escenas[cid]
    guardar(ESCENAS_FILE, escenas)
    embed = discord.Embed(title="🔒 SESIÓN CERRADA", description=f"**¡Buen rol!** 👏\n⏱️ {h}h {m}m", color=discord.Color.red()).set_image(url=URL_SESION_CERRADA_NUEVA)
    canal = bot.get_channel(CANAL_SESIONES_ID)
    if canal:
        await canal.send(embed=embed)
        await interaction.response.send_message("✅ Sesión cerrada!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No encontré canal", ephemeral=True)
    await enviar_log(f"🔒 {interaction.user.mention} cerró sesión ({h}h {m}m)", discord.Color.red())

# ==================== EVALUAR STAFF ====================
class EvalModal(discord.ui.Modal, title="⭐ Evaluar Staff"):
    que_hizo = discord.ui.TextInput(label="¿Qué hizo?", max_length=200)
    calificacion = discord.ui.TextInput(label="Calificación (1-10)", max_length=2)
    amable = discord.ui.TextInput(label="¿Fue amable?", max_length=150)
    queja = discord.ui.TextInput(label="Sugerencias (opcional)", required=False, max_length=300)
    def __init__(self, staff): super().__init__(); self.staff = staff
    async def on_submit(self, i):
        try:
            nota = int(self.calificacion.value.strip())
            if not 1 <= nota <= 10: raise ValueError
        except:
            return await i.response.send_message("⚠️ Calificación 1-10", ephemeral=True)
        evals = cargar(EVALUACIONES_FILE)
        evals.setdefault(str(self.staff.id), []).append({"staff_id": str(self.staff.id), "staff": str(self.staff), "evaluador_id": str(i.user.id), "evaluador": str(i.user), "que_hizo": self.que_hizo.value, "calificacion": nota, "amable": self.amable.value, "queja": self.queja.value or "Ninguna", "fecha": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")})
        guardar(EVALUACIONES_FILE, evals)
        embed = discord.Embed(title="📝 EVALUACIÓN", description=f"**Staff:** {self.staff.mention}", color=discord.Color.purple())
        embed.add_field(name="⭐ Calificación", value=f"{'⭐'*round(nota/2)} ({nota}/10)")
        embed.add_field(name="🤝 Amabilidad", value=self.amable.value)
        embed.add_field(name="📌 Acción", value=self.que_hizo.value)
        await i.response.send_message(content=f"{self.staff.mention} ¡Evaluación! ⭐", embed=embed)
        await enviar_log(f"⭐ {i.user.mention} evaluó a {self.staff.mention} con {nota}/10", discord.Color.purple())

@bot.tree.command(name="evaluar_staff", description="⭐ Evaluar staff")
async def evaluar_staff(interaction: discord.Interaction, staff: discord.Member):
    await interaction.response.send_modal(EvalModal(staff))
    # ==================== ENVIAR MENSAJE ====================
@bot.tree.command(name="enviar", description="📢 Enviar mensaje - SOLO ADMINS")
@app_commands.choices(posicion_imagen=[app_commands.Choice(name="📷 Abajo", value="abajo"), app_commands.Choice(name="📷 Arriba", value="arriba"), app_commands.Choice(name="📷 Ambas", value="ambas")])
async def enviar_mensaje(interaction: discord.Interaction, mensaje: str, titulo: str = None, canal: discord.TextChannel = None, imagen_principal: discord.Attachment = None, imagen_miniatura: discord.Attachment = None, posicion_imagen: app_commands.Choice[str] = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("⛔ Solo Admins", ephemeral=True)
    destino = canal or interaction.channel
    embed = discord.Embed(title=titulo or "📢 ANUNCIO OFICIAL", description=mensaje, color=discord.Color.gold())
    embed.set_author(name="DISTRICT 99 - GVRP", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    if posicion_imagen:
        if posicion_imagen.value == "abajo" and imagen_principal:
            embed.set_image(url=imagen_principal.url)
        elif posicion_imagen.value == "arriba" and imagen_principal:
            embed.set_thumbnail(url=imagen_principal.url)
        elif posicion_imagen.value == "ambas":
            if imagen_principal: embed.set_image(url=imagen_principal.url)
            if imagen_miniatura: embed.set_thumbnail(url=imagen_miniatura.url)
    elif imagen_principal:
        embed.set_image(url=imagen_principal.url)
    await destino.send(embed=embed)
    await interaction.response.send_message(f"✅ Enviado a {destino.mention}", ephemeral=True)
    await enviar_log(f"📢 {interaction.user.mention} envió anuncio a {destino.mention}", discord.Color.gold())

# ==================== STATS ====================
@bot.tree.command(name="stats", description="📊 Estadísticas - SOLO ADMINS")
async def stats(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("⛔ Solo Admins", ephemeral=True)
    dnis = cargar(DNI_FILE); lic = cargar(LICENCIAS_FILE); multas = cargar(MULTAS_FILE); autos = cargar(AUTOS_FILE); escenas = cargar(ESCENAS_FILE); evals = cargar(EVALUACIONES_FILE)
    h = multas.get("historial", [])
    embed = discord.Embed(title="📊 ESTADÍSTICAS", description=f"**{NOMBRE_SERVIDOR}**", color=discord.Color.blue())
    embed.add_field(name="🪪 DNIs", value=str(len(dnis)), inline=True)
    embed.add_field(name="🪪 Licencias", value=str(len(lic)), inline=True)
    embed.add_field(name="🚗 Autos", value=str(sum(len(v) for v in autos.values())), inline=True)
    embed.add_field(name="🚨 Multas", value=str(len(h)), inline=True)
    embed.add_field(name="✅ Pagadas", value=str(sum(1 for m in h if m.get('pagada'))), inline=True)
    embed.add_field(name="❌ Pendientes", value=str(len(h) - sum(1 for m in h if m.get('pagada'))), inline=True)
    embed.add_field(name="🎬 Sesiones", value=str(len(escenas)), inline=True)
    embed.add_field(name="⭐ Evaluaciones", value=str(len(evals)), inline=True)
    await interaction.response.send_message(embed=embed)
    await enviar_log(f"📊 {interaction.user.mention} usó /stats", discord.Color.blue())

# ==================== ON_MESSAGE (pay) ====================
@bot.event
async def on_message(message):
    if message.author.id == bot.user.id or message.channel.id != CANAL_PAGOS_ID:
        return await bot.process_commands(message)
    if message.content.lower().startswith("!pay"):
        parts = message.content.split()
        monto = next((int(p) for p in parts if p.isdigit()), None)
        if not monto:
            return await bot.process_commands(message)
        user_id, mention, name = str(message.author.id), message.author.mention, message.author.name
        historial = cargar(MULTAS_FILE).get("historial", [])
        for m in historial:
            if m.get('infractor_id') == user_id and not m.get('pagada') and m.get('precio') == monto:
                await message.channel.send(f"{mention} ✅ Pago de ${monto} detectado. Espera confirmación.")
                await message.channel.send(f"👮 <@{m.get('oficial_id')}> {mention} pagó ${monto}. Usa `/confirmar_pago {name} {monto}`")
                return await bot.process_commands(message)
        await message.channel.send(f"{mention} ✅ No tienes multas de ${monto}")
    await bot.process_commands(message)

# ==================== INICIAR BOT ====================
print("🚀 Intentando conectar...")
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback; traceback.print_exc()
