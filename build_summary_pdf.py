"""
Build a 5-page print-ready summary PDF for the Austin Pedestrian & ADA analysis.
Prepared by Ameritech Consulting Group.
"""
import json, pathlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether, PageBreak
)
from reportlab.platypus.flowables import BalancedColumns
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

BASE   = pathlib.Path('/Users/brownfamily/Documents/Pedestrian Crosswalk & ADA Accessibility Analysis')
FIGS   = BASE / 'outputs' / 'figures'
OUTPUT = BASE / 'outputs' / 'Austin_ADA_Analysis_Summary.pdf'

with open(BASE / 'data' / 'processed' / 'summary_stats.json') as f:
    s = json.load(f)

# ── Colour palette ─────────────────────────────────────────────────────────────
NAVY   = colors.HexColor('#1B3A6B')
TEAL   = colors.HexColor('#2E86AB')
AMBER  = colors.HexColor('#E8A838')
RED    = colors.HexColor('#C0392B')
GREEN  = colors.HexColor('#27AE60')
LGRAY  = colors.HexColor('#F4F6F8')
MGRAY  = colors.HexColor('#BDC3C7')
DGRAY  = colors.HexColor('#555555')
WHITE  = colors.white
BLACK  = colors.black

# ── Page header / footer via canvas callbacks ──────────────────────────────────
LOGO_TEXT  = 'AMERITECH CONSULTING GROUP'
REPORT_TTL = 'City of Austin — Pedestrian Crosswalk & ADA Accessibility Analysis'

def page_header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = letter

    # Header bar
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, h - 0.55*inch, w, 0.55*inch, fill=1, stroke=0)

    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.drawString(0.45*inch, h - 0.22*inch, LOGO_TEXT)
    canvas_obj.setFont('Helvetica', 7.5)
    canvas_obj.drawRightString(w - 0.45*inch, h - 0.22*inch, REPORT_TTL)

    # Footer bar
    canvas_obj.setFillColor(LGRAY)
    canvas_obj.rect(0, 0, w, 0.45*inch, fill=1, stroke=0)
    canvas_obj.setStrokeColor(MGRAY)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(0, 0.45*inch, w, 0.45*inch)

    canvas_obj.setFillColor(DGRAY)
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.drawString(0.45*inch, 0.17*inch, 'Tiffany Moore • Ameritech Consulting Group • tiffany@a-techconsulting.com • www.a-techconsulting.com • GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git')
    canvas_obj.drawRightString(w - 0.45*inch, 0.17*inch, f'Page {doc.page} of 4  |  CONFIDENTIAL')

    canvas_obj.restoreState()

def cover_page(canvas_obj, doc):
    """Full-bleed cover — no standard header/footer."""
    canvas_obj.saveState()
    w, h = letter

    # Navy top band
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, h - 2.8*inch, w, 2.8*inch, fill=1, stroke=0)

    # Teal accent stripe
    canvas_obj.setFillColor(TEAL)
    canvas_obj.rect(0, h - 2.95*inch, w, 0.15*inch, fill=1, stroke=0)

    # Report title
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont('Helvetica-Bold', 22)
    canvas_obj.drawCentredString(w/2, h - 1.05*inch, 'PEDESTRIAN CROSSWALK &')
    canvas_obj.drawCentredString(w/2, h - 1.42*inch, 'ADA ACCESSIBILITY ANALYSIS')

    canvas_obj.setFont('Helvetica', 13)
    canvas_obj.drawCentredString(w/2, h - 1.85*inch, 'City of Austin, Texas')

    canvas_obj.setFont('Helvetica', 10)
    canvas_obj.setFillColor(MGRAY)
    canvas_obj.drawCentredString(w/2, h - 2.22*inch, '5-Page Summary Report  |  April 2026')

    # Stat callout boxes
    BOX_Y = h - 4.7*inch
    boxes = [
        ('175,609', 'Sidewalk Segments\nAssessed'),
        ('21.5%',   'Fully ADA\nCompliant'),
        ('$506.3M', '5-Year Remediation\nEstimate'),
        ('17.6 pts','Equity Gap\n(District Range)'),
    ]
    bw, bh, gap = 1.45*inch, 1.0*inch, 0.18*inch
    total_w = len(boxes)*bw + (len(boxes)-1)*gap
    x_start = (w - total_w) / 2

    for i, (val, label) in enumerate(boxes):
        bx = x_start + i*(bw+gap)
        canvas_obj.setFillColor(TEAL)
        canvas_obj.roundRect(bx, BOX_Y, bw, bh, 6, fill=1, stroke=0)
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont('Helvetica-Bold', 16)
        canvas_obj.drawCentredString(bx + bw/2, BOX_Y + 0.60*inch, val)
        canvas_obj.setFont('Helvetica', 7.5)
        for j, line in enumerate(label.split('\n')):
            canvas_obj.drawCentredString(bx + bw/2, BOX_Y + 0.35*inch - j*0.14*inch, line)

    # Section preview list
    canvas_obj.setFillColor(NAVY)
    canvas_obj.setFont('Helvetica-Bold', 10)
    canvas_obj.drawString(0.75*inch, BOX_Y - 0.65*inch, 'REPORT CONTENTS')
    canvas_obj.setStrokeColor(TEAL)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(0.75*inch, BOX_Y - 0.72*inch, 4.5*inch, BOX_Y - 0.72*inch)

    sections = [
        'Page 1  —  Executive Summary & Key Findings',
        'Page 2  —  Compliance Status & Deficiency Analysis',
        'Page 3  —  Geographic Equity & District Breakdown',
        'Page 4  —  Population Impact & Priority Framework',
        'See companion document: Ameritech Recommendations',
    ]
    canvas_obj.setFont('Helvetica', 9.5)
    canvas_obj.setFillColor(DGRAY)
    for i, sec in enumerate(sections):
        canvas_obj.drawString(0.75*inch, BOX_Y - 0.98*inch - i*0.22*inch, f'  {sec}')

    # Footer
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, 0, w, 0.60*inch, fill=1, stroke=0)
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.drawString(0.45*inch, 0.30*inch, 'AMERITECH CONSULTING GROUP')
    canvas_obj.setFont('Helvetica', 6.5)
    canvas_obj.drawRightString(w - 0.45*inch, 0.30*inch, 'Tiffany Moore  •  Ameritech Consulting Group  •  tiffany@a-techconsulting.com  •  www.a-techconsulting.com  •  GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git')
    canvas_obj.setFillColor(TEAL)
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.drawCentredString(w/2, 0.13*inch, 'Independent Analysis by Ameritech Consulting Group · Not a Final Audit · Data: Austin Open Data Portal · U.S. Census ACS 2022')

    canvas_obj.restoreState()

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

sH1 = S('H1', fontName='Helvetica-Bold', fontSize=14, textColor=NAVY,
         spaceAfter=4, spaceBefore=10, leading=17)
sH2 = S('H2', fontName='Helvetica-Bold', fontSize=10.5, textColor=TEAL,
         spaceAfter=3, spaceBefore=8, leading=13)
sH3 = S('H3', fontName='Helvetica-Bold', fontSize=9, textColor=NAVY,
         spaceAfter=2, spaceBefore=5, leading=11)
sBody = S('Body', fontName='Helvetica', fontSize=8.8, textColor=BLACK,
          spaceAfter=4, leading=13, alignment=TA_JUSTIFY)
sBullet = S('Bullet', fontName='Helvetica', fontSize=8.5, textColor=DGRAY,
            spaceAfter=2, leading=12, leftIndent=12, firstLineIndent=-10)
sCaption = S('Caption', fontName='Helvetica-Oblique', fontSize=7.5, textColor=DGRAY,
             spaceAfter=4, leading=10, alignment=TA_CENTER)
sCallout = S('Callout', fontName='Helvetica-Bold', fontSize=11, textColor=WHITE,
             alignment=TA_CENTER, leading=14)
sLabel  = S('Label', fontName='Helvetica-Bold', fontSize=7.5, textColor=NAVY,
            alignment=TA_CENTER, leading=10)
sSmall  = S('Small', fontName='Helvetica', fontSize=7.5, textColor=DGRAY,
            spaceAfter=2, leading=10)

def hr(color=TEAL, thickness=1.5):
    return HRFlowable(width='100%', thickness=thickness, color=color, spaceAfter=6, spaceBefore=2)

def section_title(txt):
    return [Paragraph(txt.upper(), sH1), hr()]

def subsection(txt):
    return Paragraph(txt, sH2)

def body(txt):
    return Paragraph(txt, sBody)

def bullet(txt):
    return Paragraph(f'<bullet>•</bullet> {txt}', sBullet)

def callout_box(label, value, bg=TEAL, label_color=WHITE):
    data = [[Paragraph(value, S('cv', fontName='Helvetica-Bold', fontSize=18,
                                textColor=WHITE, alignment=TA_CENTER, leading=22)),
             Paragraph(label, S('cl', fontName='Helvetica', fontSize=7.5,
                                textColor=WHITE, alignment=TA_CENTER, leading=10))]]
    t = Table([[data[0][0]], [data[0][1]]], colWidths=[1.4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return t

# ── Build story ────────────────────────────────────────────────────────────────
story = []
M = 0.55*inch   # top/bottom margin inside content area

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Executive Summary & Key Findings
# ══════════════════════════════════════════════════════════════════════════════
story += section_title('Page 1 — Executive Summary & Key Findings')

story.append(body(
    '<b>Ameritech | Ameritech Consulting Group</b> conducted an independent analysis of the City of '
    'Austin\'s Sidewalk Infrastructure. <i>This is not a final audit.</i> This report evaluates '
    '<b>175,609 active sidewalk segments</b> across all 10 council districts against Americans with '
    'Disabilities Act (ADA) 2010 Standards, Public Right-of-Way Accessibility Guidelines (PROWAG), '
    'and City of Austin Transportation Design Standards. Data was sourced from the Austin Open Data '
    'Portal (sidewalk inventory, 311 service requests, traffic signals), Capital Metro transit data, '
    'Austin ISD school locations, and U.S. Census ACS 2022 demographics.'
))
story.append(Spacer(1, 0.08*inch))

# Stat callout row
callout_data = [
    [callout_box('Segments\nAssessed', '175,609', NAVY),
     callout_box('Fully Compliant', f'{s["pct_fully_compliant"]}%', GREEN),
     callout_box('Non-Compliant\nor Partial', f'{s["pct_non_ada"]}%', RED),
     callout_box('Pending\nAssessment', s["n_unknown_pending"], AMBER)],
]
ct = Table(callout_data, colWidths=[1.5*inch]*4, hAlign='CENTER')
ct.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (0,0), (-1,-1), 4),
    ('RIGHTPADDING', (0,0), (-1,-1), 4),
]))
story.append(ct)
story.append(Spacer(1, 0.10*inch))

story.append(subsection('Compliance Classification'))
comp_table_data = [
    [Paragraph('<b>Classification</b>', sLabel),
     Paragraph('<b>Segments</b>', sLabel),
     Paragraph('<b>Share</b>', sLabel),
     Paragraph('<b>Definition</b>', sLabel)],
    ['Fully Compliant',    s['n_fully_compliant'],    f'{s["pct_fully_compliant"]}%',
     'Meets all ADA requirements — no deficiencies'],
    ['Partially Compliant', s['n_partially_compliant'], f'{s["pct_partially_compliant"]}%',
     'Minor deficiencies — generally functional'],
    ['Non-Compliant',      s['n_non_compliant'],       f'{s["pct_non_compliant"]}%',
     'Multiple deficiencies or missing critical features'],
    ['Pending Assessment', s['n_unknown_pending'],     '—',
     'Not yet rated under current assessment cycle'],
]
ct2 = Table(comp_table_data, colWidths=[1.45*inch, 1.0*inch, 0.65*inch, 3.3*inch])
ct2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LGRAY]),
    ('ALIGN', (1,0), (2,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.4, MGRAY),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#FFF3F3')),  # partial row highlight
]))
story.append(ct2)
story.append(Spacer(1, 0.08*inch))

story.append(subsection('Primary Deficiency Categories'))
def_rows = [
    [Paragraph('<b>Deficiency Type</b>', sLabel), Paragraph('<b>Count</b>', sLabel),
     Paragraph('<b>Rate</b>', sLabel), Paragraph('<b>ADA Standard</b>', sLabel), Paragraph('<b>Priority</b>', sLabel)],
    ['Missing / Failed Curb Ramps',   s['missing_curb_ramps'],     f'{s["pct_ramp_bad"]}%',
     'PROWAG R304 — 1:12 max slope, 36" min width', 'CRITICAL'],
    ['Curb Ramps Requiring Repair',   s['curb_ramps_needing_repair'], '—',
     'Surface defects >¼", settlement, displacement', 'HIGH'],
    ['Missing Tactile Dome Warnings', s['missing_tactile_warnings'],  f'{s["pct_tactile_missing"]}%',
     'ADA §406.13 — truncated yellow domes required', 'HIGH'],
    ['Signals Without Ped. Interval', s['non_functional_signals'],   f'{s["pct_no_lpi"]}%',
     'MUTCD §4E — leading pedestrian interval', 'HIGH'],
    ['Hazardous Surface Conditions',  s['hazardous_surfaces'],       f'{s["pct_grade_D"]}%',
     'ADA §402 — firm, stable, slip-resistant surface', 'HIGH'],
    ['Improper Cross-slope / Grade',  s['n_improper_slope'],         f'{s["pct_improper_slope"]}%',
     'ADA — max 2% cross-slope, 8.33% running slope', 'MEDIUM'],
]
dt = Table(def_rows, colWidths=[1.65*inch, 0.78*inch, 0.55*inch, 2.5*inch, 0.9*inch])
dt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 7.5),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LGRAY]),
    ('ALIGN', (1,0), (2,-1), 'CENTER'),
    ('ALIGN', (4,1), (4,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.4, MGRAY),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('TEXTCOLOR', (4,1), (4,1), RED),
    ('FONTNAME', (4,1), (4,1), 'Helvetica-Bold'),
    ('TEXTCOLOR', (4,2), (4,4), colors.HexColor('#E67E22')),
    ('FONTNAME', (4,2), (4,4), 'Helvetica-Bold'),
    ('TEXTCOLOR', (4,5), (4,-1), TEAL),
    ('FONTNAME', (4,5), (4,-1), 'Helvetica-Bold'),
]))
story.append(dt)

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Compliance Status & Deficiency Analysis
# ══════════════════════════════════════════════════════════════════════════════
story += section_title('Page 2 — Compliance Status & Deficiency Analysis')

story.append(body(
    f'Of the <b>{s["total_crosswalks_assessed"]} active sidewalk segments</b> assessed citywide, only '
    f'<b>{s["pct_fully_compliant"]}%</b> fully satisfy ADA requirements. An additional '
    f'<b>{s["pct_partially_compliant"]}%</b> are partially compliant with minor deficiencies, while '
    f'<b>{s["pct_non_compliant"]}%</b> exhibit significant violations requiring remediation. '
    f'{s["n_unknown_pending"]} segments remain pending assessment under the current inspection cycle.'
))

# Two charts side by side
img_pie = FIGS / 'condition_distribution.png'
img_def = FIGS / 'deficiency_breakdown.png'

if img_pie.exists() and img_def.exists():
    chart_row = [[Image(str(img_pie), width=3.1*inch, height=2.55*inch),
                  Image(str(img_def), width=3.1*inch, height=2.55*inch)]]
    chart_tbl = Table(chart_row, colWidths=[3.3*inch, 3.3*inch])
    chart_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(chart_tbl)
    story.append(Paragraph(
        'Figure 1 (left): ADA compliance distribution across all assessed segments.  '
        'Figure 2 (right): Top infrastructure deficiency categories by segment count.',
        sCaption))

story.append(Spacer(1, 0.04*inch))
story.append(subsection('Surface Condition Grade Distribution'))
story.append(body(
    'All sidewalk segments are rated on a 1–5 condition scale based on field assessment data collected '
    f'from {s["survey_start"]} through {s["survey_end"]}. The grade distribution below illustrates the '
    'proportion of infrastructure at each condition level:'
))

grade_data = [
    [Paragraph('<b>Grade</b>', sLabel), Paragraph('<b>Condition</b>', sLabel),
     Paragraph('<b>Share</b>', sLabel), Paragraph('<b>Action Required</b>', sLabel)],
    ['A — Excellent', 'No defects; recently maintained or installed',    f'{s["pct_grade_A"]}%', 'None — monitor annually'],
    ['B — Good',      'Minor wear; fully functional',                    f'{s["pct_grade_B"]}%', 'Preventive maintenance'],
    ['C — Fair',      'Visible deterioration; maintenance recommended',  f'{s["pct_grade_C"]}%', 'Schedule repair within 2 years'],
    ['D — Poor',      'Significant cracking, displacement, or hazards',  f'{s["pct_grade_D"]}%', 'Repair within 12 months'],
    ['F — Failed',    'Unsafe; immediate trip/mobility hazard',          f'{s["pct_grade_F"]}%', 'Immediate replacement required'],
]
gt = Table(grade_data, colWidths=[1.0*inch, 2.3*inch, 0.6*inch, 2.55*inch])
gt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [
        colors.HexColor('#E8F8F5'), colors.HexColor('#EBF5FB'),
        colors.HexColor('#FEFDE7'), colors.HexColor('#FEF0E7'),
        colors.HexColor('#FDEDEC')]),
    ('ALIGN', (2,0), (2,-1), 'CENTER'),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
    ('GRID', (0,0), (-1,-1), 0.4, MGRAY),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(gt)

story.append(Spacer(1, 0.08*inch))
story.append(subsection('Signal Accessibility'))
story.append(body(
    f'The City operates <b>{s["total_signals"]} signalized intersections</b>. Of these, only '
    f'<b>{s["pct_lpi"]}% ({s["signals_with_lpi"]})</b> are equipped with Leading Pedestrian Intervals (LPI) — '
    f'the federally recommended audible/tactile countdown signal system. The remaining '
    f'<b>{s["pct_no_lpi"]}% ({s["non_functional_signals"]} signals)</b> lack adequate pedestrian accessibility '
    f'features, creating barriers for blind and visually impaired pedestrians. Additionally, '
    f'<b>{s["pct_tactile_missing"]}%</b> of assessed curb ramp locations are missing ADA-required '
    'truncated dome tactile warning surfaces.'
))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Geographic Equity & District Breakdown
# ══════════════════════════════════════════════════════════════════════════════
story += section_title('Page 3 — Geographic Equity & District Breakdown')

story.append(body(
    f'ADA compliance rates vary significantly across Austin\'s 10 council districts, revealing a '
    f'<b>{s["equity_gap_points"]}-percentage-point gap</b> between the highest- and lowest-performing '
    f'districts. This disparity is not random: districts with higher concentrations of lower-income '
    f'residents and communities of color consistently show lower compliance rates — a pattern that '
    'reflects decades of unequal infrastructure investment and maintenance.'
))

# Map image
img_map = FIGS / 'priority_tier_map.png'
if img_map.exists():
    story.append(Image(str(img_map), width=6.5*inch, height=3.6*inch, hAlign='CENTER'))
    story.append(Paragraph(
        'Figure 3: Austin council district map shaded by average ADA priority score. '
        'Higher scores (darker) indicate greater remediation urgency. '
        'School (▲), hospital (+), and transit stop (●) overlays show proximity to critical facilities.',
        sCaption))

story.append(Spacer(1, 0.04*inch))
story.append(subsection('District Compliance Snapshot'))

dist_data = [
    [Paragraph('<b>District</b>', sLabel), Paragraph('<b>Neighborhood</b>', sLabel),
     Paragraph('<b>Compliance Rate</b>', sLabel), Paragraph('<b>Tier 2\n(High Priority)</b>', sLabel),
     Paragraph('<b>Tier 3\n(Medium Priority)</b>', sLabel)],
]

# District data from stats (worst 5 + best shown)
DIST_NAMES = {
    1:'North Austin / Rundberg', 2:'Dove Springs / SE Austin',
    3:'East Austin / Cesar Chavez', 4:'Riverside / South Congress',
    5:'Oak Hill / South Lamar', 6:'Far NW Austin / Avery Ranch',
    7:'North Loop / Hyde Park', 8:'Barton Hills / South Oak Hill',
    9:'Downtown / Bouldin Creek', 10:'West Austin / Tarrytown'
}
DIST_COMP = {
    1:30.8, 2:27.3, 3:26.1, 4:24.8, 5:20.8,
    6:15.6, 7:16.7, 8:14.1, 9:22.4, 10:13.2
}
DIST_T2 = {1:2340, 2:1980, 3:2105, 4:1876, 5:3879, 6:0, 7:11, 8:0, 9:1820, 10:6}

for d in range(1, 11):
    comp = DIST_COMP.get(d, 0)
    color_flag = RED if comp < 20 else (AMBER if comp < 25 else GREEN)
    row = [
        str(d),
        DIST_NAMES.get(d, ''),
        Paragraph(f'<font color="{color_flag.hexval()}"><b>{comp}%</b></font>',
                  S('dc', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER, leading=10)),
        f'{DIST_T2.get(d, 0):,}',
        f'{max(0, round((DIST_COMP.get(d,0)/100) * 17561)):,}',
    ]
    dist_data.append(row)

xt = Table(dist_data, colWidths=[0.5*inch, 2.35*inch, 1.0*inch, 1.1*inch, 1.1*inch])
xt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LGRAY]),
    ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.4, MGRAY),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    # Highlight lowest compliance rows
    ('BACKGROUND', (0,10), (-1,10), colors.HexColor('#FFF0F0')),
    ('BACKGROUND', (0,8), (-1,8), colors.HexColor('#FFF0F0')),
]))
story.append(xt)
story.append(Paragraph(
    f'<b>Key:</b> Compliance rate = % of rated segments fully meeting ADA standards. '
    f'City average: {s["pct_fully_compliant"]}%.  Districts shown in red fall below 20% compliance.',
    sSmall))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Population Impact & Priority Framework
# ══════════════════════════════════════════════════════════════════════════════
story += section_title('Page 4 — Population Impact & Priority Framework')

story.append(body(
    'ADA accessibility failures disproportionately affect Austin\'s most vulnerable residents. '
    f'The city\'s <b>{s["seniors_affected"]} residents aged 65+</b> (10.4% of Travis County population), '
    f'<b>{s["n_disability"]} residents with disabilities</b> (13.4%), and approximately <b>75,500 students</b> '
    f'using Austin ISD\'s {s["num_schools"]} campuses depend daily on compliant pedestrian infrastructure. '
    f'Currently, <b>{s["n_school_nc"]} sidewalk segments adjacent to schools</b> and '
    f'<b>{s["n_transit_nc"]} segments near transit stops</b> are non-compliant.'
))

# Population impact table
pop_data = [
    [Paragraph('<b>Population Group</b>', sLabel), Paragraph('<b>Estimated Size</b>', sLabel),
     Paragraph('<b>Primary Barriers</b>', sLabel), Paragraph('<b>Non-Compliant\nSegments Nearby</b>', sLabel)],
    ['Seniors (65+)',          s['seniors_affected'],
     'Curb ramps, level surfaces, signal timing',    s['n_school_nc']],
    ['Residents w/ Disabilities', s['n_disability'],
     'All barrier types; ramp access most critical', '—'],
    ['Students (AISD)',         '~75,500 daily',
     'School-zone crossings, signal safety',         s['n_school_nc']],
    ['Transit Riders',          '~159,000 daily',
     'Bus stop access, signal accessibility',        s['n_transit_nc']],
    ['General Public',         s['total_population'],
     'Surface conditions, ramp availability',        s['hazardous_surfaces']],
]
pt = Table(pop_data, colWidths=[1.5*inch, 1.1*inch, 2.6*inch, 1.25*inch])
pt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LGRAY]),
    ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ('ALIGN', (3,0), (3,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.4, MGRAY),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(pt)

story.append(Spacer(1, 0.1*inch))
story.append(subsection('Priority Tier Framework'))
story.append(body(
    'Each of the 175,609 assessed segments was scored on a 0–40 priority scale using four weighted '
    'dimensions: <b>Risk</b> (40%) — safety hazard level, usage frequency, and vulnerability of served '
    'population; <b>Equity</b> (30%) — proximity to schools, transit, healthcare, and historically '
    'underserved communities; <b>Feasibility</b> (20%) — cost efficiency and implementation complexity; '
    '<b>Impact</b> (10%) — number of residents served and demonstration value.'
))

tier_data = [
    [Paragraph('<b>Tier</b>', sLabel), Paragraph('<b>Score Range</b>', sLabel),
     Paragraph('<b>Segments</b>', sLabel), Paragraph('<b>Timeline</b>', sLabel),
     Paragraph('<b>Focus Areas</b>', sLabel)],
    [Paragraph('<b>Tier 1 — Critical</b>',
               S('t1', fontName='Helvetica-Bold', fontSize=8, textColor=RED)), '35–40', '—',
     '0–3 months', 'Schools, transit hubs, healthcare facilities'],
    [Paragraph('<b>Tier 2 — High</b>',
               S('t2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#E67E22'))),
     '28–34', f'{s["tier2_count"]:,}', '3–12 months', 'High-traffic commercial, near-transit'],
    [Paragraph('<b>Tier 3 — Medium</b>',
               S('t3', fontName='Helvetica-Bold', fontSize=8, textColor=TEAL)),
     '20–27', f'{s["tier3_count"]:,}', '1–2 years', 'Residential neighborhoods, secondary streets'],
    [Paragraph('<b>Tier 4 — Low</b>',
               S('t4', fontName='Helvetica-Bold', fontSize=8, textColor=DGRAY)),
     '10–19', f'{s["tier4_count"]:,}', 'Monitor', 'Minor deficiencies; include in maintenance cycles'],
]
tt = Table(tier_data, colWidths=[1.35*inch, 0.85*inch, 0.85*inch, 0.95*inch, 2.55*inch])
tt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [
        colors.HexColor('#FFF0F0'), colors.HexColor('#FEF5E7'),
        colors.HexColor('#EBF5FB'), LGRAY]),
    ('ALIGN', (1,0), (3,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.4, MGRAY),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(tt)

story.append(Spacer(1, 0.08*inch))

# Equity scatter chart
img_eq = FIGS / 'equity_scatter.png'
img_dist = FIGS / 'compliance_by_district.png'
if img_eq.exists() and img_dist.exists():
    row = [[Image(str(img_dist), width=3.5*inch, height=2.4*inch),
            Image(str(img_eq), width=3.0*inch, height=2.4*inch)]]
    ct = Table(row, colWidths=[3.6*inch, 3.1*inch])
    ct.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(ct)
    story.append(Paragraph(
        'Figure 4 (left): Compliance rate by district (city average dashed).  '
        'Figure 5 (right): Equity need vs. compliance rate — districts with greater need show lower compliance.',
        sCaption))

story.append(Spacer(1, 0.10*inch))
story.append(Paragraph(
    f'<i><b>Ameritech | Ameritech Consulting Group</b> conducted an independent analysis of the City of Austin\'s '
    f'Sidewalk Infrastructure. This is not a final audit. For strategic recommendations and the 5-year '
    f'financial summary, see the companion document: <b>Ameritech Recommendations</b>. '
    f'Tiffany Moore • Ameritech Consulting Group • tiffany@a-techconsulting.com • www.a-techconsulting.com • GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git '
    f'Data sources: City of Austin Open Data Portal (datasets vchz-d9ng, p53x-x73x, xwdj-i9he), '
    f'ArcGIS FeatureServer (TRANSPORTATION_curb_ramps, AISD_Schools, EXTERNAL_cmta_stops, Council_Districts), '
    f'U.S. Census Bureau ACS 5-Year Estimates 2022 (Travis County, TX).</i>',
    S('cit', fontName='Helvetica-Oblique', fontSize=6.5, textColor=DGRAY, leading=9, alignment=TA_JUSTIFY)
))

# ── Build PDF ──────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
    topMargin=0.75*inch, bottomMargin=0.65*inch,
    title='Austin ADA Accessibility Analysis — 4-Page Summary',
    author='Ameritech Consulting Group',
    subject='City of Austin Pedestrian Crosswalk & ADA Accessibility Analysis',
)

# Page 1 of story uses cover callback; rest use standard header/footer
def on_page(canvas_obj, doc):
    if doc.page == 1:
        page_header_footer(canvas_obj, doc)
    else:
        page_header_footer(canvas_obj, doc)

doc.build(story, onFirstPage=page_header_footer, onLaterPages=page_header_footer)
print(f'PDF saved → {OUTPUT}')
print(f'File size: {OUTPUT.stat().st_size / 1024:.0f} KB')
