# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
from io import BytesIO
from flask import send_file

# Python encoding ayarları
if sys.platform.startswith('win'):
    # Windows'ta encoding ayarları
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        except:
            pass
    
    # Console encoding'i UTF-8 yap
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Environment variables for encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import traceback
from datetime import datetime, timezone, timedelta
import json
import hashlib
import warnings
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# Redis import'u kaldırıldı - artık kullanılmıyor
from flask_mail import Mail, Message
import re
import unicodedata
import socket
from functools import wraps

# LDAP3 import - IIS'te sorun çıkarabilir, güvenli import
try:
    from ldap3 import Server, Connection, ALL, NTLM, SIMPLE
    LDAP3_AVAILABLE = True
except ImportError as e:
    print(f"⚠ LDAP3 kütüphanesi yüklenemedi: {e}")
    print("  Active Directory entegrasyonu devre dışı olacak.")
    LDAP3_AVAILABLE = False
    # Dummy değerler
    Server = Connection = ALL = NTLM = SIMPLE = None

# Türkiye timezone'u tanımla (UTC+3)
TURKEY_TZ = timezone(timedelta(hours=3))

# Flask-Limiter uyarısını bastır (geliştirme ortamı için)
warnings.filterwarnings("ignore", message="Using the in-memory storage")

load_dotenv()

app = Flask(__name__)
# Static folder ayarı - PDF dosyaları için
app = Flask(__name__, static_folder='public', static_url_path='/public')

# CORS Ayarları - Ortama göre
from flask_cors import CORS
import os

def configure_cors():
    environment = os.getenv('FLASK_ENV', 'development')
    if environment == 'production':
        # Canlı domainler izinli
        CORS(app, origins=[
            'https://mastermatch.doquhome.com.tr',
            'https://devmastermatch.doquhome.com.tr'
        ], supports_credentials=True)
    else:
        # Geliştirme ortamı - localhost ve dev domain izinli
        CORS(app, origins=[
            'http://localhost:3000',
            'https://devmastermatch.doquhome.com.tr'
        ], supports_credentials=True)

configure_cors()

# Veritabanı Yapılandırması
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Eğer DATABASE_URL yoksa SQLite kullan (geliştirme için)
    database_url = 'sqlite:///app.db'
# Sessiz moda alındı
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Rate Limiting Konfigürasyonu - In-memory storage kullan
def create_limiter():
    """In-memory rate limiter oluşturur"""
    environment = os.getenv('FLASK_ENV', 'development')
    
    if environment == 'production':
        # Canlı ortam - In-memory storage kullan
        return Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["500 per day", "50 per hour", "5 per minute"]
        )
    else:
        # Geliştirme ortamı - Rate limiting devre dışı
        return Limiter(
            app=app,
            key_func=get_remote_address,
            enabled=False  # Rate limiting tamamen kapalı
        )

limiter = create_limiter()

# .env'den SMTP ve mail ayarlarını oku
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.office365.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
MAIL_BCC_LIST = os.getenv('MAIL_BCC_LIST', '')
MAIL_REPLY_TO = os.getenv('MAIL_REPLY_TO', app.config['MAIL_DEFAULT_SENDER'])

mail = Mail(app)

IADE_PROSEDURU_METNI = """DOQU HOME KOŞULSUZ İADE GARANTİSİ

Doqu Home, Yastıklarda "100 gece Koşulsuz İade Garantisi" sunmaktadır. Bu garanti, satın alınan ürünün teslim tarihinden itibaren başlar.

İade/Değişim prosedürü şu şekildedir:

1) Deneme Süresi: Ürünü teslim aldığınız tarihten itibaren 100 gece deneme hakkınız bulunmaktadır.
Koşulsuz iadenin geçerli olması için doquhome.com.tr web sitesinde bulunan "Master Match Yastık Seçim Robotu" web sayfasından kişiye özel ürün seçiminin tamamlanması gereklidir.

2) Garanti Kaydı: Koşulsuz iade garantisinin geçerli olması için ürün satın alındıktan sonra ürün teslim tarihinden itibaren 30 gün sonrasında ve en geç 100 gün içerisinde doquhome.com.tr web sitesinde bulunan "%100 Koşulsuz İade Garantisi" sayfasındaki formun doldurulması gerekmektedir. Bu formun doldurulmaması durumunda koşulsuz iade garantisi geçerli olmayacaktır. İade talebi için doldurulan form ve Master Match yastık seçim robotu tarafından kişiye gönderilen sonuç mail çıktısıyla birlikte iade edilecek bayiye gidilerek ürün iadesi yapılmalıdır. Web sitesi üzerinden yapılan alışverişlerde iade formu doldurulduktan sonra ürün Doqu A.Ş. fabrikaya karşı ödemeli olarak kargo edilmelidir.

3) İade/Değişim Talebi: Deneme süresi içinde üründen memnun kalmamanız durumunda 3. maddede belirtilen şartların karşılanması halinde iade veya değişim talebinde bulunabilirsiniz. Öncelikli olarak değişim tavsiye edilir, ancak tüketici iade talebinde de bulunabilir.

4) Online Alışverişlerde Değişim: Online alışverişlerde 100 gece deneme kapsamında değişim ve iade hakkı bulunur. Online değişimde, kalan tutar hediye çeki olarak yüklenir ve para iadesi yapılmaz.

5) Ürün Koşulları: İade veya değişim yapılacak ürünün bazı koşulları karşılaması gerekmektedir. Kullanım esnasında yırtılmış, sıvı teması olmuş, yanmış ya da aksesuarları hasar görmüş ürünler iade alınmaz.

6) Kapsam Dışı Ürün ve Durumlar: Outlet ve teşhir ürünleri kampanya kapsamı dışındadır. Otel, yurt, misafirhane ve ticari işletmeler gibi toplu satışlar kampanya kapsamına dâhil değildir. E-ticaret pazaryerlerinden veya yurt dışından yapılan alışverişler bu kampanyaya dâhil değildir.

7) Ücret ve Kesintiler: İade/değişimde kargo bedeli alıcıya aittir. İlk değişim talebinde herhangi bir ücret kesintisi yapılmayacaktır. İkinci ve üçüncü değişim talebinde ürün bedelinden %50 ücret kesintisi yapılacaktır. Değişim talebi yılda 3 ürünle sınırlı olacaktır. Değişim sonrası satın alınan ürün için değişim işlemleri yapılırken değiştirilmek istenen ürünün satın alındığı dönemdeki fiyatı geçerli olacaktır. Yeni alınacak ürün için güncel fiyat geçerli olacaktır. Yeni alınan ürün ücreti daha yüksek ise tüketici tarafından fark ödemesi yapılacaktır. Değişim sonucunda yeni alınan ürün değiştirilmek istenen üründen daha ucuz ise satış noktası müşteriye ilk ödeme yöntemi ne ise o şekilde geri ödeme yapacaktır.

8) Değişim Hizmet Bedeli: Ürünün 100 gece içerisinde değiştirilmesi durumunda tüketici değişim hizmet bedeli olarak ürünün perakende satış fiyatının %10'u kadar hizmet bedeli ödemesini satış noktasına yapacaktır. İade alınan ürünler İstikbal, Bellona, Mondihome mağazalarından aldığında satın aldıkları mağazadan, doquhome.com.tr web sitemizden yapılan alışveriş iadelerinde ise Doqu Home genel merkeze kargo ile iade işlemi yapacaktır.

9) Hediye ve Promosyonlar: Ürünün hediyesi veya promosyonu var ise, değişim yapılacak üründe hediye verilmez. Hediye olarak alışverişten sonra verilen yastıklar koşulsuz iade kapsamında değildir.

10) Geçerlilik Alanı: Kampanya İstikbal, Bellona, Mondihome ve Doqu Home mağazaları, bellona.com.tr ve www.doquhome.com.tr üzerinden yapılan alışverişlerde geçerlidir.

11) Koşulsuz iade geçerliliği olan ürünler: Koşulsuz iade garantisi Master Match yastık seçim robotunda tanımlı bulunan ve sistemin önerdiği yastıklarla sınırlıdır.

Bu garanti, Doqu Home'un ürünlerine duyduğu güveni temsil eder.
"""


def _resolve_pdf_font_path():
    """Türkçe karakter destekleyen bir TTF font yolu bulur."""
    candidates = [
        r'C:\Windows\Fonts\arial.ttf',
        r'C:\Windows\Fonts\calibri.ttf',
        r'C:\Windows\Fonts\tahoma.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def build_iade_proseduru_pdf_bytes(text=None):
    """İade prosedürü metninden PDF (bytes) üretir."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm

    content = (text or IADE_PROSEDURU_METNI).strip()
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    font_name = 'Helvetica'
    font_path = _resolve_pdf_font_path()
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('IadeFont', font_path))
            font_name = 'IadeFont'
        except Exception as font_err:
            print(f"PDF font yükleme uyarısı: {font_err}")

    left = 2 * cm
    right = page_width - 2 * cm
    top = page_height - 2 * cm
    bottom = 2 * cm
    max_width = right - left
    line_height = 14
    y = top

    def draw_wrapped_line(raw_line, size=10, leading=None):
        nonlocal y
        leading = leading or (size + 4)
        c.setFont(font_name, size)
        words = (raw_line or '').split(' ')
        if not words or (len(words) == 1 and words[0] == ''):
            y -= leading
            if y < bottom:
                c.showPage()
                c.setFont(font_name, size)
                y = top
            return

        current = ''
        for word in words:
            candidate = word if not current else f'{current} {word}'
            if c.stringWidth(candidate, font_name, size) <= max_width:
                current = candidate
            else:
                if y < bottom:
                    c.showPage()
                    c.setFont(font_name, size)
                    y = top
                c.drawString(left, y, current)
                y -= leading
                current = word
        if current:
            if y < bottom:
                c.showPage()
                c.setFont(font_name, size)
                y = top
            c.drawString(left, y, current)
            y -= leading

    lines = content.split('\n')
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if idx == 0 and stripped:
            draw_wrapped_line(stripped, size=14, leading=20)
            y -= 6
        elif not stripped:
            y -= 8
            if y < bottom:
                c.showPage()
                y = top
        else:
            draw_wrapped_line(stripped, size=10, leading=line_height)

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _is_knee_pillow_name(name: str) -> bool:
    n = (name or '').lower()
    return ('diz arası' in n) or ('diz arasi' in n)


def _fetch_image_bytes(url_or_path, timeout=8):
    """Ürün görselini URL veya yerel yoldan okur."""
    if not url_or_path:
        return None
    try:
        src = str(url_or_path).strip()
        if src.startswith('http://') or src.startswith('https://'):
            import urllib.request
            import ssl
            req = urllib.request.Request(src, headers={'User-Agent': 'MasterMatchPDF/1.0'})
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.read()
        # Yerel dosya / relative path
        candidates = [
            src,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), src),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', os.path.basename(src)),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'public', os.path.basename(src)),
        ]
        for path in candidates:
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    return f.read()
    except Exception as img_err:
        print(f"PDF görsel okunamadı ({url_or_path}): {img_err}")
    return None


def build_recommendation_pdf_bytes(recommendations):
    """Önerilen yastık listesinden görselli PDF (bytes) üretir."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.utils import ImageReader

    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    font_name = 'Helvetica'
    font_path = _resolve_pdf_font_path()
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('OneriFont', font_path))
            font_name = 'OneriFont'
        except Exception as font_err:
            print(f"Öneri PDF font yükleme uyarısı: {font_err}")

    left = 1.6 * cm
    right = page_width - 1.6 * cm
    top = page_height - 1.4 * cm
    bottom = 1.8 * cm
    content_width = right - left
    accent = HexColor('#1f4e79')
    muted = HexColor('#6b7280')
    card_border = HexColor('#e5e7eb')
    card_bg = HexColor('#f8fafc')
    link_color = HexColor('#0b6e99')

    tarih_str = datetime.now().strftime('%d.%m.%Y')
    y = top

    # Sağ üst tarih
    c.setFont(font_name, 9)
    c.setFillColor(muted)
    date_label = f'Tarih: {tarih_str}'
    c.drawRightString(right, y, date_label)
    y -= 10

    # Başlık bloğu
    c.setFillColor(accent)
    c.setFont(font_name, 18)
    c.drawCentredString(page_width / 2, y - 6, 'MASTER MATCH')
    y -= 26
    c.setFont(font_name, 13)
    c.drawCentredString(page_width / 2, y, 'YASTIK ÖNERİ SONUCU')
    y -= 12
    c.setStrokeColor(HexColor('#d1d5db'))
    c.setLineWidth(0.8)
    c.line(left, y, right, y)
    y -= 16

    c.setFillColor(HexColor('#374151'))
    c.setFont(font_name, 10)
    intro = 'Master Match Yastık Seçim Robotu yanıtlarınıza göre size önerilen yastıklar aşağıdadır.'
    # basit wrap
    words = intro.split(' ')
    line = ''
    for word in words:
        candidate = word if not line else f'{line} {word}'
        if c.stringWidth(candidate, font_name, 10) <= content_width:
            line = candidate
        else:
            c.drawString(left, y, line)
            y -= 13
            line = word
    if line:
        c.drawString(left, y, line)
        y -= 18

    c.setFillColor(accent)
    c.setFont(font_name, 12)
    c.drawString(left, y, 'Önerilen Ürünler')
    y -= 14

    products = []
    for yastik in recommendations or []:
        name = (yastik.get('isim') or '').strip()
        if not name or _is_knee_pillow_name(name):
            continue
        products.append({
            'isim': name,
            'link': (yastik.get('link') or '').strip(),
            'gorsel': (yastik.get('gorsel') or '').strip(),
        })

    img_size = 2.4 * cm
    row_h = 3.0 * cm
    text_x = left + img_size + 0.55 * cm

    def new_page():
        nonlocal y
        c.showPage()
        y = top
        c.setFont(font_name, 9)
        c.setFillColor(muted)
        c.drawRightString(right, y, date_label)
        y -= 18

    if not products:
        c.setFillColor(muted)
        c.setFont(font_name, 10)
        c.drawString(left, y, 'Önerilen ürün bulunamadı.')
        y -= 16
    else:
        for idx, item in enumerate(products, start=1):
            if y - row_h < bottom:
                new_page()

            # Kart arka planı
            card_bottom = y - row_h + 0.25 * cm
            c.setFillColor(card_bg)
            c.setStrokeColor(card_border)
            c.setLineWidth(0.7)
            c.roundRect(left, card_bottom, content_width, row_h - 0.2 * cm, 6, fill=1, stroke=1)

            # Görsel kutusu
            img_x = left + 0.28 * cm
            img_y = card_bottom + (row_h - 0.2 * cm - img_size) / 2
            img_bytes = _fetch_image_bytes(item['gorsel'])
            if img_bytes:
                try:
                    reader = ImageReader(BytesIO(img_bytes))
                    c.drawImage(
                        reader,
                        img_x,
                        img_y,
                        width=img_size,
                        height=img_size,
                        preserveAspectRatio=True,
                        mask='auto',
                        anchor='c'
                    )
                except Exception as draw_err:
                    print(f"PDF görsel çizilemedi: {draw_err}")
                    c.setFillColor(white)
                    c.setStrokeColor(card_border)
                    c.rect(img_x, img_y, img_size, img_size, fill=1, stroke=1)
            else:
                c.setFillColor(white)
                c.setStrokeColor(card_border)
                c.rect(img_x, img_y, img_size, img_size, fill=1, stroke=1)
                c.setFillColor(muted)
                c.setFont(font_name, 8)
                c.drawCentredString(img_x + img_size / 2, img_y + img_size / 2 - 3, 'Görsel yok')

            # Ürün adı
            name_y = card_bottom + row_h - 1.05 * cm
            c.setFillColor(HexColor('#111827'))
            c.setFont(font_name, 11)
            name_text = f'{idx}. {item["isim"]}'
            max_name_w = right - text_x - 0.3 * cm
            # taşarsa kısalt
            if c.stringWidth(name_text, font_name, 11) > max_name_w:
                while name_text and c.stringWidth(name_text + '…', font_name, 11) > max_name_w:
                    name_text = name_text[:-1]
                name_text = name_text.rstrip() + '…'
            c.drawString(text_x, name_y, name_text)

            # Tıklanabilir "Ürünü İncele" (uzun URL yazılmaz)
            if item['link']:
                link_label = 'Ürünü İncele →'
                c.setFillColor(link_color)
                c.setFont(font_name, 10)
                link_y = name_y - 18
                c.drawString(text_x, link_y, link_label)
                link_w = c.stringWidth(link_label, font_name, 10)
                c.linkURL(
                    item['link'],
                    (text_x, link_y - 2, text_x + link_w + 2, link_y + 11),
                    relative=0
                )
                c.setStrokeColor(link_color)
                c.setLineWidth(0.6)
                c.line(text_x, link_y - 1, text_x + link_w, link_y - 1)

            y = card_bottom - 0.35 * cm

    if y - 40 < bottom:
        new_page()

    y -= 8
    c.setFillColor(HexColor('#374151'))
    c.setFont(font_name, 10)
    c.drawString(left, y, 'Eğer memnun kalmazsanız 100 gün içinde kolayca değiştirebilirsiniz.')
    y -= 18
    c.setFillColor(muted)
    c.setFont(font_name, 8)
    c.drawString(left, y, 'Bu belge Master Match Yastık Seçim Robotu sonuç çıktısıdır. Doqu Home')

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def build_recommendation_mail_html(recommendations, logo_cid=None):
    """Soru/cevap ve mükemmel eşleşme olmadan, iade belgesi tarzı mail HTML'i üretir."""
    def normalize(s: str) -> str:
        return (s or '').lower()

    def is_knee_pillow(name: str) -> bool:
        return _is_knee_pillow_name(name)

    tarih_str = datetime.now().strftime('%d.%m.%Y')
    tarih_saat_str = datetime.now().strftime('%d.%m.%Y %H:%M')

    product_rows = []
    for yastik in recommendations or []:
        name = yastik.get('isim') or 'Yastık'
        if is_knee_pillow(name):
            continue
        img = yastik.get('gorsel') or ''
        href = yastik.get('link') or ''

        img_html = ''
        if img:
            img_tag = f'<img src="{img}" alt="{name}" style="width:72px;height:72px;object-fit:contain;border:1px solid #eee;border-radius:6px;background:#fff;"/>'
            if href:
                img_html = f'<a href="{href}" target="_blank" rel="noopener noreferrer">{img_tag}</a>'
            else:
                img_html = img_tag
        else:
            img_html = '<div style="width:72px;height:72px;border:1px solid #eee;border-radius:6px;background:#f7f7f7;"></div>'

        name_html = f'<a href="{href}" target="_blank" rel="noopener noreferrer" style="color:#1f2d3d;text-decoration:none;font-weight:600;">{name}</a>' if href else f'<span style="font-weight:600;color:#1f2d3d;">{name}</span>'

        product_rows.append(f'''
        <tr>
          <td style="padding:10px 8px;border-bottom:1px solid #ececec;width:84px;vertical-align:middle;">{img_html}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #ececec;vertical-align:middle;font-size:15px;">{name_html}</td>
        </tr>
        ''')

    products_section = ''.join(product_rows) if product_rows else '''
        <tr><td colspan="2" style="padding:12px;color:#666;">Önerilen ürün bulunamadı.</td></tr>
    '''

    if logo_cid:
        logo_html = f'<img src="cid:{logo_cid}" alt="Master Match / Doqu Home" style="max-width:220px;height:auto;margin:0 auto 10px;display:block;"/>'
    else:
        logo_html = ''

    return f'''
    <div style="font-family:Arial,Helvetica,sans-serif;color:#222;max-width:680px;margin:0 auto;line-height:1.55;">
      <div style="text-align:center;margin:8px 0 18px;">
        {logo_html}
        <div style="font-size:22px;font-weight:700;letter-spacing:0.5px;">MASTER MATCH</div>
        <div style="font-size:18px;font-weight:700;margin-top:4px;">YASTIK ÖNERİ SONUCU</div>
      </div>

      <p style="margin:0 0 10px;"><b>Tarih:</b> {tarih_str}</p>

      <p style="margin:0 0 12px;">
        İhtiyaçlarınızı anlamak ve size en uygun yastığı önerebilmek için geliştirilen
        <b>Master Match Yastık Seçim Robotu</b> uygulamasını doğru ve eksiksiz tamamladığınız için teşekkür ederiz.
        Master Match sorularına verdiğiniz yanıtlar doğrultusunda önerdiğimiz yastıklar ek olarak gönderilmiştir.
      </p>
      <p style="margin:0 0 18px;">
        Size önerilen yastıkları inceleyebilir, dilediğiniz yastığı tercih edebilirsiniz.
      </p>

      <p style="margin:18px 0 10px;">
        Eğer memnun kalmazsanız <b>100 gün</b> içinde kolayca değiştirebilirsiniz.
      </p>

      <div style="margin-top:18px;padding:12px 14px;background:#f5f8fb;border:1px solid #d9e4ef;border-radius:8px;font-size:13px;">
        <b>Bilgi:</b> Önerilen yastık listesi ve Doqu Home Koşulsuz İade Garantisi / iade prosedürü bu e-postaya <b>PDF ek</b> olarak gönderilmiştir.
        İade işlemlerinde ekteki sonuç çıktısını ve prosedürü kullanabilirsiniz.
      </div>
    </div>
    '''


def get_mail_logo_bytes():
    """Mail için logo dosyasını okur."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'welcomelogo.png'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'src', 'assets', 'welcomelogo.png'),
    ]
    for path in candidates:
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read()
        except Exception:
            continue
    return None


# Mail gönderme fonksiyonu
def send_analysis_email(email, mail_content, from_address=None, bcc_emails=None, attachments=None, inline_images=None):
    try:
        msg = Message(
            subject='Master Match Yastık Öneri Sonucu - Doqu Home',
            sender=from_address or app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        # reply_to güvenli ayarla
        try:
            if MAIL_REPLY_TO and (' ' not in MAIL_REPLY_TO) and ('@' in MAIL_REPLY_TO):
                msg.reply_to = MAIL_REPLY_TO
        except Exception:
            pass
        # BCC env'den veya parametreden
        bcc_final = bcc_emails or MAIL_BCC_LIST
        if bcc_final:
            msg.bcc = [e.strip() for e in bcc_final.split(';') if e.strip()]

        msg.html = mail_content

        # Inline görseller: [(cid, filename, content_bytes, mime_type), ...]
        for item in (inline_images or []):
            try:
                cid, filename, content, mime_type = item
                msg.attach(
                    filename,
                    mime_type,
                    content,
                    'inline',
                    headers={'Content-ID': f'<{cid}>', 'X-Attachment-Id': cid}
                )
            except Exception as attach_err:
                print(f"Mail inline görsel hatası: {attach_err}")

        # Ek dosyalar: [(filename, content_bytes, mime_type), ...]
        for item in (attachments or []):
            try:
                filename, content, mime_type = item
                msg.attach(filename, mime_type, content)
            except Exception as attach_err:
                print(f"Mail ek dosya hatası: {attach_err}")

        mail.send(msg)
        return True, None
    except Exception as e:
        print(f"Mail gönderme hatası: {e}")
        traceback.print_exc()
        return False, str(e)

def sanitize_email(raw_email: str) -> str:
    """E‑posta için unicode normalizasyonu ve görünmez boşluk temizliği uygular."""
    if not raw_email:
        return ''
    # Unicode normalize
    normalized = unicodedata.normalize('NFKC', str(raw_email))
    # Zero-width ve NBSP dahil tüm beyaz boşluk karakterlerini standart boşluğa indir
    normalized = ''.join(ch if not ch.isspace() else ' ' for ch in normalized)
    # Trim
    normalized = normalized.strip()
    # Yaygın görünmez karakterleri at
    normalized = normalized.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '').replace('\xa0', '')
    return normalized.strip()

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# Admin credentials (production'da environment variable'dan alınmalı)
# Admin panel credentials - .env'den oku
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Güvenlik kontrolü
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("ADMIN_USERNAME ve ADMIN_PASSWORD environment variables zorunludur!")

# Active Directory ayarları
AD_ENABLED = os.getenv('AD_ENABLED', 'False').lower() == 'true'
AD_SERVER = os.getenv('AD_SERVER', '')
AD_PORT = int(os.getenv('AD_PORT', 389))
AD_USE_SSL = os.getenv('AD_USE_SSL', 'False').lower() == 'true'
AD_USE_TLS = os.getenv('AD_USE_TLS', 'True').lower() == 'true'
AD_DOMAIN = os.getenv('AD_DOMAIN', '')
AD_BASE_DN = os.getenv('AD_BASE_DN', '')
AD_AUTHORIZED_GROUP = os.getenv('AD_AUTHORIZED_GROUP', '')

def authenticate_with_ad(username, password):
    """
    Active Directory ile kullanıcı doğrulama
    Returns: (success: bool, message: str, user_info: dict)
    """
    try:
        if not LDAP3_AVAILABLE:
            return False, "LDAP3 kütüphanesi yüklü değil. Active Directory devre dışı.", {}
        
        # Ayarları veritabanından oku
        ad_settings = get_ad_settings()
        
        if not ad_settings['enabled']:
            return False, "AD authentication devre dışı", {}
        
        if not ad_settings['server'] or not ad_settings['domain'] or not ad_settings['base_dn']:
            return False, "AD konfigürasyonu eksik", {}
        
        # AD sunucusuna bağlan
        server = Server(ad_settings['server'], port=ad_settings['port'], use_ssl=ad_settings['use_ssl'], get_info=ALL)
        
        # Farklı authentication yöntemleri dene
        conn = None
        last_error = None
        
        # 1. Yöntem: User Principal Name (UPN) - SIMPLE auth
        try:
            user_principal = f"{username}@{ad_settings['domain']}"
            print(f"Deneniyor: SIMPLE auth - {user_principal}")
            conn = Connection(server, user=user_principal, password=password, authentication=SIMPLE, auto_bind=True)
            print("✓ SIMPLE authentication başarılı")
        except Exception as e1:
            print(f"SIMPLE auth başarısız: {e1}")
            last_error = e1
            
            # 2. Yöntem: Domain\Username - NTLM auth (MD4 hatası olabilir)
            try:
                user_dn = f"{ad_settings['domain']}\\{username}"
                print(f"Deneniyor: NTLM auth - {user_dn}")
                conn = Connection(server, user=user_dn, password=password, authentication=NTLM, auto_bind=True)
                print("✓ NTLM authentication başarılı")
            except Exception as e2:
                print(f"NTLM auth başarısız: {e2}")
                # Her iki yöntem de başarısız
                if 'md4' in str(e2).lower():
                    raise Exception("MD4 hash desteklenmiyor. Python/OpenSSL güncellenmeli veya SIMPLE auth etkinleştirilmeli.")
                else:
                    raise e2
        
        if not conn:
            raise last_error or Exception("AD bağlantısı kurulamadı")
        
        # Kullanıcı bilgilerini al
        conn.search(
            search_base=ad_settings['base_dn'],
            search_filter=f"(sAMAccountName={username})",
            search_scope='SUBTREE',
            attributes=['cn', 'mail', 'memberOf', 'sAMAccountName']
        )
        
        if conn.entries:
            user_entry = conn.entries[0]
            user_info = {
                'username': str(user_entry.sAMAccountName),
                'full_name': str(user_entry.cn),
                'email': str(user_entry.mail) if user_entry.mail else '',
                'groups': [str(group) for group in user_entry.memberOf] if user_entry.memberOf else []
            }
            
            # Yetkili grup kontrolü (eğer belirtilmişse)
            if ad_settings['authorized_group']:
                # Grup listesinde tam eşleşme veya kısmi eşleşme kontrolü
                is_authorized = False
                for group in user_info['groups']:
                    if ad_settings['authorized_group'].lower() in group.lower():
                        is_authorized = True
                        break
                
                if not is_authorized:
                    conn.unbind()
                    return False, "Bu kullanıcının admin paneline erişim yetkisi yok", {}
            
            conn.unbind()
            return True, "Giriş başarılı", user_info
        else:
            conn.unbind()
            return False, "Kullanıcı bulunamadı", {}
            
    except Exception as e:
        error_msg = str(e).lower()
        print(f"AD authentication hatası: {e}")
        print(f"Hata tipi: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Kullanıcı dostu hata mesajları
        if 'invalidcredentials' in error_msg or 'invalid credentials' in error_msg:
            return False, "Kullanıcı adı veya şifre hatalı", {}
        elif 'server' in error_msg or 'connection' in error_msg:
            return False, "Active Directory sunucusuna bağlanılamıyor", {}
        elif 'ldap3' in error_msg.lower() or 'module' in error_msg.lower():
            return False, f"LDAP3 modül hatası: {str(e)}", {}
        else:
            # Detaylı hata mesajı döndür (debugging için)
            return False, f"AD hatası: {str(e)}", {}

def authenticate_user(username, password):
    """
    Kullanıcı doğrulama - AD veya basit authentication
    Returns: (success: bool, message: str, user_info: dict)
    """
    # Ayarları veritabanından oku
    ad_settings = get_ad_settings()
    
    if ad_settings['enabled']:
        return authenticate_with_ad(username, password)
    else:
        # Basit authentication - .env veya veritabanından
        admin_user = get_setting('ADMIN_USERNAME', ADMIN_USERNAME)
        admin_pass = get_setting('ADMIN_PASSWORD', ADMIN_PASSWORD)
        
        if username == admin_user and password == admin_pass:
            return True, "Giriş başarılı", {'username': username, 'full_name': 'Admin'}
        else:
            return False, "Geçersiz kullanıcı adı veya şifre", {}

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header gerekli'}), 401
        
        try:
            # Basic auth format: "Basic base64(username:password)"
            auth_type, auth_string = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return jsonify({'error': 'Basic authentication gerekli'}), 401
            
            import base64
            decoded = base64.b64decode(auth_string).decode('utf-8')
            username, password = decoded.split(':', 1)
            
            # Yeni authentication sistemi kullan
            success, message, user_info = authenticate_user(username, password)
            if not success:
                return jsonify({'error': message}), 401
                
        except Exception as e:
            return jsonify({'error': 'Geçersiz authorization formatı'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_email_domain(email):
    """
    Email domain'inin gerçek olup olmadığını kontrol et
    MX record veya A record varsa geçerli domain
    """
    try:
        domain = email.split('@')[1]
        
        # MX record kontrolü (mail sunucusu var mı?)
        try:
            socket.getaddrinfo(domain, 'smtp', socket.AF_UNSPEC, socket.SOCK_STREAM)
            return True, None
        except socket.gaierror:
            pass
        
        # A record kontrolü (domain var mı?)
        try:
            socket.gethostbyname(domain)
            return True, None
        except socket.gaierror:
            return False, f"Domain '{domain}' bulunamadı veya geçersiz."
    
    except Exception as e:
        # Hata durumunda geçerli kabul et (çok katı olmasın)
        return True, None

# --- Veritabanı Modelleri ---
class KvkkMetin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosya_adi = db.Column(db.String(200), nullable=False)
    versiyon = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(64), nullable=False)  # SHA256 hash
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(TURKEY_TZ))
    icerik = db.Column(db.UnicodeText, nullable=False)

class KvkkOnay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, nullable=False)
    kvkk_metin_id = db.Column(db.Integer, nullable=False)
    ip_adresi = db.Column(db.String(50))
    onay_tarihi = db.Column(db.DateTime, default=lambda: datetime.now(TURKEY_TZ))
    onay_durumu = db.Column(db.String(10), default='1')
    onay_yontemi = db.Column(db.String(50), default='popup')

class Yastik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(150), nullable=False)
    gorsel = db.Column(db.String(250))
    link = db.Column(db.String(250))
    sertlik = db.Column(db.String(50))  # Yastık sertliği (ideal_sertlik sorusu)
    yatak_sertlik = db.Column(db.String(100))  # Uyumlu yatak sertliği (sertlik sorusu)
    uyku_pozisyonu = db.Column(db.String(350))
    bmi = db.Column(db.String(50))
    dogal_malzeme = db.Column(db.String(350))
    uyku_düzeni = db.Column(db.String(350))
    agri_bolge = db.Column(db.String(350))
    yas = db.Column(db.String(50))
    tempo = db.Column(db.String(350))
    yastik_yukseklik = db.Column(db.String(350))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in Yastik.__table__.columns}

class Settings(db.Model):
    """Uygulama ayarları - Admin panelden düzenlenebilir"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)  # Ayar anahtarı (örn: AD_ENABLED)
    value = db.Column(db.Text, nullable=False)  # Ayar değeri
    description = db.Column(db.String(500))  # Açıklama
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(TURKEY_TZ), onupdate=lambda: datetime.now(TURKEY_TZ))
    updated_by = db.Column(db.String(100))  # Kim güncelledi

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }

class KullaniciLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100))
    soyad = db.Column(db.String(100))
    email = db.Column(db.String(100))
    ip_adresi = db.Column(db.String(50))
    yas = db.Column(db.String(10))
    boy = db.Column(db.String(10))
    kilo = db.Column(db.String(10))
    vki = db.Column(db.String(10))
    cevaplar = db.Column(db.Text)  # Tüm cevaplar JSON olarak
    tarih = db.Column(db.DateTime, default=lambda: datetime.now(TURKEY_TZ))
    incelendi_mi = db.Column(db.Boolean, default=False)
    incelenen_urunler = db.Column(db.Text, nullable=True)
    onerilen_yastiklar = db.Column(db.Text, nullable=True)  # Önerilen yastıklar JSON olarak
    analiz_sonucu_alindi_mi = db.Column(db.Boolean, default=False)  # Analiz sonucu popup ile alındı mı

# --- Sabit Veriler ---
SORU_AGIRLIKLARI = {
    'sertlik': 1, 'bmi': 2, 'yas': 2, 'uyku_pozisyonu': 4, 'ideal_sertlik': 5, 'yastik_yukseklik': 3, 'dogal_malzeme': 6, 'tempo': 7, 'agri_bolge': 8, 'uyku_düzeni': 9,
}

# --- Yardımcı Fonksiyonlar ---

def get_setting(key, default=None):
    """
    Veritabanından ayar değerini getir, yoksa default değeri veya .env'den oku
    """
    try:
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            return setting.value
    except:
        pass
    # Veritabanında yoksa .env'den oku
    return os.getenv(key, default)

def get_ad_settings():
    """Active Directory ayarlarını getir (veritabanı > .env)"""
    return {
        'enabled': get_setting('AD_ENABLED', 'False').lower() == 'true',
        'server': get_setting('AD_SERVER', ''),
        'port': int(get_setting('AD_PORT', '389')),
        'use_ssl': get_setting('AD_USE_SSL', 'False').lower() == 'true',
        'use_tls': get_setting('AD_USE_TLS', 'False').lower() == 'true',
        'domain': get_setting('AD_DOMAIN', ''),
        'base_dn': get_setting('AD_BASE_DN', ''),
        'authorized_group': get_setting('AD_AUTHORIZED_GROUP', '')
    }

def normalize_turkish(text):
    """Türkçe karakterleri normalize eder"""
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def calculate_pillow_recommendations(responses):
    """Yastık önerilerini hesaplar - tekrar kullanılabilir fonksiyon"""
    yastiklar = Yastik.query.all()
    if not yastiklar:
        return []
    
    # BASİT ALGORİTMA - Her yastık için puan hesapla
    yastik_puanlari = []
    
    for yastik in yastiklar:
        toplam_puan = 0
        # Her soru için puan hesapla
        for soru_key, agirlik in SORU_AGIRLIKLARI.items():
            # Bu sorular aşağıda özel mantıkla işleniyor
            if soru_key in ('ideal_sertlik', 'sertlik', 'yastik_yukseklik', 'bmi'):
                continue

            # Kullanıcı cevabını al
            kullanici_cevap = None
            if soru_key == 'yas':
                yas_gercek = responses.get('bmi_age', {}).get('yas_gercek')
                if yas_gercek is not None:
                    yas_int = int(yas_gercek)
                    if yas_int <= 7:
                        kullanici_cevap = "0-7"
                    else:
                        kullanici_cevap = "7+"
                else:
                    kullanici_cevap = None
            else:
                kullanici_cevap = responses.get(soru_key)
            
            if not kullanici_cevap:
                continue
            
            # Yastık özelliğini al
            yastik_ozellik = getattr(yastik, soru_key, None)
            if not yastik_ozellik:
                continue
            
            # Eşleşme kontrolü
            if isinstance(kullanici_cevap, list):
                # Çoklu seçim için
                for cevap in kullanici_cevap:
                    if str(cevap).lower() in str(yastik_ozellik).lower():
                        toplam_puan += agirlik
                        break
            else:
                # Tek seçim için
                kullanici_cevap_str = str(kullanici_cevap).lower().strip()
                yastik_ozellik_str = str(yastik_ozellik).lower().strip()
                
                kullanici_cevap_normalized = normalize_turkish(kullanici_cevap_str)
                yastik_ozellik_normalized = normalize_turkish(yastik_ozellik_str)
                
                if kullanici_cevap_normalized in yastik_ozellik_normalized:
                    toplam_puan += agirlik
        
        # BMI için özel kontrol
        bmi_cevap = responses.get('bmi')
        if bmi_cevap and yastik.bmi:
            bmi_cevap_str = str(bmi_cevap).lower().strip()
            bmi_yastik_str = str(yastik.bmi).lower().strip()
            
            bmi_cevap_normalized = normalize_turkish(bmi_cevap_str)
            bmi_yastik_normalized = normalize_turkish(bmi_yastik_str)
            
            if bmi_cevap_normalized in bmi_yastik_normalized:
                toplam_puan += SORU_AGIRLIKLARI.get('bmi', 2)

        # Yastık yüksekliği için özel kontrol (orta-sert mantığına benzer kapsama)
        yukseklik_cevap = responses.get('yastik_yukseklik')
        if yukseklik_cevap and getattr(yastik, 'yastik_yukseklik', None):
            ans_str = str(yukseklik_cevap).lower().strip()
            yastik_val_str = str(getattr(yastik, 'yastik_yukseklik')).lower().strip()

            ans_norm = normalize_turkish(ans_str)
            yastik_norm = normalize_turkish(yastik_val_str)

            # varyantları birleştir ("orta yuksek", "orta – yuksek" → "orta-yuksek")
            ans_norm = ans_norm.replace('orta yuksek', 'orta-yuksek').replace('orta – yuksek', 'orta-yuksek')
            yastik_norm = yastik_norm.replace('orta yuksek', 'orta-yuksek').replace('orta – yuksek', 'orta-yuksek')

            if ans_norm in yastik_norm:
                toplam_puan += SORU_AGIRLIKLARI.get('yastik_yukseklik', 3)
            else:
                # Kapsama kuralları:
                # - "yuksek" seçilirse: yastık "yuksek" veya "orta-yuksek" ise eşleşir
                # - "orta-yuksek" seçilirse: yastık "orta-yuksek" veya "yuksek" ise eşleşir
                if ans_norm == 'yuksek' and ('yuksek' in yastik_norm or 'orta-yuksek' in yastik_norm):
                    toplam_puan += SORU_AGIRLIKLARI.get('yastik_yukseklik', 3)
                elif ans_norm == 'orta-yuksek' and ('orta-yuksek' in yastik_norm or 'yuksek' in yastik_norm):
                    toplam_puan += SORU_AGIRLIKLARI.get('yastik_yukseklik', 3)

        # İdeal yastık sertliği → yastik.sertlik
        ideal_sertlik_cevap = responses.get('ideal_sertlik')
        if ideal_sertlik_cevap and yastik.sertlik:
            ideal_sertlik_str = str(ideal_sertlik_cevap).lower().strip()
            yastik_sertlik_str = str(yastik.sertlik).lower().strip()
            
            # Kullanıcı cevabını normalize et: Türkçe karakterler, "yastik" eki, boşluk/zülfiyet
            ideal_sertlik_normalized = normalize_turkish(ideal_sertlik_str)
            # "yastik" veya "yastık" ekini kaldır
            ideal_sertlik_normalized = ideal_sertlik_normalized.replace(' yastik', '').replace(' yastık', '').strip()
            # Orta sert -> orta-sert standardize
            ideal_sertlik_normalized = ideal_sertlik_normalized.replace('orta sert', 'orta-sert').replace('orta – sert', 'orta-sert')
            yastik_sertlik_normalized = normalize_turkish(yastik_sertlik_str)
            
            # Direkt eşleşme kontrolü
            if ideal_sertlik_normalized in yastik_sertlik_normalized:
                toplam_puan += SORU_AGIRLIKLARI.get('ideal_sertlik', 5)
            else:
                # İçinde geçen kelimelere göre eşleşme
                if ideal_sertlik_normalized == 'sert' and ('sert' in yastik_sertlik_normalized or 'orta-sert' in yastik_sertlik_normalized):
                    toplam_puan += SORU_AGIRLIKLARI.get('ideal_sertlik', 5)
                elif ideal_sertlik_normalized == 'orta' and ('orta' in yastik_sertlik_normalized or 'orta-sert' in yastik_sertlik_normalized or 'yumusak-orta' in yastik_sertlik_normalized):
                    toplam_puan += SORU_AGIRLIKLARI.get('ideal_sertlik', 5)
                elif ideal_sertlik_normalized == 'yumusak' and ('yumusak' in yastik_sertlik_normalized or 'yumusak-orta' in yastik_sertlik_normalized):
                    toplam_puan += SORU_AGIRLIKLARI.get('ideal_sertlik', 5)
                elif ideal_sertlik_normalized == 'orta-sert' and ('orta-sert' in yastik_sertlik_normalized or 'sert' in yastik_sertlik_normalized or 'orta' in yastik_sertlik_normalized):
                    toplam_puan += SORU_AGIRLIKLARI.get('ideal_sertlik', 5)

        # Yatak sertliği → yastik.yatak_sertlik
        yatak_sertlik_cevap = responses.get('sertlik')
        yatak_sertlik_ozellik = getattr(yastik, 'yatak_sertlik', None)
        if yatak_sertlik_cevap and yatak_sertlik_ozellik:
            cevap_norm = normalize_turkish(str(yatak_sertlik_cevap).lower().strip())
            cevap_norm = cevap_norm.replace(' yatak', '').strip()
            cevap_norm = cevap_norm.replace('orta sert', 'orta-sert').replace('orta – sert', 'orta-sert')
            ozellik_norm = normalize_turkish(str(yatak_sertlik_ozellik).lower().strip())
            ozellik_norm = ozellik_norm.replace('orta sert', 'orta-sert').replace('orta – sert', 'orta-sert')

            if cevap_norm in ozellik_norm:
                toplam_puan += SORU_AGIRLIKLARI.get('sertlik', 1)
            else:
                if cevap_norm == 'sert' and ('sert' in ozellik_norm or 'orta-sert' in ozellik_norm):
                    toplam_puan += SORU_AGIRLIKLARI.get('sertlik', 1)
                elif cevap_norm in ('orta', 'orta-sert') and ('orta' in ozellik_norm or 'orta-sert' in ozellik_norm):
                    toplam_puan += SORU_AGIRLIKLARI.get('sertlik', 1)
                elif cevap_norm == 'yumusak' and ('yumusak' in ozellik_norm or 'yumusak-orta' in ozellik_norm):
                    toplam_puan += SORU_AGIRLIKLARI.get('sertlik', 1)

        # Doğal malzeme alerjisi için özel kontrol
        dogal_malzeme_cevap = responses.get('dogal_malzeme')
        if dogal_malzeme_cevap:
            # Kullanıcı alerjisi varsa
            if 'evet' in str(dogal_malzeme_cevap).lower():
                # Yastık doğal malzemeli mi kontrol et
                yastik_dogal_malzeme = yastik.dogal_malzeme or ''
                dogal_malzemeler = ['kaz tüyü', 'yün', 'bambu', 'pamuk', 'doğal', 'organik']
                
                # Yastık doğal malzemeli ise puanı sıfırla
                for malzeme in dogal_malzemeler:
                    if malzeme.lower() in yastik_dogal_malzeme.lower():
                        toplam_puan = 0  # Alerjik kullanıcı için doğal malzemeli yastık uygun değil
                        break

        # Yastık ve puanını listeye ekle
        yastik_puanlari.append({
            'yastik': yastik.to_dict(),
            'puan': toplam_puan
        })
    
    # Yaş kontrolü - 0-7 yaş seçildiyse özel algoritma
    yas_cevap = responses.get('bmi_age', {}).get('yas_gercek')
    if yas_cevap and int(yas_cevap) < 7:
        # 0-7 yaş için özel algoritma
        bebek_yastiklar = []
        onemli_eslesenler = []
        diger_yastiklar = []
        
        for item in yastik_puanlari:
            yastik_yas = item['yastik'].get('yas', '')
            yastik_isim = item['yastik'].get('isim', '').lower()
            if yastik_yas and ('0-7' in str(yastik_yas).lower() or 'bebek' in yastik_isim):
                bebek_yastiklar.append(item)
            else:
                onemli_eslesme_var = False
                for soru_key, agirlik in SORU_AGIRLIKLARI.items():
                    if agirlik >= 5:
                        kullanici_cevap = responses.get(soru_key)
                        if kullanici_cevap:
                            yastik_ozellik = item['yastik'].get(soru_key, '')
                            if yastik_ozellik:
                                kullanici_normalized = normalize_turkish(str(kullanici_cevap).lower().strip())
                                yastik_normalized = normalize_turkish(str(yastik_ozellik).lower().strip())
                                if kullanici_normalized in yastik_normalized:
                                    onemli_eslesme_var = True
                                    break
                if onemli_eslesme_var:
                    onemli_eslesenler.append(item)
                else:
                    diger_yastiklar.append(item)
        
        bebek_yastiklar.sort(key=lambda x: x['puan'], reverse=True)
        onemli_eslesenler.sort(key=lambda x: x['puan'], reverse=True)
        diger_yastiklar.sort(key=lambda x: x['puan'], reverse=True)
        
        sonuc_listesi = []
        sonuc_listesi.extend(bebek_yastiklar[:2])
        sonuc_listesi.extend(onemli_eslesenler[:2])
        sonuc_listesi.extend(diger_yastiklar[:1])
        yastik_puanlari = sonuc_listesi[:5]
        
        # Debug için puanları yazdır
        print("=== 0-7 YAŞ ALGORİTMASI (2 bebek + 2 önemli + 1 diğer) ===")
        for i, item in enumerate(yastik_puanlari):
            print(f"{i+1}. {item['yastik']['isim']} - Puan: {item['puan']}")
    else:
        # 7+ yaş için: bebek yastıkları hariç, normal puan sıralaması
        yastiklar_yas_bebek_haric = []
        for item in yastik_puanlari:
            yastik_yas = item['yastik'].get('yas', '')
            yastik_isim = item['yastik'].get('isim', '').lower()
            if not (yastik_yas and ('0-7' in str(yastik_yas).lower() or 'bebek' in yastik_isim)):
                yastiklar_yas_bebek_haric.append(item)
        yastiklar_yas_bebek_haric.sort(key=lambda x: x['puan'], reverse=True)
        yastik_puanlari = yastiklar_yas_bebek_haric
    
    # İlk 5 yastığı döndür
    return [item['yastik'] for item in yastik_puanlari[:5]]

QUESTIONS = [
    {
        'id': 'bmi_age',
        'question': 'Yaşınızı, boyunuzu ve kilonuzu belirtiniz.',
        'type': 'bmi_age',
        'info': 'Yaş, boy ve kilo gibi fiziksel bilgiler; ideal yastık yüksekliği ve destek düzeyini belirlememize yardımcı olur. Bu bilgiler yalnızca daha doğru bir öneri sunmak amacıyla kullanılacaktır.',
        'order': 1
    },
    {'id': 'uyku_pozisyonu', 'question': 'Sizin için en rahat uyku pozisyonunu seçer misiniz?', 'type': 'checkbox', 'options': ['Sırt üstü uyku pozisyonu', 'Yüz üstü uyku pozisyonu', 'Yan uyku pozisyonu', 'Hareketli Uyku Pozisyonu'], 'info': 'Uyku pozisyonu, boyun ve omurga sağlığınızı doğrudan etkiler. Doğru yastık, uyku tarzınıza uyum sağlamalıdır.', 'order': 2},
    {'id': 'ideal_sertlik', 'question': 'Sizin için ideal yastık sertliği nedir?', 'type': 'radio', 'options': ['Yumuşak Yastık', 'Orta-Sert Yastık', 'Sert Yastık'], 'info': 'Yastık sertliği, baş ve boynunuza ne kadar destek verdiğini belirler. Yumuşak yastıklar daha çok batarken, sert yastıklar daha sıkı bir yapı sunar. Konforunuz için size en uygun olanı seçin.', 'order': 3},
    {'id': 'yastik_yukseklik', 'question': 'Sizin için ideal yastık yüksekliği hangisi?', 'type': 'radio', 'options': ['Alçak', 'Orta-Yüksek', 'Yüksek'], 'info': 'Yastığınızın yüksekliği, omurganızın doğru hizalanmasını sağlar.Çok alçak ya da çok yüksek yastıklar, boyun ve sırt ağrılarına yol açabilir','order': 4},
    {'id': 'uyku_düzeni', 'question': 'Uyku düzeniniz genellikle nasıldır?', 'type': 'radio', 'options': ['Uykum terleme nedeniyle bölünüyor.', 'Hiçbir problem yaşamıyorum, sabahları dinlenmiş uyanıyorum.','Nefes almakta zorlanıyorum, zaman zaman horlama problemi yaşıyorum','Reflü nedeniyle geceleri sık sık uyanıyorum.'], 'info': 'Terleme sorunu için özel yastıklar mevcuttur.', 'order': 5},
    {'id': 'tempo', 'question': 'Günlük yaşam temponuzu nasıl tanımlarsınız?', 'type': 'radio', 'options': ['Oldukça sakin bir tempom var.','Genelde orta tempoda, dengeli bir günüm oluyor.', 'Yoğun tempolu bir gün geçiriyorum.'], 'info': 'Yoğun tempolu yaşamda vücut daha fazla destek ve dinlenmeye ihtiyaç duyar. Doğru yastık, günün yorgunluğunu hafifletir.', 'order': 6},
    {'id': 'agri_bolge', 'question': 'Sabahları belirli bir bölgede ağrı hissediyor musunuz?', 'type': 'checkbox', 'options': ['Hiçbir ağrı hissetmiyorum', 'Sadece Bel Ağrısı', 'Sadece Omuz Ağrısı', 'Sadece Boyun Ağrısı', 'Hepsi'], 'info': 'Boyun, omuz veya bel ağrısı; yanlış yastık seçiminden kaynaklanıyor olabilir. Vücudunuzu dinleyin, ihtiyacınıza uygun yastığı seçin.', 'order': 7},
    {'id': 'dogal_malzeme', 'question': 'Doğal malzemelere (kaz tüyü,yün,bambu,pamuk gibi) karşı alerjiniz veya hassasiyetiniz var mı ?', 'type': 'radio', 'options': ['Hayır,yok', 'Evet,bu tür doğal malzemelere karşı alerjim,hassasiyetim var'], 'info': 'Bazı kişiler doğal dolgu malzemelerine (kaz tüyü,yün,bambu,pamuk gibi) karşı alerjik reaksiyon veya hassasiyet gösterebilir.Bu kişiler için,elyaf dolgulu veya visco sünger dolgulu ürünlerin kullanımı daha sağlıklı ve konforlu bir tercih olabilir', 'order': 8},
    {'id': 'sertlik', 'question': 'Son Olarak Size Daha İyi Sonuç Verebilmemiz İçin Yatak Sertlik Derecenizi Belirtir misiniz?', 'type': 'radio', 'options': ['Yumuşak Yatak', 'Orta-Sert Yatak', 'Sert Yatak'], 'info': 'Yatak sertliği, yastığın yüksekliği ve dolgunluğu ile uyumlu olmalı. Uyumlu ikili, daha sağlıklı bir uyku sağlar.', 'order': 9}
]

# --- API Endpoint'leri ---
@app.route('/')
def home():
    return jsonify({
        'message': 'Pillow Selection Robot API',
        'version': '1.0',
        'endpoints': [
            '/api/questions',
            '/api/yastiklar', 
            '/api/recommend',
            '/api/kvkk_metin',
            '/api/kvkk_onay_ekle',
            '/api/health'
        ]
    })

@app.route('/api/health')
def health_check():
    """Sistem sağlık kontrolü endpoint'i"""
    try:
        # Database bağlantısını test et
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        
        # Redis artık kullanılmıyor - in-memory storage kullanılıyor
        environment = os.getenv('FLASK_ENV', 'development')
        redis_status = 'not_used'
        
        return jsonify({
            'status': 'healthy',
            'database': 'healthy',
            'redis': redis_status,
            'environment': environment,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/questions')
def get_questions():
    try:
        sorted_questions = sorted(QUESTIONS, key=lambda x: x['order'])
        return jsonify(questions=sorted_questions)
    except Exception as e:
        print(f"Soru getirme hatası: {e}")
        return jsonify(error="Sorular yüklenirken bir hata oluştu."), 500

@app.route('/api/yastiklar')
def get_yastiklar():
    try:
        yastiklar = Yastik.query.all()
        return jsonify(yastiklar=[y.to_dict() for y in yastiklar])
    except Exception as e:
        print(f"Yastık getirme hatası: {e}")
        return jsonify(error="Yastıklar yüklenirken bir hata oluştu."), 500



@app.route('/api/recommend', methods=['POST'])
@limiter.limit("10 per minute")  # Her IP için dakikada 10 istek
def recommend():
    try:
        data = request.get_json()
        if not data or 'responses' not in data or not isinstance(data['responses'], dict):
            return jsonify({'error': 'Eksik veya hatalı veri: responses alanı zorunlu ve dict olmalı!'}), 400
        responses = data['responses']
        user_info = data.get('user', {})

        yas = responses.get('bmi_age', {}).get('yas_gercek')
        boy = responses.get('bmi_age', {}).get('boy')
        kilo = responses.get('bmi_age', {}).get('kilo')
        vki = responses.get('bmi_age', {}).get('vki')
        ad = user_info.get('ad')
        soyad = user_info.get('soyad')
        ip_adresi = request.remote_addr if not (ad and soyad) else None

        if not responses:
            return jsonify(error="Cevaplar alınamadı."), 400

        # Yeni fonksiyonu kullanarak önerileri hesapla
        recommendations = calculate_pillow_recommendations(responses)
        
        if not recommendations:
            return jsonify(error="Veritabanında yastık bulunamadı."), 500
        
        # Önerilen yastıklar henüz kaydedilmeyecek - sadece mail girilince kaydedilecek
        
        log = KullaniciLog(
            ad=ad,
            soyad=soyad,
            ip_adresi=ip_adresi,
            yas=str(yas),
            boy=str(boy),
            kilo=str(kilo),
            vki=str(vki),
            cevaplar=json.dumps(responses, ensure_ascii=False)
            # onerilen_yastiklar başta NULL olacak
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(recommendations=recommendations, log_id=log.id)

    except Exception as e:
        print(f"Öneri sırasında hata: {e}")
        traceback.print_exc()
        return jsonify(error="Sunucu hatası."), 500

@app.route('/api/kvkk_onay_ekle', methods=['POST'])
@limiter.limit("20 per minute")  # Her IP için dakikada 20 istek
def kvkk_onay_ekle():
    try:
        data = request.get_json()
        if not data or not data.get('log_id') or not data.get('kvkk_metin_id'):
            return jsonify({'error': 'Eksik parametre: log_id ve kvkk_metin_id zorunlu!'}), 400
        log_id = data['log_id']
        kvkk_metin_id = data['kvkk_metin_id']
        ip_adresi = data.get('ip_adresi', request.remote_addr)
        onay_durumu = data.get('onay_durumu', 'kabul')
        onay_yontemi = data.get('onay_yontemi', 'popup')
        onay_tarihi = datetime.now(TURKEY_TZ)
        onay = KvkkOnay(
            log_id=log_id,
            kvkk_metin_id=kvkk_metin_id,
            ip_adresi=ip_adresi,
            onay_tarihi=onay_tarihi,
            onay_durumu=onay_durumu,
            onay_yontemi=onay_yontemi,
        )
        db.session.add(onay)
        db.session.commit()
        return jsonify({'success': True, 'onay_id': onay.id})
    except Exception as e:
        print(f"KVKK onay ekleme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/kvkk_aktif_pdf')
def kvkk_aktif_pdf():
    try:
        # Aktif KVKK metnini bul
        aktif_kvkk = KvkkMetin.query.filter_by(aktif=True).first()
        
        if not aktif_kvkk:
            return jsonify({'error': 'Aktif KVKK metni bulunamadı'}), 404
        
        # PDF dosya yolunu oluştur
        pdf_path = os.path.join('public', aktif_kvkk.dosya_adi)
        
        # Dosyanın var olup olmadığını kontrol et
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF dosyası bulunamadı'}), 404
        
        # Dosya URL'ini oluştur
        pdf_url = f"/public/{aktif_kvkk.dosya_adi}"
        
        return jsonify({
            'id': aktif_kvkk.id,
            'dosya_adi': aktif_kvkk.dosya_adi,
            'versiyon': aktif_kvkk.versiyon,
            'hash': aktif_kvkk.hash,
            'url': pdf_url,
            'aktif': aktif_kvkk.aktif
        })
        
    except Exception as e:
        print(f"KVKK PDF getirme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/log_urun_inceleme', methods=['POST'])
def log_urun_inceleme():
    try:
        data = request.get_json()
        log_id = data.get('log_id')
        urun_ismi = data.get('urun_ismi')
        if not log_id or not urun_ismi:
            return jsonify({'error': 'log_id ve urun_ismi zorunlu!'}), 400
        log = db.session.get(KullaniciLog, log_id)
        if not log:
            return jsonify({'error': 'Log bulunamadı!'}), 404
        log.incelendi_mi = True
        if log.incelenen_urunler:
            urunler = log.incelenen_urunler.split(',')
            if urun_ismi not in urunler:
                urunler.append(urun_ismi)
            log.incelenen_urunler = ','.join(urunler)
        else:
            log.incelenen_urunler = urun_ismi
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Ürün inceleme logu ekleme hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası'}), 500

@app.route('/api/kvkk_metin', methods=['GET'])
def get_kvkk_metin():
    kvkk = KvkkMetin.query.filter_by(aktif=True).first()
    if not kvkk:
        return jsonify({'error': 'KVKK metni bulunamadı'}), 404
    return jsonify({
        'id': kvkk.id,
        'versiyon': kvkk.versiyon,
        'icerik': kvkk.icerik
    })

@app.route('/api/save-mail', methods=['POST'])
def save_mail():
    try:
        # sessiz
        data = request.get_json(silent=True) or {}
        email = sanitize_email(data.get('email') or '')
        log_id = data.get('logId')
        analiz_alindi_mi = data.get('analizAlindiMi', False)
        from_address = data.get('from_address')
        bcc_emails = data.get('bcc_emails')

        # sessiz

        if not log_id:
            # sessiz
            return jsonify({'error': 'logId zorunlu!'}), 400

        log = db.session.get(KullaniciLog, log_id)
        if not log:
            # sessiz
            return jsonify({'error': 'Log bulunamadı!'}), 404
    except Exception as e:
        print(f"Mail kaydetme isteği işlenirken hata: {e}")
        return jsonify({'error': f'İstek işlenirken hata: {str(e)}'}), 500

    # Email varsa kaydet (mail gönderilsin ya da gönderilmesin)
    if email:
        # 1. Format doğrulama
        if not EMAIL_REGEX.match(email):
            return jsonify({'error': 'Geçersiz e-posta formatı.', 'field': 'email'}), 400
        
        # 2. Domain doğrulama (gerçek domain mi?)
        is_valid_domain, domain_error = validate_email_domain(email)
        if not is_valid_domain:
            return jsonify({
                'error': 'Geçersiz e-posta adresi. Lütfen gerçek bir e-posta adresi girin.',
                'reason': domain_error,
                'field': 'email'
            }), 400
        
        # Mail bilgisini log kaydına ekle
        log.email = email
        
        # Kullanıcı cevaplarını al
        responses = json.loads(log.cevaplar) if log.cevaplar else {}
        
        # Önerilen yastıkları kaydet
        # 1. Frontend'den direkt JSON string olarak geldi mi?
        incoming_pillows_json = data.get('onerilen_yastiklar')
        if incoming_pillows_json and not log.onerilen_yastiklar:
            # Frontend'den JSON string olarak gelmiş, direkt kaydet
            log.onerilen_yastiklar = incoming_pillows_json
        
        # 2. Yoksa frontend'den öneri listesi geldiyse onu kullan
        incoming_recs = data.get('recommendations')
        recommendations = None
        if isinstance(incoming_recs, list) and len(incoming_recs) > 0:
            recommendations = incoming_recs
        else:
            recommendations = calculate_pillow_recommendations(responses)
        
        # 3. Recommendations varsa ve henüz kaydedilmemişse kaydet
        if recommendations and not log.onerilen_yastiklar:
            onerilen_isimler = [y.get('isim', '') for y in recommendations if y.get('isim')]
            log.onerilen_yastiklar = json.dumps(onerilen_isimler, ensure_ascii=False)
        
        logo_bytes = get_mail_logo_bytes()
        logo_cid = 'mastermatch_logo' if logo_bytes else None
        complete_mail_content = build_recommendation_mail_html(recommendations or [], logo_cid=logo_cid)
        mail_attachments = []
        try:
            iade_pdf_bytes = build_iade_proseduru_pdf_bytes()
            mail_attachments.append((
                'Doqu_Home_Kosulsuz_Iade_Proseduru.pdf',
                iade_pdf_bytes,
                'application/pdf'
            ))
        except Exception as pdf_err:
            print(f"İade prosedürü PDF oluşturulamadı, txt gönderiliyor: {pdf_err}")
            mail_attachments.append((
                'Doqu_Home_Kosulsuz_Iade_Proseduru.txt',
                IADE_PROSEDURU_METNI.encode('utf-8'),
                'text/plain'
            ))

        try:
            oneri_pdf_bytes = build_recommendation_pdf_bytes(recommendations or [])
            mail_attachments.append((
                'Master_Match_Yastik_Oneri_Sonucu.pdf',
                oneri_pdf_bytes,
                'application/pdf'
            ))
        except Exception as oneri_pdf_err:
            print(f"Öneri PDF oluşturulamadı: {oneri_pdf_err}")

        inline_images = []
        if logo_bytes and logo_cid:
            inline_images.append((logo_cid, 'welcomelogo.png', logo_bytes, 'image/png'))

        mail_sent, mail_error = send_analysis_email(
            email,
            complete_mail_content,
            from_address,
            bcc_emails,
            attachments=mail_attachments,
            inline_images=inline_images
        )

        if not mail_sent:
            # Mail gönderilemedi ama email bilgisini kaydet
            log.analiz_sonucu_alindi_mi = analiz_alindi_mi
            db.session.commit()
            return jsonify({'error': 'Mail gönderilemedi!', 'reason': mail_error or 'Bilinmeyen hata'}), 500
    
    # Başarılı durum: analiz sonucu ve email kaydedildi
    log.analiz_sonucu_alindi_mi = analiz_alindi_mi
    db.session.commit()
    
    return jsonify({'success': True})

# ===== ADMIN PANEL ENDPOINTS =====

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin girişi - AD veya basit credentials ile doğrula"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Kullanıcı adı ve şifre gerekli'}), 400
        
        # Yeni authentication sistemi kullan
        success, message, user_info = authenticate_user(username, password)
        
        if success:
            return jsonify({
                'success': True, 
                'message': message,
                'user_info': {
                    'username': user_info.get('username', username),
                    'full_name': user_info.get('full_name', ''),
                    'email': user_info.get('email', ''),
                    'auth_method': 'AD' if AD_ENABLED else 'Local'
                }
            })
        else:
            return jsonify({'success': False, 'error': message}), 401
            
    except Exception as e:
        print(f"Admin login hatası: {e}")
        return jsonify({'success': False, 'error': 'Giriş işlemi başarısız'}), 500

@app.route('/api/admin/logs', methods=['GET'])
@admin_required
def admin_get_logs():
    """Admin paneli için log kayıtlarını getir"""
    try:
        # Query parametreleri
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        
        # Base query
        query = KullaniciLog.query
        
        # Arama filtresi
        if search:
            query = query.filter(
                db.or_(
                    KullaniciLog.email.ilike(f'%{search}%'),
                    KullaniciLog.cevaplar.ilike(f'%{search}%'),
                    KullaniciLog.onerilen_yastiklar.ilike(f'%{search}%')
                )
            )
        
        # Tarih filtresi 
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                from_date = datetime.combine(from_date.date(), datetime.min.time())
                # Türkiye timezone'u ekle
                from_date = from_date.replace(tzinfo=TURKEY_TZ)
                query = query.filter(KullaniciLog.tarih >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                to_date = datetime.combine(to_date.date(), datetime.max.time())
                # Türkiye timezone'u ekle
                to_date = to_date.replace(tzinfo=TURKEY_TZ)
                query = query.filter(KullaniciLog.tarih <= to_date)
            except ValueError:
                pass
        
        # Sıralama (en yeni önce)
        query = query.order_by(KullaniciLog.tarih.desc())
        
        # Sayfalama
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Logları formatla
        logs = []
        for log in pagination.items:
            # Cevapları parse et
            try:
                cevaplar_json = json.loads(log.cevaplar) if log.cevaplar else {}
            except:
                cevaplar_json = {}
            
            # Önerilen yastıkları parse et
            try:
                onerilen_yastiklar = json.loads(log.onerilen_yastiklar) if log.onerilen_yastiklar else []
            except:
                onerilen_yastiklar = []
            
            # Tarihi Türkiye saatinde formatla
            tarih_str = None
            if log.tarih:
                # Eğer tarih timezone bilgisi içermiyorsa, Türkiye timezone'u ekle
                if log.tarih.tzinfo is None:
                    tarih_with_tz = log.tarih.replace(tzinfo=TURKEY_TZ)
                else:
                    tarih_with_tz = log.tarih
                tarih_str = tarih_with_tz.isoformat()
            
            logs.append({
                'id': log.id,
                'ad': log.ad,
                'soyad': log.soyad,
                'email': log.email,
                'tarih': tarih_str,
                'cevaplar': cevaplar_json,
                'onerilen_yastiklar': onerilen_yastiklar,
                'incelenen_urunler': log.incelenen_urunler,
                'incelendi_mi': log.incelendi_mi,
                'analiz_alindi_mi': log.analiz_sonucu_alindi_mi,
                'ip_adresi': log.ip_adresi
            })
        
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        print(f"Admin logs hatası: {e}")
        return jsonify({'success': False, 'error': 'Loglar getirilemedi'}), 500

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_get_stats():
    """Admin paneli için istatistikler"""
    try:
        # Toplam log sayısı
        total_logs = KullaniciLog.query.count()
        
        # Email veren kullanıcı sayısı
        email_logs = KullaniciLog.query.filter(KullaniciLog.email.isnot(None)).count()
        
        # Bugünkü loglar - basit yaklaşım
        today_logs = 0
        week_logs = 0
        domain_stats = []
        
        try:
            # Bugünkü loglar - Türkiye saati ile
            today = datetime.now(TURKEY_TZ).date()
            today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=TURKEY_TZ)
            today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=TURKEY_TZ)
            today_logs = KullaniciLog.query.filter(
                KullaniciLog.tarih >= today_start,
                KullaniciLog.tarih <= today_end
            ).count()
            
            # Bu haftaki loglar - Türkiye saati ile
            week_ago = datetime.now(TURKEY_TZ).date() - timedelta(days=7)
            week_start = datetime.combine(week_ago, datetime.min.time()).replace(tzinfo=TURKEY_TZ)
            week_logs = KullaniciLog.query.filter(
                KullaniciLog.tarih >= week_start
            ).count()
            
            # Email domainleri
            all_email_logs = KullaniciLog.query.filter(KullaniciLog.email.isnot(None)).all()
            domain_count = {}
            
            for log in all_email_logs:
                if log.email and '@' in log.email:
                    domain = log.email.split('@')[1]
                    domain_count[domain] = domain_count.get(domain, 0) + 1
            
            # En çok kullanılan 10 domain
            domain_stats = sorted(domain_count.items(), key=lambda x: x[1], reverse=True)[:10]
            domain_stats = [domain[0] for domain in domain_stats]
            
        except Exception as date_error:
            print(f"Tarih/domain hesaplama hatası: {date_error}")
            # Hata durumunda sıfır değerler kullan
        
        return jsonify({
            'success': True,
            'stats': {
                'total_logs': total_logs,
                'email_logs': email_logs,
                'today_logs': today_logs,
                'week_logs': week_logs,
                'email_domains': domain_stats
            }
        })
        
    except Exception as e:
        print(f"Admin stats hatası: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'İstatistikler getirilemedi: {str(e)}'}), 500

@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def admin_get_settings():
    """Admin paneli için ayarları getir"""
    try:
        # Tüm ayarları getir
        settings = Settings.query.all()
        settings_dict = {s.key: s.to_dict() for s in settings}
        
        # Eğer veritabanında yoksa .env'den default değerleri döndür
        default_settings = {
            'AD_ENABLED': {'key': 'AD_ENABLED', 'value': get_setting('AD_ENABLED', 'False'), 'description': 'Active Directory kullan'},
            'AD_SERVER': {'key': 'AD_SERVER', 'value': get_setting('AD_SERVER', ''), 'description': 'AD sunucu adresi'},
            'AD_PORT': {'key': 'AD_PORT', 'value': get_setting('AD_PORT', '389'), 'description': 'AD sunucu portu'},
            'AD_DOMAIN': {'key': 'AD_DOMAIN', 'value': get_setting('AD_DOMAIN', ''), 'description': 'AD domain'},
            'AD_BASE_DN': {'key': 'AD_BASE_DN', 'value': get_setting('AD_BASE_DN', ''), 'description': 'AD Base DN'},
            'AD_USE_SSL': {'key': 'AD_USE_SSL', 'value': get_setting('AD_USE_SSL', 'False'), 'description': 'SSL kullan'},
            'AD_USE_TLS': {'key': 'AD_USE_TLS', 'value': get_setting('AD_USE_TLS', 'False'), 'description': 'TLS kullan'},
            'AD_AUTHORIZED_GROUP': {'key': 'AD_AUTHORIZED_GROUP', 'value': get_setting('AD_AUTHORIZED_GROUP', ''), 'description': 'Yetkili grup'},
        }
        
        # Merge: veritabanındakiler öncelikli
        for key, value in default_settings.items():
            if key not in settings_dict:
                settings_dict[key] = value
        
        return jsonify({'success': True, 'settings': settings_dict})
        
    except Exception as e:
        print(f"Admin settings getirme hatası: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Ayarlar getirilemedi'}), 500

@app.route('/api/admin/settings', methods=['POST'])
@admin_required
def admin_update_settings():
    """Admin paneli için ayarları güncelle"""
    try:
        data = request.get_json()
        settings_to_update = data.get('settings', {})
        
        # Authorization header'dan kullanıcı adını al
        auth_header = request.headers.get('Authorization', '')
        username = 'admin'
        try:
            import base64
            decoded = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
            username = decoded.split(':')[0]
        except:
            pass
        
        updated = []
        for key, value in settings_to_update.items():
            # Veritabanında varsa güncelle, yoksa oluştur
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
                setting.updated_by = username
                setting.updated_at = datetime.now(TURKEY_TZ)
            else:
                setting = Settings(
                    key=key,
                    value=str(value),
                    updated_by=username
                )
                db.session.add(setting)
            updated.append(key)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(updated)} ayar güncellendi',
            'updated': updated
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Admin settings güncelleme hatası: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Ayarlar güncellenemedi'}), 500

@app.route('/api/admin/logs/export-excel', methods=['GET'])
@admin_required
def admin_export_logs_excel():
    """Admin paneli için log kayıtlarını Excel olarak indir"""
    try:
        # Query parametrelerini al
        search = request.args.get('search', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()

        # Base query
        query = KullaniciLog.query

        # Arama filtresi
        if search:
            query = query.filter(
                db.or_(
                    KullaniciLog.email.ilike(f'%{search}%'),
                    KullaniciLog.cevaplar.ilike(f'%{search}%'),
                    KullaniciLog.onerilen_yastiklar.ilike(f'%{search}%')
                )
            )

        # Tarih filtresi
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                from_date = datetime.combine(from_date.date(), datetime.min.time())
                from_date = from_date.replace(tzinfo=TURKEY_TZ)
                query = query.filter(KullaniciLog.tarih >= from_date)
            except ValueError:
                pass
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                to_date = datetime.combine(to_date.date(), datetime.max.time())
                to_date = to_date.replace(tzinfo=TURKEY_TZ)
                query = query.filter(KullaniciLog.tarih <= to_date)
            except ValueError:
                pass

        logs = query.order_by(KullaniciLog.tarih.desc()).all()
        data = []
        for log in logs:
            try:
                cevaplar_json = json.loads(log.cevaplar) if log.cevaplar else {}
            except:
                cevaplar_json = {}
            try:
                onerilen_yastiklar = json.loads(log.onerilen_yastiklar) if log.onerilen_yastiklar else []
            except:
                onerilen_yastiklar = []
            data.append({
                'ID': log.id,
                'Ad': log.ad,
                'Soyad': log.soyad,
                'E-posta': log.email,
                'Tarih': log.tarih.isoformat() if log.tarih else '',
                'IP Adresi': log.ip_adresi,
                'Yaş': log.yas,
                'Boy': log.boy,
                'Kilo': log.kilo,
                'VKI': log.vki,
                'Cevaplar': json.dumps(cevaplar_json, ensure_ascii=False),
                'Önerilen Yastıklar': json.dumps(onerilen_yastiklar, ensure_ascii=False),
                'İncelenen Ürünler': log.incelenen_urunler,
                'İncelendi mi': log.incelendi_mi,
                'Analiz Sonucu Alındı mı': log.analiz_sonucu_alindi_mi
            })
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Logs')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"kullanici_loglari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
    except Exception as e:
        print(f"Excel export hatası: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Excel dosyası oluşturulamadı'}), 500

def ensure_yatak_sertlik_column():
    """Mevcut veritabanına yatak_sertlik kolonunu ekler (yoksa)."""
    try:
        dialect = db.engine.dialect.name
        with db.engine.connect() as conn:
            if dialect == 'sqlite':
                rows = conn.execute(db.text("PRAGMA table_info(yastik)")).fetchall()
                cols = {row[1] for row in rows}
                if 'yatak_sertlik' not in cols:
                    conn.execute(db.text("ALTER TABLE yastik ADD COLUMN yatak_sertlik VARCHAR(100)"))
                    conn.commit()
                    print("✓ yastik.yatak_sertlik kolonu eklendi (sqlite)")
            else:
                # MSSQL / diğerleri
                result = conn.execute(db.text("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'yastik' AND COLUMN_NAME = 'yatak_sertlik'
                """)).scalar()
                if not result:
                    conn.execute(db.text("ALTER TABLE yastik ADD yatak_sertlik NVARCHAR(100) NULL"))
                    conn.commit()
                    print("✓ yastik.yatak_sertlik kolonu eklendi")
    except Exception as e:
        print(f"yatak_sertlik kolon kontrolü: {e}")


# Uygulamayı çalıştırmak için
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_yatak_sertlik_column()
    environment = os.getenv('FLASK_ENV', 'development')
    if environment != 'production':
        print("🚀 Backend geliştirme modunda başlatılıyor... http://localhost:5001")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("Production ortamı: Lütfen bir WSGI sunucusu ile başlatın (örn. waitress, IIS, vs.)") 