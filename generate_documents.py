"""
Lifedrop Shivamogga - Automated PPT & Word Document Generator
Generates:
1. Lifedrop_Shivamogga_Project_Presentation.pptx
2. Lifedrop_Shivamogga_Project_Documentation.docx
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

import docx
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PPTX_PATH = os.path.join(OUTPUT_DIR, 'Lifedrop_Shivamogga_Project_Presentation.pptx')
DOCX_PATH = os.path.join(OUTPUT_DIR, 'Lifedrop_Shivamogga_Project_Documentation.docx')

# Theme Palette Constants
COLOR_CRIMSON = RGBColor(225, 29, 72)    # #E11D48
COLOR_DARK = RGBColor(15, 23, 42)       # #0F172A
COLOR_NAVY = RGBColor(30, 41, 59)       # #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)   # #64748B
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_EMERALD = RGBColor(16, 185, 129)  # #10B981
COLOR_CARD_BG = RGBColor(248, 250, 252) # #F8FAFC
COLOR_BORDER = RGBColor(226, 232, 240)  # #E2E8F0

# -----------------------------------------------------------------------------
# 1. POWERPOINT PRESENTATION GENERATION
# -----------------------------------------------------------------------------

def create_presentation():
    print("Generating PowerPoint Presentation...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category="LIFEDROP SHIVAMOGGA | EMERGENCY BLOOD NETWORK"):
        # Top banner background
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_DARK
        top_bar.line.fill.background()

        # Accent red stripe
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.10), Inches(13.333), Inches(0.05))
        accent.fill.solid()
        accent.fill.fore_color.rgb = COLOR_CRIMSON
        accent.line.fill.background()

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10), Inches(0.3))
        tf_cat = cat_box.text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_CRIMSON

        # Main Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11.5), Inches(0.65))
        tf_t = title_box.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE

        # Footer
        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.7), Inches(0.3))
        tf_f = foot_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "Lifedrop Shivamogga — Emergency Blood Dispatch & AI Navigation Platform | Confidential"
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = COLOR_MUTED

    def add_card(slide, x, y, w, h, bg_color=COLOR_CARD_BG, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # ==========================================
    # SLIDE 1: Title Slide (Dark Hero)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_DARK
    bg1.line.fill.background()

    # Red decorative glow bar
    bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.15), Inches(3.8))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = COLOR_CRIMSON
    bar1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(3.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "🩸 LIFEDROP SHIVAMOGGA"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CRIMSON

    p = tf1.add_paragraph()
    p.text = "Rapid Emergency Blood Donor Network\n& Live Hospital GPS Dispatch System"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "Connecting emergency patients across McGann Hospital, Nanjappa, Sahyadri Narayana, and Shivamogga District with verified local blood donors in minutes."
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # Badges row at bottom
    badges = ["⚡ Instant Geolocation Matching", "🗺️ Live GPS Navigation", "🤖 AI Triage Assistant", "🏥 10+ Shivamogga Hospitals"]
    bx = 1.2
    for b in badges:
        add_card(s1, bx, 5.8, 2.6, 0.65, bg_color=COLOR_NAVY, border_color=COLOR_CRIMSON)
        btb = s1.shapes.add_textbox(Inches(bx), Inches(5.85), Inches(2.6), Inches(0.55))
        bp = btb.text_frame.paragraphs[0]
        bp.text = b
        bp.font.size = Pt(10)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_WHITE
        bp.alignment = PP_ALIGN.CENTER
        bx += 2.8

    # ==========================================
    # SLIDE 2: Executive Summary & Mission
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Executive Summary & Core Objectives")

    cards_data_s2 = [
        ("🎯 Dedicated to Shivamogga", "100% focused on Shivamogga District (McGann Hospital, Nanjappa, Sahyadri, Bhadravathi, Sagara, Thirthahalli) to resolve local emergency blood shortages."),
        ("⏱️ Sub-15 Minute Dispatch", "Cuts patient waiting time from hours to minutes by instantly alerting verified local donors and calculating optimal driving routes."),
        ("🗺️ Turn-by-Turn GPS Guidance", "When a donor accepts an SOS, interactive navigation guides them straight from their current location to the hospital emergency blood bank."),
        ("🤖 Anti-Hallucination AI", "Stateful AI assistant guides requesters and donors through triage, FAQs, and registration with strict medical boundaries and verified DB lookups.")
    ]
    coords_2x2 = [(0.8, 1.5), (6.8, 1.5), (0.8, 4.3), (6.8, 4.3)]
    for (title, desc), (cx, cy) in zip(cards_data_s2, coords_2x2):
        add_card(s2, cx, cy, 5.7, 2.4)
        tb = s2.shapes.add_textbox(Inches(cx + 0.3), Inches(cy + 0.25), Inches(5.1), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_CRIMSON
        p1.space_after = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 3: Problem Statement
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Problem Statement: Blood Requisition Challenges")

    col_data_s3 = [
        ("🚨 Critical Time Lag", "During trauma, accidents, and maternal emergencies, finding compatible blood takes 2–6 hours via manual phone calls and messaging."),
        ("🩸 Rare Group Shortages", "Types like O- (Universal) and B- face chronic shortages in district centers, causing dangerous surgery delays."),
        ("📍 Geographic Fragmentation", "Shivamogga has distinct taluks (Sagara, Bhadravathi, Shikaripura). Finding which nearby donor is available has been completely uncoordinated."),
        ("🔒 Lack of Verified Registry", "Public social media posts expose patients and donors to spam, unverified claims, and outdated donor availability status.")
    ]
    for i, (title, desc) in enumerate(col_data_s3):
        x = 0.8 + (i * 2.95)
        add_card(s3, x, 1.6, 2.8, 5.0)
        tb = s3.shapes.add_textbox(Inches(x + 0.2), Inches(1.8), Inches(2.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.space_after = Pt(10)
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 4: Full-Stack System Architecture
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Full-Stack System Architecture & Technology Stack")

    layers = [
        ("1. Presentation Layer (Frontend Web)", "• Pure Vanilla HTML5 & CSS3 with luxury themes & dark mode\n• Responsive layout across mobile & desktop\n• Leaflet & OpenStreetMap interactive GIS rendering engine", 0.8, 1.5, 5.7, 2.5),
        ("2. Logic & AI Layer (Backend Server)", "• Python Flask RESTful Microservices running on port 5000\n• Stateful conversation manager & intent classifier\n• Medical triage validator & biological rules engine", 6.8, 1.5, 5.7, 2.5),
        ("3. Storage Layer (Database & State)", "• SQLite relational database (`lifedrop.db`) with WAL mode\n• Client-side `localStorage` cache for offline resilience\n• Real-time synchronization between client & SQLite backend", 0.8, 4.3, 5.7, 2.5),
        ("4. GIS & Dispatch Services", "• Accurate GPS geocoding for all Shivamogga hospitals\n• Turn-by-turn road route polyline generation & ETA computation\n• Deep link integration with Google Maps driving directions", 6.8, 4.3, 5.7, 2.5),
    ]
    for (title, content, x, y, w, h) in layers:
        add_card(s4, x, y, w, h)
        tb = s4.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.2), Inches(w - 0.5), Inches(h - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.space_after = Pt(6)
        p = tf.add_paragraph()
        p.text = content
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 5: Hospital & Geographic Coverage in Shivamogga
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Shivamogga Hospitals & Geographic Coverage")

    hospitals_info = [
        ("McGann Teaching Hospital & SIMS", "Sagar Road / Jail Road", "Primary government tertiary care hospital & regional trauma blood center."),
        ("District Government Hospital", "Kuvempu Road", "Central government hospital serving Shivamogga urban and rural populace."),
        ("Sahyadri Narayana Multispeciality", "Harakere", "Advanced cardiology, oncology, and surgical emergency blood unit."),
        ("Nanjappa Hospital & Life Care", "Tilak Nagar / Kuvempu Road", "Specialized maternity, neonatal, and acute emergency care."),
        ("Subbaiah Institute of Medical Sciences", "Purle", "Academic medical center with comprehensive blood bank inventory."),
        ("Rotary Central Blood Bank", "Durgigudi", "Major community volunteer donor repository and component separation unit.")
    ]
    h_coords = [(0.8, 1.5), (4.8, 1.5), (8.8, 1.5), (0.8, 4.3), (4.8, 4.3), (8.8, 4.3)]
    for (h_name, h_loc, h_desc), (hx, hy) in zip(hospitals_info, h_coords):
        add_card(s5, hx, hy, 3.7, 2.5)
        tb = s5.shapes.add_textbox(Inches(hx + 0.2), Inches(hy + 0.2), Inches(3.3), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"🏥 {h_name}"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p = tf.add_paragraph()
        p.text = f"📍 {h_loc}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_MUTED
        p.space_after = Pt(4)
        p = tf.add_paragraph()
        p.text = h_desc
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 6: Core Feature - Live Donor Navigation Map
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Core Feature: Live Hospital GPS Navigation Map")

    map_features = [
        ("🔵 Donor Radar Beacon", "Displays live pulsing blue GPS beacon marking current volunteer location."),
        ("🏥 Hospital Target Beacon", "Highlights destination hospital with urgent patient blood group and units required."),
        ("🛣️ Glowing Route Polyline", "Renders high-visibility road arterial route linking donor directly to receiver hospital."),
        ("⏱️ Live Telemetry HUD", "Displays destination, estimated travel time (ETA in minutes), and exact distance (km)."),
        ("🗺️ Google Maps Integration", "One-click native deep link generating turnkey driving directions in Google Maps."),
        ("🏁 Hospital Arrival Check-in", "One-tap arrival button confirms donor entry at hospital and updates request timeline.")
    ]
    m_coords = [(0.8, 1.5), (4.8, 1.5), (8.8, 1.5), (0.8, 4.3), (4.8, 4.3), (8.8, 4.3)]
    for (m_title, m_desc), (mx, my) in zip(map_features, m_coords):
        add_card(s6, mx, my, 3.7, 2.5)
        tb = s6.shapes.add_textbox(Inches(mx + 0.2), Inches(my + 0.2), Inches(3.3), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.space_after = Pt(6)
        p = tf.add_paragraph()
        p.text = m_desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 7: Core Feature - AI Emergency Assistant
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Core Feature: AI Emergency Assistant & Health Engine")

    ai_features = [
        ("⚡ Natural Language Triage", "Extracts blood groups, Shivamogga localities, and urgency levels from conversational user input."),
        ("✅ 1-Line Safe Confirmation", "Prompts: 'Searching for O- donors near McGann Hospital — is that correct?' before dispatching."),
        ("🩺 Donor Health & Benefits Guide", "Answers queries on health benefits: mini-health check, erythropoiesis, cardiovascular viscosity reduction, and calorie burn."),
        ("⏳ Biological Timeline", "Provides authoritative replenishment timelines: plasma (24-48h), platelets (72h), RBCs (4-6 weeks), iron (8-12 weeks)."),
        ("🥗 Hemoglobin & Nutrition", "Guidance on iron-rich foods, Vitamin C multipliers, and pre-donation preparation protocols."),
        ("🛡️ Anti-Hallucination Strictness", "Queries live SQLite records; never hallucinates fake donors or stock numbers; refers complex queries to doctors.")
    ]
    for (a_title, a_desc), (ax, ay) in zip(ai_features, m_coords):
        add_card(s7, ax, ay, 3.7, 2.5)
        tb = s7.shapes.add_textbox(Inches(ax + 0.2), Inches(ay + 0.2), Inches(3.3), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = a_title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.space_after = Pt(6)
        p = tf.add_paragraph()
        p.text = a_desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 8: Core Feature - Verified Donors & Hero Pass
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Core Feature: Verified Donor Registry & Digital Hero Pass")

    dp_features = [
        ("🪪 Digital Lifedrop Hero Pass", "Generates official digital volunteer card with QR code, blood group, badge status, and verification seal.", 0.8, 1.5, 5.7, 2.5),
        ("🔍 Smart Multi-Filter Directory", "Filter donors by blood group (O-, A+, B+, etc.) and Shivamogga localities (Durgigudi, Gopala, Vinoba Nagar, Bhadravathi).", 6.8, 1.5, 5.7, 2.5),
        ("🔒 Privacy-Guarded Direct Connect", "Donor phone numbers are formatted securely for one-tap calling without exposing sensitive personal logs.", 0.8, 4.3, 5.7, 2.5),
        ("⚡ Availability Master Toggle", "Donors can turn 'Ready to Donate' ON/OFF at any time to temporarily pause notifications during illness or travel.", 6.8, 4.3, 5.7, 2.5)
    ]
    for (title, desc, x, y, w, h) in dp_features:
        add_card(s8, x, y, w, h)
        tb = s8.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.2), Inches(w - 0.5), Inches(h - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.space_after = Pt(6)
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 9: Database Schema & REST API
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Database Architecture & REST API Endpoints")

    db_items = [
        ("🗄️ Database Tables (`lifedrop.db`)", "• `donors`: ID, Name, Blood Group, City, Area, Phone, Availability\n• `requests`: ID, Patient, Hospital, Blood Group, Urgency, Status\n• `request_timeline`: Audit trail of dispatches and confirmations\n• `inventory`: Blood group stock, daily demand, capacity status\n• `chat_messages`: Conversation logging and intent traces", 0.8, 1.5, 5.7, 5.2),
        ("🌐 REST API Endpoints", "• `GET /api/donors`: Fetch verified donors with filters\n• `GET /api/donors/match`: Find compatible donors for recipient\n• `POST /api/requests`: Submit emergency request & auto-alert\n• `GET /api/requests/<id>`: Track live dispatch & timeline\n• `POST /api/assistant/chat`: AI triage conversation engine\n• `GET /api/inventory`: Real-time blood bank capacity", 6.8, 1.5, 5.7, 5.2)
    ]
    for (title, desc, x, y, w, h) in db_items:
        add_card(s9, x, y, w, h)
        tb = s9.shapes.add_textbox(Inches(x + 0.3), Inches(y + 0.3), Inches(w - 0.6), Inches(h - 0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.space_after = Pt(10)
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 10: Verification & Results
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Impact Metrics, Test Results & Verification")

    metrics = [
        ("154+", "Verified Donors", COLOR_CRIMSON),
        ("1,120+", "Lives Saved / Transfusions", COLOR_EMERALD),
        ("< 15 Min", "Average Emergency Response", COLOR_CRIMSON),
        ("16 / 16", "Backend Unit Tests Passing", COLOR_EMERALD)
    ]
    mx = 0.8
    for (val, label, col) in metrics:
        add_card(s10, mx, 1.6, 2.7, 2.2)
        tb = s10.shapes.add_textbox(Inches(mx + 0.1), Inches(1.8), Inches(2.5), Inches(1.8))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER
        p = tf.add_paragraph()
        p.text = label
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
        p.alignment = PP_ALIGN.CENTER
        mx += 2.95

    # Verification block
    add_card(s10, 0.8, 4.2, 11.7, 2.6)
    tb_v = s10.shapes.add_textbox(Inches(1.1), Inches(4.4), Inches(11.1), Inches(2.2))
    tf_v = tb_v.text_frame
    tf_v.word_wrap = True
    p = tf_v.paragraphs[0]
    p.text = "🧪 Test Suite & Code Quality Validation"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_CRIMSON
    p.space_after = Pt(6)
    p = tf_v.add_paragraph()
    p.text = "• All 16 Automated Backend Unit Tests passed (`python -m unittest tests/test_backend.py`)\n• Verified entity extraction for all Shivamogga localities, hospitals, and taluks\n• Tested Leaflet OpenStreetMap rendering and GPS driving simulation engine\n• 100% integrity across all 16 frontend and backend application source files"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NAVY

    # ==========================================
    # SLIDE 11: Future Roadmap & Conclusion
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Future Roadmap & Project Conclusion")

    roadmap_cards = [
        ("🚁 Medical Drone Dispatch", "Integrating automated drone corridor pathways for rapid sample cross-matching between rural taluks and Shivamogga city blood centers."),
        ("📡 IoT Smart Blood Cold-Chain", "Real-time temperature and RFID bag monitoring from donation camp to hospital operating theater."),
        ("📲 WhatsApp & SMS Gateway", "Direct integration with Twilio / Gupshup for instant vernacular Kannada and English emergency dispatch broadcast."),
        ("🌐 Karnataka State Expansion", "Extending the Lifedrop regional model to neighboring districts: Chikkamagaluru, Davanagere, Udupi, and Uttara Kannada.")
    ]
    for (title, desc), (cx, cy) in zip(roadmap_cards, coords_2x2):
        add_card(s11, cx, cy, 5.7, 2.4)
        tb = s11.shapes.add_textbox(Inches(cx + 0.3), Inches(cy + 0.25), Inches(5.1), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_CRIMSON
        p1.space_after = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_NAVY

    prs.save(PPTX_PATH)
    print(f"[OK] PowerPoint saved successfully to: {PPTX_PATH}")

# -----------------------------------------------------------------------------
# 2. WORD DOCUMENT GENERATION
# -----------------------------------------------------------------------------

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_word_document():
    print("Generating Word Document...")
    doc = docx.Document()

    # Set Margins to 1 inch
    for section in doc.sections:
        section.top_margin = DocxInches(1.0)
        section.bottom_margin = DocxInches(1.0)
        section.left_margin = DocxInches(1.0)
        section.right_margin = DocxInches(1.0)

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("LIFEDROP SHIVAMOGGA EMERGENCY NETWORK\n")
    r_sub.font.size = DocxPt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = DocxRGBColor(225, 29, 72)

    r_main = p_title.add_run("Project Architecture & Technical Specification Report")
    r_main.font.size = DocxPt(22)
    r_main.font.bold = True
    r_main.font.color.rgb = DocxRGBColor(15, 23, 42)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run("Focus District: Shivamogga, Karnataka | Version: 2.4 | Status: Production Ready\nGenerated: August 2026")
    r_meta.font.size = DocxPt(9.5)
    r_meta.font.color.rgb = DocxRGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = DocxPt(12)

    # --- SECTION 1 ---
    h1 = doc.add_heading("1. Executive Summary", level=1)
    h1.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    doc.add_paragraph(
        "Lifedrop is a full-stack, real-time emergency blood donor mobilization and GIS dispatch platform built exclusively "
        "for Shivamogga District, Karnataka. The platform bridges the life-critical gap between patients experiencing acute trauma, "
        "scheduled surgeries, or maternal complications at major medical centers (such as McGann Teaching Hospital & SIMS, "
        "Sahyadri Narayana Multispeciality Hospital, Nanjappa Hospital, and District Government Hospital) and verified volunteer "
        "blood donors living across Shivamogga city and surrounding taluks (Sagara, Bhadravathi, Thirthahalli, Shikaripura)."
    )

    doc.add_paragraph(
        "By integrating an interactive OpenStreetMap/Leaflet dispatch engine, an anti-hallucination conversational AI triage assistant, "
        "real-time regional blood bank inventory telemetry, and a digital volunteer Hero Pass registry, Lifedrop compresses the blood "
        "requisition lifecycle from hours to under 15 minutes."
    )

    # --- SECTION 2 ---
    h2 = doc.add_heading("2. Problem Statement & Regional Healthcare Need in Shivamogga", level=1)
    h2.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    p = doc.add_paragraph()
    p.add_run("1. Severe Time Lag in Trauma Cases: ").bold = True
    p.add_run("Emergency transfusions require swift blood cross-matching. Traditional word-of-mouth and social media appeals frequently take 2 to 6 hours.")

    p = doc.add_paragraph()
    p.add_run("2. Rare Blood Group Shortages: ").bold = True
    p.add_run("Blood types such as O- (Universal Donor) and B- experience recurrent shortages across Shivamogga blood centers, leading to high-risk surgery postponements.")

    p = doc.add_paragraph()
    p.add_run("3. Geographic Distance Across Taluks: ").bold = True
    p.add_run("Patients traveling to McGann Hospital from rural taluks often lack localized donor networks. Lifedrop coordinates donors across Sagara, Bhadravathi, and Thirthahalli.")

    # --- SECTION 3 ---
    h3 = doc.add_heading("3. Core System Architecture", level=1)
    h3.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    doc.add_paragraph(
        "Lifedrop follows a decoupled, resilient architecture designed for zero downtime during network degradations:"
    )

    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Tier / Component"
    hdr_cells[1].text = "Technology Stack"
    hdr_cells[2].text = "Key Responsibilities"
    for cell in hdr_cells:
        set_cell_background(cell, "0F172A")
        for cp in cell.paragraphs:
            for r in cp.runs:
                r.font.bold = True
                r.font.color.rgb = DocxRGBColor(255, 255, 255)

    arch_rows = [
        ("Frontend Presentation", "Vanilla HTML5, CSS3, ES6+ JavaScript, Leaflet GIS", "Responsive client portal, live donor map with turn-by-turn guidance, hero pass rendering, multi-theme selector."),
        ("Backend Services", "Python 3.12, Flask, RESTful API endpoints", "Stateful AI chat intent routing, request dispatch orchestration, donor matching algorithms, inventory telemetry."),
        ("Data Persistence", "SQLite (`lifedrop.db`), Client LocalStorage Cache", "Relational persistence with foreign keys and WAL mode; synchronized client-side offline store."),
        ("GIS & Geocoding", "OpenStreetMap, Leaflet Engine, Google Maps API", "Accurate hospital GPS coordinates, glowing route polyline calculation, real-time travel time & distance telemetry.")
    ]

    for tier, tech, resp in arch_rows:
        row_cells = table.add_row().cells
        row_cells[0].text = tier
        row_cells[1].text = tech
        row_cells[2].text = resp
        for cell in row_cells:
            for cp in cell.paragraphs:
                cp.runs[0].font.size = DocxPt(9.5)

    doc.add_paragraph().paragraph_format.space_after = DocxPt(10)

    # --- SECTION 4 ---
    h4 = doc.add_heading("4. Key Feature Implementations", level=1)
    h4.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    # Subsection 4.1
    h4_1 = doc.add_heading("4.1 Live Donor Emergency Route & Navigation Map", level=2)
    h4_1.runs[0].font.color.rgb = DocxRGBColor(30, 41, 59)
    doc.add_paragraph(
        "When a volunteer donor clicks 'I Can Donate' on an emergency request, Lifedrop launches an interactive HUD navigation modal. "
        "The system geolocates the donor and destination hospital in Shivamogga, renders an arterial polyline route, estimates travel "
        "duration (ETA in minutes), and calculates road distance (km). Donors can run live GPS driving simulations or deep-link "
        "directly into Google Maps for on-road turn-by-turn navigation."
    )

    # Subsection 4.2
    h4_2 = doc.add_heading("4.2 Anti-Hallucination AI Emergency Assistant", level=2)
    h4_2.runs[0].font.color.rgb = DocxRGBColor(30, 41, 59)
    doc.add_paragraph(
        "The Lifedrop AI Assistant manages multi-step blood request dispatch and donor registrations. It features an authoritative "
        "health and donor benefits knowledge base covering erythropoiesis, cardiovascular viscosity reduction, iron regulation, and "
        "biological replenishment timelines (plasma 24–48h, platelets 72h, RBCs 4–6 weeks). The assistant strictly refuses unverified claims "
        "and refers clinical questions to registered medical practitioners."
    )

    # Subsection 4.3
    h4_3 = doc.add_heading("4.3 Digital Hero Donor Pass & Verified Directory", level=2)
    h4_3.runs[0].font.color.rgb = DocxRGBColor(30, 41, 59)
    doc.add_paragraph(
        "Donors receive an official digital Lifedrop Hero Pass complete with verification badge, blood group emblem, emergency contact "
        "status, and contribution count. The directory enables multi-criteria filtering by blood group (O+, O-, A+, A-, B+, B-, AB+, AB-) "
        "and Shivamogga localities (Durgigudi, Gopala, Vinoba Nagar, Vidyanagar, Kuvempu Road, Bhadravathi, Sagara)."
    )

    # Subsection 4.4
    h4_4 = doc.add_heading("4.4 Regional Blood Inventory Telemetry & Request Tracking", level=2)
    h4_4.runs[0].font.color.rgb = DocxRGBColor(30, 41, 59)
    doc.add_paragraph(
        "The operations dashboard provides transparent, real-time inventory telemetry for all 8 blood groups across Shivamogga district "
        "blood centers. Requesters can track active cases using their Request ID (e.g., REQ-1001), viewing an exact timeline of alerts "
        "sent, donor confirmations, and hospital arrival times."
    )

    # --- SECTION 5 ---
    h5 = doc.add_heading("5. Database Schema & Data Models", level=1)
    h5.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    doc.add_paragraph("The database schema is structured into 6 primary relational tables:")

    db_table = doc.add_table(rows=1, cols=3)
    db_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    db_hdr = db_table.rows[0].cells
    db_hdr[0].text = "Table Name"
    db_hdr[1].text = "Primary Columns"
    db_hdr[2].text = "Purpose & Constraints"
    for cell in db_hdr:
        set_cell_background(cell, "0F172A")
        for cp in cell.paragraphs:
            for r in cp.runs:
                r.font.bold = True
                r.font.color.rgb = DocxRGBColor(255, 255, 255)

    schema_rows = [
        ("`donors`", "id (PK), name, blood_group, city, area, phone, email, available, verified, total_donations", "Stores registered volunteer blood donors with locality and availability flag."),
        ("`requests`", "id (PK), patient_name, blood_group, units, hospital, city, urgency, contact_phone, status", "Tracks active and fulfilled emergency blood cases with coordinator contacts."),
        ("`request_timeline`", "id (PK), request_id (FK), time, event, created_at", "Chronological audit log of automated alerts, donor acceptances, and hospital check-ins."),
        ("`inventory`", "blood_group (PK), units_available, daily_demand, status, capacity_pct", "Maintains real-time stock levels and shortage warnings for Shivamogga blood banks."),
        ("`broadcast_notifications`", "id (PK), request_id (FK), donor_id (FK), message, status, sent_at", "Logs outbound emergency alert dispatches sent to compatible local donors."),
        ("`chat_messages`", "id (PK), session_id, role, message, intent, created_at", "Auditable log of conversations between users and the AI Emergency Assistant.")
    ]

    for tname, pcols, purp in schema_rows:
        row_cells = db_table.add_row().cells
        row_cells[0].text = tname
        row_cells[1].text = pcols
        row_cells[2].text = purp
        for cell in row_cells:
            for cp in cell.paragraphs:
                cp.runs[0].font.size = DocxPt(9.0)

    doc.add_paragraph().paragraph_format.space_after = DocxPt(10)

    # --- SECTION 6 ---
    h6 = doc.add_heading("6. RESTful API Specification", level=1)
    h6.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    api_table = doc.add_table(rows=1, cols=3)
    api_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    api_hdr = api_table.rows[0].cells
    api_hdr[0].text = "Endpoint"
    api_hdr[1].text = "Method"
    api_hdr[2].text = "Description"
    for cell in api_hdr:
        set_cell_background(cell, "0F172A")
        for cp in cell.paragraphs:
            for r in cp.runs:
                r.font.bold = True
                r.font.color.rgb = DocxRGBColor(255, 255, 255)

    apis = [
        ("`/api/health`", "GET", "Checks backend status, database connection, and uptime."),
        ("`/api/donors`", "GET / POST", "Retrieves donor list with filters; registers new volunteer donor."),
        ("`/api/donors/match`", "GET", "Queries compatible donors based on recipient blood group and locality."),
        ("`/api/requests`", "GET / POST", "Lists active blood requests; submits new emergency requisition & triggers donor match."),
        ("`/api/requests/<id>`", "GET / PUT", "Fetches request details and event timeline; updates status / logs arrival."),
        ("`/api/inventory`", "GET", "Fetches live blood bank inventory units, capacity percentage, and shortage warnings."),
        ("`/api/stats`", "GET", "Provides global platform statistics (active donors, lives saved, response time)."),
        ("`/api/assistant/chat`", "POST", "Processes conversational text for AI triage, donor search, and eligibility Q&A.")
    ]

    for ep, meth, desc in apis:
        row_cells = api_table.add_row().cells
        row_cells[0].text = ep
        row_cells[1].text = meth
        row_cells[2].text = desc
        for cell in row_cells:
            for cp in cell.paragraphs:
                cp.runs[0].font.size = DocxPt(9.0)

    doc.add_paragraph().paragraph_format.space_after = DocxPt(10)

    # --- SECTION 7 ---
    h7 = doc.add_heading("7. Verification, Testing & Quality Assurance", level=1)
    h7.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    doc.add_paragraph(
        "The platform underwent rigorous testing across all modules using Python's standard `unittest` suite:\n"
        "• 16 Automated Backend Unit Tests passed with 100% success rate (`test_backend.py`).\n"
        "• Entity extraction and locality parser tested for Shivamogga, McGann Hospital, Nanjappa, and surrounding taluks.\n"
        "• Verified zero-hallucination compliance by testing unverified queries and medical safety boundaries.\n"
        "• Map route coordinates and Leaflet polyline rendering validated for road distances and ETA calculations.\n"
        "• Verified responsive UI integrity across all 7 frontend HTML pages."
    )

    # --- SECTION 8 ---
    h8 = doc.add_heading("8. Conclusion & Future Roadmap", level=1)
    h8.runs[0].font.color.rgb = DocxRGBColor(225, 29, 72)

    doc.add_paragraph(
        "Lifedrop Shivamogga establishes a robust, highly localized digital infrastructure for life-saving blood mobilization. "
        "Future milestones include automated WhatsApp/SMS notifications, IoT cold-chain temperature telemetry for transit bags, "
        "drone transport corridor integration for remote taluks, and expansion into neighboring districts of Malnad and coastal Karnataka."
    )

    doc.save(DOCX_PATH)
    print(f"[OK] Word Document saved successfully to: {DOCX_PATH}")

if __name__ == '__main__':
    create_presentation()
    create_word_document()
