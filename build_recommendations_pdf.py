"""
Standalone Ameritech Recommendations document.
Companion to the 4-page Austin ADA Analysis Summary.
"""
import json, pathlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)

BASE   = pathlib.Path('/Users/brownfamily/Documents/Pedestrian Crosswalk & ADA Accessibility Analysis')
OUTPUT = BASE / 'outputs' / 'Ameritech_Recommendations.pdf'

with open(BASE / 'data' / 'processed' / 'summary_stats.json') as f:
    s = json.load(f)

# ── Colours (matching main document) ─────────────────────────────────────────
NAVY  = colors.HexColor('#1B3A6B')
TEAL  = colors.HexColor('#2E86AB')
AMBER = colors.HexColor('#E8A838')
RED   = colors.HexColor('#C0392B')
GREEN = colors.HexColor('#27AE60')
LGRAY = colors.HexColor('#F4F6F8')
MGRAY = colors.HexColor('#BDC3C7')
DGRAY = colors.HexColor('#555555')
WHITE = colors.white

# ── Styles ────────────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

sH1    = S('H1', fontName='Helvetica-Bold', fontSize=13, textColor=NAVY, spaceAfter=4, spaceBefore=10, leading=16)
sH2    = S('H2', fontName='Helvetica-Bold', fontSize=10, textColor=TEAL, spaceAfter=3, spaceBefore=8, leading=13)
sH3    = S('H3', fontName='Helvetica-Bold', fontSize=9, textColor=NAVY, spaceAfter=2, spaceBefore=6, leading=11)
sBody  = S('Body', fontName='Helvetica', fontSize=8.8, textColor=colors.black, spaceAfter=4, leading=13, alignment=TA_JUSTIFY)
sSmall = S('Small', fontName='Helvetica', fontSize=7.5, textColor=DGRAY, spaceAfter=2, leading=10)
sLabel = S('Label', fontName='Helvetica-Bold', fontSize=7.5, textColor=NAVY, alignment=TA_CENTER, leading=10)
sCaption = S('Caption', fontName='Helvetica-Oblique', fontSize=7.5, textColor=DGRAY, spaceAfter=4, leading=10, alignment=TA_CENTER)

def hr(color=TEAL, thickness=1.5):
    return HRFlowable(width='100%', thickness=thickness, color=color, spaceAfter=6, spaceBefore=2)

def section_title(txt):
    return [Paragraph(txt.upper(), sH1), hr()]

def body(txt):
    return Paragraph(txt, sBody)

# ── Header / footer ───────────────────────────────────────────────────────────
def page_hf(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = letter

    # Header
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, h - 0.55*inch, w, 0.55*inch, fill=1, stroke=0)
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.drawString(0.45*inch, h - 0.22*inch, 'AMERITECH CONSULTING GROUP')
    canvas_obj.setFont('Helvetica', 7.5)
    canvas_obj.drawRightString(w - 0.45*inch, h - 0.22*inch,
                               'Ameritech Recommendations — Austin ADA Sidewalk Infrastructure Analysis')

    # Footer
    canvas_obj.setFillColor(LGRAY)
    canvas_obj.rect(0, 0, w, 0.45*inch, fill=1, stroke=0)
    canvas_obj.setStrokeColor(MGRAY)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(0, 0.45*inch, w, 0.45*inch)
    canvas_obj.setFillColor(DGRAY)
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.drawString(0.45*inch, 0.17*inch,
                          'Ameritech Consulting Group  |  tiffany@a-techconsulting.com  |  April 2026  |  Independent Analysis — Not a Final Audit')
    canvas_obj.drawRightString(w - 0.45*inch, 0.17*inch, f'Page {doc.page}  |  CONFIDENTIAL')
    canvas_obj.restoreState()

# ── Story ─────────────────────────────────────────────────────────────────────
story = []

# ── Cover block ───────────────────────────────────────────────────────────────
cover_data = [[
    Paragraph(
        'AMERITECH RECOMMENDATIONS',
        S('ct', fontName='Helvetica-Bold', fontSize=20, textColor=WHITE,
          alignment=TA_CENTER, leading=26)),
    Paragraph(
        'City of Austin — Sidewalk Infrastructure &amp; ADA Accessibility',
        S('cs', fontName='Helvetica', fontSize=11, textColor=MGRAY,
          alignment=TA_CENTER, leading=15)),
    Paragraph(
        '<i>Ameritech | Ameritech Consulting Group conducted an independent analysis of the '
        'City of Austin\'s Sidewalk Infrastructure. This is not a final audit.</i>',
        S('cd', fontName='Helvetica-Oblique', fontSize=8.5, textColor=colors.HexColor('#A8C8E8'),
          alignment=TA_CENTER, leading=12)),
]]
# Flatten rows for table
cover_tbl = Table(
    [[cover_data[0][0]], [cover_data[0][1]], [Spacer(1, 0.08*inch)], [cover_data[0][2]]],
    colWidths=[6.5*inch]
)
cover_tbl.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), NAVY),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('LEFTPADDING', (0,0), (-1,-1), 20),
    ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ('ROUNDEDCORNERS', [6]),
]))
story.append(cover_tbl)
story.append(Spacer(1, 0.18*inch))

# Context note
story.append(body(
    f'This document presents Ameritech Consulting Group\'s strategic recommendations and 5-year '
    f'financial framework for addressing ADA compliance deficiencies identified across '
    f'<b>{s["total_crosswalks_assessed"]} active sidewalk segments</b> in the City of Austin. '
    f'It is intended as a companion to the <i>Austin ADA Accessibility Analysis — 4-Page Summary</i>. '
    f'Findings are based on publicly available City of Austin data and independent analysis. '
    f'These recommendations do not constitute a final audit or engineering assessment.'
))
story.append(Spacer(1, 0.06*inch))

# ── Section 1: Strategic Recommendations ─────────────────────────────────────
story += section_title('Strategic Recommendations')

recs = [
    ('1.  Adopt a Phased Remediation Plan',
     f'Authorize a 5-year, ${s["total_remediation_M"]}M remediation program structured around the four '
     f'priority tiers derived from this analysis. <b>Phase 1 (Year 1, ${s["yr1_budget_M"]}M)</b> should '
     f'address the <b>{s["tier2_count"]:,} highest-priority Tier 2 segments</b> concentrated near schools, '
     'transit hubs, and healthcare facilities. Phased implementation allows compliance progress to be '
     'demonstrated to federal funders before later phases require full appropriation.'),

    ('2.  Establish a Dedicated ADA Compliance Office',
     'Create an ADA Compliance Coordinator position ($125K/year) with direct reporting to the City '
     'Manager\'s Office. Convene an interdepartmental compliance committee (Transportation, Public '
     'Works, Parks, Planning) with monthly accountability meetings. Deploy a digital asset management '
     'system ($350K one-time capital) to replace ad hoc tracking with real-time compliance dashboards '
     'accessible to department heads and City Council.'),

    ('3.  Prioritize Equity-Deficit Districts First',
     f'Districts 10, 8, 6, and 7 — with compliance rates between <b>{s["lowest_compliance_pct"]}% and '
     f'16.7%</b> against a city average of {s["pct_fully_compliant"]}% — must receive disproportionate '
     f'Phase 1 and 2 funding. The <b>{s["equity_gap_points"]}-percentage-point gap</b> between the best '
     'and worst-performing districts is not the result of random deterioration; it reflects historically '
     'inequitable infrastructure investment. The priority scoring framework already equity-weights '
     'underserved communities, ensuring resources flow to highest-need areas within each tier.'),

    ('4.  Shift from Reactive to Preventive Maintenance',
     f'Current City practice skews toward emergency repair after failure. Preventive maintenance '
     f'costs approximately <b>${s["cost_preventive_K"]}K per segment annually</b>, compared to '
     f'<b>${s["cost_replace_K"]}K for emergency replacement</b> after failure — a <b>{s["roi_pct"]}% '
     f'cost premium</b> for inaction. Shifting 40% of the maintenance budget toward preventive '
     'interventions within Year 2 is projected to reduce emergency repair spending by a third within '
     'three years, freeing capital for new installations.'),

    ('5.  Diversify and Sequence Funding Sources',
     'Do not wait for full municipal budget appropriation before beginning Phase 1. Ameritech '
     'recommends the following funding sequence: (a) FY2026 municipal allocation for Tier 2 critical '
     'segments; (b) Federal USDOT RAISE grant and FTA ADA improvement grants, applied within 90 days '
     'of Council approval; (c) Texas Department of Transportation Safe Routes to School and pedestrian '
     'safety matching funds; (d) Developer impact fee contributions tied to new construction permits '
     'in non-compliant districts; (e) Philanthropic partnerships for pilot equity-district projects '
     'that demonstrate replicable models.'),

    ('6.  Integrate 311 Data into Prioritization',
     f'The City\'s 311 system currently receives ADA and sidewalk complaints at meaningful volume '
     f'across all 10 districts. This data should be formally integrated into the asset management '
     'platform as a real-time leading indicator — complaints predict deficiency escalation 12–18 '
     'months before conditions reach the "poor" or "failed" threshold. Automated escalation rules '
     '(e.g., 3+ complaints at a single segment within 90 days triggers inspection) would extend the '
     'reach of the compliance team without proportional staffing increases.'),

    ('7.  Establish Public Accountability Dashboard',
     'Publish a public-facing ADA compliance dashboard (updated monthly) showing compliance rates '
     'by district, 311 response times, and remediation progress against the phased plan. Public '
     'transparency creates political accountability and helps sustain multi-year budget commitments '
     'across Council terms. Set a target of 80%+ public satisfaction in an annual accessibility '
     'survey beginning Year 2.'),
]

for title, text in recs:
    story.append(KeepTogether([
        Paragraph(f'<b>{title}</b>', sH3),
        body(text),
        Spacer(1, 0.06*inch),
    ]))

story.append(Spacer(1, 0.04*inch))

# ── Section 2: 5-Year Financial Summary ──────────────────────────────────────
story += section_title('5-Year Financial Summary')

story.append(body(
    f'Total estimated remediation cost across all priority tiers is <b>${s["total_remediation_M"]}M over '
    f'5 years</b>, or approximately ${s["cost_per_segment"]} per segment. The budget below is structured '
    'to front-load the highest-urgency work while maintaining a preventive maintenance base throughout '
    'the program. All figures are estimates based on Austin-area unit cost benchmarks and should be '
    'validated by a licensed civil engineer prior to contract award.'
))
story.append(Spacer(1, 0.06*inch))

yr1 = float(s['yr1_budget_M'])
yr2 = float(s['yr2_budget_M'])
yr3 = float(s['yr3_budget_M'])
yr4 = float(s['yr4_budget_M'])
yr5 = float(s['yr5_budget_M'])

fin_data = [
    [Paragraph('<b>Budget Item</b>', sLabel),
     Paragraph('<b>Year 1</b>', sLabel), Paragraph('<b>Year 2</b>', sLabel),
     Paragraph('<b>Year 3</b>', sLabel), Paragraph('<b>Yrs 4–5</b>', sLabel),
     Paragraph('<b>5-Yr Total</b>', sLabel)],
    ['Tier 2 — High Priority Remediation',
     f'${yr1}M', '—', '—', '—', f'${yr1}M'],
    ['Tier 3 — Medium Priority Remediation',
     f'${yr2}M', f'${yr2}M', '—', '—',
     f'${round(yr2*2, 1)}M'],
    ['Tier 4 — Low Priority / Preventive',
     f'${yr3}M', f'${yr3}M', f'${yr3}M',
     f'${round(yr4+yr5, 1)}M',
     f'${round(yr3*3+yr4+yr5, 1)}M'],
    ['ADA Compliance Coordinator (FTE)',
     '$125K', '$125K', '$125K', '$250K', '$625K'],
    ['Asset Management System (Capital)',
     '$350K', '—', '—', '—', '$350K'],
    [Paragraph('<b>TOTAL</b>', S('tb', fontName='Helvetica-Bold', fontSize=8)),
     Paragraph(f'<b>${yr1}M</b>',
               S('tv', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER, textColor=WHITE)),
     Paragraph(f'<b>${yr2}M</b>',
               S('tv2', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER, textColor=WHITE)),
     Paragraph(f'<b>${yr3}M</b>',
               S('tv3', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER, textColor=WHITE)),
     Paragraph(f'<b>${round(yr4+yr5, 1)}M</b>',
               S('tv4', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER, textColor=WHITE)),
     Paragraph(f'<b>${s["total_remediation_M"]}M</b>',
               S('tv5', fontName='Helvetica-Bold', fontSize=9, alignment=TA_CENTER, textColor=WHITE))],
]
ft = Table(fin_data, colWidths=[2.3*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch])
ft.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0),  NAVY),
    ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
    ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-2), [WHITE, LGRAY, WHITE, LGRAY]),
    ('BACKGROUND',  (0,-1), (-1,-1), TEAL),
    ('ALIGN',       (1,0),  (-1,-1), 'CENTER'),
    ('GRID',        (0,0),  (-1,-1), 0.4, MGRAY),
    ('TOPPADDING',  (0,0),  (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0),  (-1,-1), 6),
    ('BACKGROUND',  (-1,1), (-1,-2), colors.HexColor('#EBF5FB')),
    ('FONTNAME',    (-1,1), (-1,-2), 'Helvetica-Bold'),
    ('TEXTCOLOR',   (-1,1), (-1,-2), NAVY),
]))
story.append(ft)
story.append(Spacer(1, 0.05*inch))
story.append(Paragraph(
    f'Unit cost assumptions: curb ramp installation $18,000 · curb ramp repair $8,500 · '
    f'signal LPI upgrade $4,500 · surface replacement $12,000/segment · '
    f'preventive maintenance ${s["cost_preventive_K"]}K/segment/year.',
    sSmall))

story.append(Spacer(1, 0.10*inch))

# ── Section 3: Council Action Items ──────────────────────────────────────────
story += section_title('City Council Action Requested')

action_data = [[
    Paragraph(
        f'<b>1.</b>  Approve phased remediation plan — ${s["total_remediation_M"]}M over 5 years, '
        f'beginning with the <b>{s["tier2_count"]:,} Tier 2 high-priority segments</b> in Year 1.<br/><br/>'
        f'<b>2.</b>  Authorize ADA Compliance Coordinator position and asset management system '
        f'($125K operating + $350K capital) in the FY2026 budget.<br/><br/>'
        f'<b>3.</b>  Direct staff to submit federal USDOT RAISE and FTA ADA grant applications '
        f'within <b>90 days</b> of Council approval.<br/><br/>'
        f'<b>4.</b>  Establish quarterly compliance reporting to the Council Transportation '
        f'Committee, beginning Q3 FY2026.<br/><br/>'
        f'<b>5.</b>  Commission a licensed civil engineer to validate unit cost estimates and '
        f'finalize scope for Year 1 contract procurement.',
        S('act', fontName='Helvetica', fontSize=9, textColor=WHITE, leading=15,
          leftIndent=4, rightIndent=4))
]]
at = Table(action_data, colWidths=[6.5*inch])
at.setStyle(TableStyle([
    ('BACKGROUND',     (0,0), (-1,-1), NAVY),
    ('TOPPADDING',     (0,0), (-1,-1), 14),
    ('BOTTOMPADDING',  (0,0), (-1,-1), 14),
    ('LEFTPADDING',    (0,0), (-1,-1), 16),
    ('RIGHTPADDING',   (0,0), (-1,-1), 16),
    ('ROUNDEDCORNERS', [6]),
]))
story.append(at)

story.append(Spacer(1, 0.10*inch))
story.append(HRFlowable(width='100%', thickness=0.5, color=MGRAY, spaceAfter=6))
story.append(Paragraph(
    f'<i><b>Ameritech | Ameritech Consulting Group</b> conducted an independent analysis of the City of '
    f'Austin\'s Sidewalk Infrastructure. This is not a final audit. These recommendations are based '
    f'on publicly available data and independent analysis only, and do not substitute for a licensed '
    f'engineering assessment. Prepared by Ameritech Consulting Group · tiffany@a-techconsulting.com · '
    f'April 2026.</i>',
    S('disc', fontName='Helvetica-Oblique', fontSize=6.5, textColor=DGRAY, leading=9, alignment=TA_JUSTIFY)
))

# ── Build PDF ─────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
    topMargin=0.75*inch, bottomMargin=0.65*inch,
    title='Ameritech Recommendations — Austin ADA Sidewalk Infrastructure Analysis',
    author='Ameritech Consulting Group',
    subject='Strategic Recommendations — City of Austin Pedestrian ADA Analysis',
)
doc.build(story, onFirstPage=page_hf, onLaterPages=page_hf)
print(f'PDF saved → {OUTPUT}')
print(f'File size: {OUTPUT.stat().st_size / 1024:.0f} KB')
