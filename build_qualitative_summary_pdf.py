"""
5-page qualitative narrative summary PDF — Austin Pedestrian & ADA Analysis.
Cover page + 4 narrative content pages. Policy-brief / consulting report style.
Ameritech Consulting Group — April 2026.
"""
import json, pathlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether, PageBreak,
)

BASE   = pathlib.Path('/Users/brownfamily/Documents/Pedestrian Crosswalk & ADA Accessibility Analysis')
FIGS   = BASE / 'outputs' / 'figures'
OUTPUT = BASE / 'outputs' / 'Austin_ADA_Qualitative_Summary.pdf'

with open(BASE / 'data' / 'processed' / 'summary_stats.json') as f:
    s = json.load(f)

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor('#1B3A6B')
TEAL  = colors.HexColor('#2E86AB')
AMBER = colors.HexColor('#E8A838')
RED   = colors.HexColor('#C0392B')
GREEN = colors.HexColor('#27AE60')
LGRAY = colors.HexColor('#F4F6F8')
MGRAY = colors.HexColor('#BDC3C7')
DGRAY = colors.HexColor('#555555')
WHITE = colors.white
BLACK = colors.black

CONTACT = (
    'Tiffany Moore  •  Ameritech Consulting Group  •  tiffany@a-techconsulting.com'
    '  •  www.a-techconsulting.com  •  '
    'GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git'
)
CONTACT_SHORT = (
    'Tiffany Moore  •  Ameritech Consulting Group  •  tiffany@a-techconsulting.com'
    '  •  www.a-techconsulting.com'
)

# ── Canvas callbacks ───────────────────────────────────────────────────────────
def cover_page(cv, doc):
    cv.saveState()
    w, h = letter

    # Navy top band
    cv.setFillColor(NAVY)
    cv.rect(0, h - 3.4*inch, w, 3.4*inch, fill=1, stroke=0)
    cv.setFillColor(TEAL)
    cv.rect(0, h - 3.55*inch, w, 0.15*inch, fill=1, stroke=0)
    cv.setFillColor(AMBER)
    cv.rect(0, h - 3.70*inch, w, 0.15*inch, fill=1, stroke=0)

    # Title
    cv.setFillColor(WHITE)
    cv.setFont('Helvetica-Bold', 27)
    cv.drawCentredString(w/2, h - 1.15*inch, 'THE STATE OF PEDESTRIAN')
    cv.drawCentredString(w/2, h - 1.62*inch, 'ACCESSIBILITY IN AUSTIN')
    cv.setFont('Helvetica', 11)
    cv.setFillColor(MGRAY)
    cv.drawCentredString(w/2, h - 2.05*inch,
        'A Qualitative Analysis of ADA Compliance, Equity, and the Path Forward')
    cv.setFont('Helvetica', 9)
    cv.setFillColor(TEAL)
    cv.drawCentredString(w/2, h - 2.55*inch,
        'City of Austin, Texas  |  Assessment Period: Jan 2020 – Dec 2024  |  April 2026')

    # Stat boxes
    BY = h - 5.2*inch
    boxes = [
        (GREEN,  '21.5%',   'Fully ADA\nCompliant'),
        (RED,    '78.5%',   'Non-Compliant\nor Partial'),
        (AMBER,  '$506.3M', 'Est. Full\nRemediation'),
        (NAVY,   '17.6 pts','District\nEquity Gap'),
    ]
    bw, bh, gap = 1.38*inch, 1.0*inch, 0.22*inch
    x0 = (w - (4*bw + 3*gap)) / 2
    for i, (bg, val, lbl) in enumerate(boxes):
        bx = x0 + i*(bw + gap)
        cv.setFillColor(bg)
        cv.roundRect(bx, BY, bw, bh, 6, fill=1, stroke=0)
        cv.setFillColor(WHITE)
        cv.setFont('Helvetica-Bold', 17)
        cv.drawCentredString(bx + bw/2, BY + 0.63*inch, val)
        cv.setFont('Helvetica', 7)
        for j, ln in enumerate(lbl.split('\n')):
            cv.drawCentredString(bx + bw/2, BY + 0.30*inch - j*0.145*inch, ln)

    # Tagline
    cv.setFillColor(DGRAY)
    cv.setFont('Helvetica-Oblique', 9.5)
    cv.drawCentredString(w/2, BY - 0.45*inch,
        "Austin’s sidewalk infrastructure is failing the people who need it most.")
    cv.setFont('Helvetica', 9)
    cv.drawCentredString(w/2, BY - 0.65*inch,
        'This report examines who bears that burden — and what must change.')

    # Contents list
    cy = BY - 1.15*inch
    cv.setFillColor(NAVY)
    cv.setFont('Helvetica-Bold', 9)
    cv.drawString(0.75*inch, cy, 'INSIDE THIS REPORT')
    cv.setStrokeColor(TEAL)
    cv.setLineWidth(2)
    cv.line(0.75*inch, cy - 0.08*inch, 4.1*inch, cy - 0.08*inch)
    cv.setFont('Helvetica', 9)
    cv.setFillColor(DGRAY)
    sections = [
        'Page 1  —  Austin at a Crossroads: The Accessibility Crisis',
        'Page 2  —  A Tale of Two Austins: Geographic & Equity Disparities',
        'Page 3  —  Who Is Left Behind: The Human Cost',
        'Page 4  —  From Compliance to Commitment: The Path Forward',
    ]
    for i, sec in enumerate(sections):
        cv.drawString(0.75*inch, cy - 0.32*inch - i*0.225*inch, f'  {sec}')

    # Footer
    cv.setFillColor(NAVY)
    cv.rect(0, 0, w, 0.75*inch, fill=1, stroke=0)
    cv.setFillColor(WHITE)
    cv.setFont('Helvetica-Bold', 8)
    cv.drawString(0.45*inch, 0.56*inch, 'AMERITECH CONSULTING GROUP')
    cv.setFont('Helvetica', 6.5)
    cv.drawRightString(w - 0.45*inch, 0.56*inch, CONTACT_SHORT)
    cv.setFillColor(MGRAY)
    cv.setFont('Helvetica', 6)
    cv.drawCentredString(w/2, 0.38*inch,
        'GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git')
    cv.setFillColor(TEAL)
    cv.setFont('Helvetica', 7)
    cv.drawCentredString(w/2, 0.20*inch,
        'Independent Analysis · Not a Final Audit · Data: Austin Open Data Portal · U.S. Census ACS 2022')

    cv.restoreState()


def page_hf(cv, doc):
    cv.saveState()
    w, h = letter
    pg = doc.page - 1  # content page number; cover is page 1

    cv.setFillColor(NAVY)
    cv.rect(0, h - 0.55*inch, w, 0.55*inch, fill=1, stroke=0)
    cv.setFillColor(WHITE)
    cv.setFont('Helvetica-Bold', 8)
    cv.drawString(0.45*inch, h - 0.22*inch, 'AMERITECH CONSULTING GROUP')
    cv.setFont('Helvetica', 7.5)
    cv.drawRightString(w - 0.45*inch, h - 0.22*inch,
        'City of Austin — Pedestrian Crosswalk & ADA Accessibility Analysis  |  Qualitative Summary')

    cv.setFillColor(LGRAY)
    cv.rect(0, 0, w, 0.60*inch, fill=1, stroke=0)
    cv.setStrokeColor(MGRAY)
    cv.setLineWidth(0.5)
    cv.line(0, 0.60*inch, w, 0.60*inch)
    cv.setFillColor(DGRAY)
    cv.setFont('Helvetica', 6.5)
    cv.drawString(0.45*inch, 0.38*inch, CONTACT_SHORT)
    cv.drawRightString(w - 0.45*inch, 0.38*inch, f'Page {pg} of 4  |  CONFIDENTIAL')
    cv.setFont('Helvetica', 6)
    cv.drawString(0.45*inch, 0.20*inch,
        'GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git')

    cv.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
_sid = 0
def S(base='', **kw):
    global _sid
    _sid += 1
    return ParagraphStyle(f'_s{_sid}_{base}', **kw)

sH1  = S('H1', fontName='Helvetica-Bold', fontSize=13.5, textColor=NAVY,
          spaceAfter=4, spaceBefore=6, leading=16)
sH2  = S('H2', fontName='Helvetica-Bold', fontSize=10, textColor=TEAL,
          spaceAfter=3, spaceBefore=6, leading=13)
sBod = S('Bod', fontName='Helvetica', fontSize=8.8, textColor=BLACK,
          spaceAfter=5, leading=13.5, alignment=TA_JUSTIFY)
sBul = S('Bul', fontName='Helvetica', fontSize=8.5, textColor=DGRAY,
          spaceAfter=3, leading=12.5, leftIndent=14, firstLineIndent=-10)
sCap = S('Cap', fontName='Helvetica-Oblique', fontSize=7.5, textColor=DGRAY,
          spaceAfter=5, leading=10, alignment=TA_CENTER)
sCite= S('Cite', fontName='Helvetica-Oblique', fontSize=6.5, textColor=DGRAY,
          leading=9.5, alignment=TA_JUSTIFY)


def hr(c=TEAL, t=1.5):
    return HRFlowable(width='100%', thickness=t, color=c, spaceAfter=6, spaceBefore=2)

def page_title(txt):
    return [Paragraph(txt.upper(), sH1), hr()]

def body(txt):    return Paragraph(txt, sBod)

def bul(txt):
    return Paragraph(f'<bullet>•</bullet> {txt}', sBul)


def stat_box(val, lbl, bg, col_w=1.5*inch):
    t = Table([
        [Paragraph(val, S('sv', fontName='Helvetica-Bold', fontSize=18,
                          textColor=WHITE, alignment=TA_CENTER, leading=22))],
        [Paragraph(lbl, S('sl', fontName='Helvetica', fontSize=7.5,
                          textColor=WHITE, alignment=TA_CENTER, leading=10))],
    ], colWidths=[col_w])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    return t


def pull_quote(txt):
    inner = Paragraph(
        f'“{txt}”',
        S('pq', fontName='Helvetica-BoldOblique', fontSize=10,
          textColor=NAVY, alignment=TA_JUSTIFY, leading=14.5))
    t = Table([[inner]], colWidths=[5.9*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), LGRAY),
        ('LINEBEFORE',  (0,0), (0,-1), 4, TEAL),
        ('TOPPADDING',  (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING',(0,0), (-1,-1), 10),
    ]))
    return t


def pop_panel(title, stat, stat_lbl, text, accent):
    """Coloured-top population impact panel for 2×2 grid."""
    rows = [
        [Paragraph(title, S('ppt', fontName='Helvetica-Bold', fontSize=9.5,
                            textColor=accent, leading=12, spaceAfter=3))],
        [Table([[
            Paragraph(stat, S('pps', fontName='Helvetica-Bold', fontSize=19,
                              textColor=NAVY, leading=23, alignment=TA_LEFT)),
            Paragraph(stat_lbl, S('ppsl', fontName='Helvetica', fontSize=7.5,
                                  textColor=DGRAY, leading=11)),
        ]], colWidths=[1.0*inch, 1.85*inch],
           style=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                  ('LEFTPADDING',(0,0),(-1,-1),0),
                  ('RIGHTPADDING',(0,0),(-1,-1),0),
                  ('TOPPADDING',(0,0),(-1,-1),0),
                  ('BOTTOMPADDING',(0,0),(-1,-1),2)])],
        [Paragraph(text, S('ppb', fontName='Helvetica', fontSize=8.1,
                           textColor=BLACK, leading=12.5, alignment=TA_JUSTIFY))],
    ]
    inner = Table(rows, colWidths=[2.8*inch])
    inner.setStyle(TableStyle([
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (0,0),   7),
        ('BOTTOMPADDING', (0,-1),(0,-1),  8),
        ('TOPPADDING',    (0,1), (0,-1),  2),
        ('BOTTOMPADDING', (0,0), (0,-2),  2),
    ]))
    outer = Table([[inner]], colWidths=[3.0*inch])
    outer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LGRAY),
        ('LINEABOVE',  (0,0), (-1,0),  3, accent),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING', (0,0), (-1,-1),0),
        ('RIGHTPADDING',(0,0), (-1,-1),0),
    ]))
    return outer


def principle_row(bg, title, text):
    t = Table([[
        Paragraph(title, S('prt', fontName='Helvetica-Bold', fontSize=8.5,
                           textColor=WHITE, leading=11, alignment=TA_CENTER)),
        Paragraph(text,  S('prb', fontName='Helvetica', fontSize=8.3,
                           textColor=BLACK, leading=12.5, alignment=TA_JUSTIFY)),
    ]], colWidths=[1.05*inch, 5.25*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,0),   bg),
        ('BACKGROUND',    (1,0), (1,0),   LGRAY),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN',         (0,0), (0,0),   'CENTER'),
        ('LEFTPADDING',   (0,0), (0,0),   4),
        ('RIGHTPADDING',  (0,0), (0,0),   4),
        ('LEFTPADDING',   (1,0), (1,0),   8),
        ('RIGHTPADDING',  (1,0), (1,0),   8),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LINEBELOW',     (0,0), (-1,-1), 0.5, MGRAY),
    ]))
    return t


# ═════════════════════════════════════════════════════════════════════════════
# STORY
# ═════════════════════════════════════════════════════════════════════════════
story = []

# Cover page — story reserves the page; canvas callback draws the design
story.append(Spacer(1, 9.4*inch))
story.append(PageBreak())

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — AUSTIN AT A CROSSROADS
# ─────────────────────────────────────────────────────────────────────────────
story += page_title('Page 1 — Austin at a Crossroads: The Accessibility Crisis')

story.append(body(
    'Austin, Texas is celebrated as one of America’s most dynamic cities — a hub of '
    'technology, culture, and economic growth. Yet beneath the gleaming campuses and booming '
    'skyline lies an infrastructure crisis that receives far too little public attention: the '
    'sustained failure of the city’s pedestrian network to serve the residents who depend on '
    'it most. An independent analysis of all <b>175,609 active sidewalk segments</b> across '
    'Austin’s 10 council districts — spanning the full assessment period from January '
    '2020 through December 2024 — reveals a picture defined by broken ramps, inaccessible '
    'signals, deteriorating surfaces, and a compliance gap that affects nearly four out of every '
    'five crosswalks in the city.'
))
story.append(Spacer(1, 0.06*inch))

# Stat row
sr = Table([[
    stat_box(f'{s["pct_fully_compliant"]}%', 'Fully\nCompliant',    GREEN, 1.5*inch),
    stat_box(f'{s["pct_partially_compliant"]}%','Partially\nCompliant', AMBER, 1.5*inch),
    stat_box(f'{s["pct_non_compliant"]}%',   'Non-\nCompliant',     RED,   1.5*inch),
    stat_box(s['n_unknown_pending'],         'Pending\nAssessment', NAVY,  1.5*inch),
]], colWidths=[1.6*inch]*4, hAlign='CENTER')
sr.setStyle(TableStyle([
    ('ALIGN',  (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
]))
story.append(sr)
story.append(Spacer(1, 0.08*inch))

story.append(Paragraph('What Non-Compliance Really Means', sH2))
story.append(body(
    'Raw percentages can obscure the lived reality of inaccessible infrastructure. For a wheelchair '
    'user, a missing curb ramp is not an inconvenience — it is a barrier that ends a journey '
    'before it begins. For a blind pedestrian, an intersection without an audible signal is a hazard '
    'that cannot be safely crossed. For an elderly resident with a walker, a cracked and uneven '
    'surface is a genuine fall risk. These are not edge cases. They are the daily reality for '
    'hundreds of thousands of Austin residents. Of the city’s 175,609 assessed segments, only '
    f'<b>{s["n_fully_compliant"]} (21.5%) fully meet ADA standards</b>. Another '
    f'{s["n_partially_compliant"]} (50.6%) are partially compliant — functional at a basic '
    f'level but carrying deficiencies that create real barriers. A stark <b>{s["n_non_compliant"]} '
    '(27.9%) are fully non-compliant</b>, exhibiting multiple violations or missing critical '
    'features entirely.'
))
story.append(Spacer(1, 0.04*inch))

story.append(Paragraph('Three Defining Infrastructure Failures', sH2))
story.append(body(
    '<b>Curb Ramps — The Most Basic Access Point:</b> The curb ramp is the fundamental gateway '
    'between sidewalk and street. Yet <b>167 locations in Austin lack ramps entirely</b>, and 93 '
    'more have ramps so damaged they require immediate replacement. An additional <b>644 locations '
    'are missing legally required truncated dome tactile warning surfaces</b> — the yellow '
    'domed panels that alert blind and visually impaired pedestrians to the transition zone. These '
    'are not obscure technical requirements. They are the minimum features that make a crossing '
    'usable for someone with a mobility or visual disability.'
))
story.append(Spacer(1, 0.02*inch))
story.append(body(
    '<b>Signal Accessibility — A Near-Total Failure:</b> Of Austin’s 1,331 signalized '
    'intersections, only <b>324 (24.3%) have Leading Pedestrian Intervals (LPI)</b> — the '
    'audible and tactile countdown systems that allow blind and visually impaired pedestrians to '
    'cross safely. The remaining <b>75.7% lack these federally recommended features</b>. '
    'Additionally, 45.4% of signal locations have push buttons that are obstructed or unreachable '
    'from an accessible approach — meaning even where signals exist, they often cannot be '
    'activated by someone using a wheelchair or with limited reach.'
))
story.append(Spacer(1, 0.02*inch))
story.append(body(
    '<b>Surface Conditions — An Epidemic of Hazards:</b> ADA standards require crosswalk '
    'surfaces to be firm, stable, and slip-resistant. Currently, <b>41,494 segments have hazardous '
    'surface conditions</b> — 34,366 rated Poor and 7,128 rated Failed, requiring immediate '
    'replacement. Another 40,899 segments have improper cross-slope or running grade, conditions '
    'that cause wheelchairs and mobility devices to tip or pull sideways. The city’s '
    'infrastructure is deteriorating at approximately 3.2% annually — meaning every year of '
    'inaction converts today’s manageable deficiencies into tomorrow’s crises.'
))

story.append(PageBreak())

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — A TALE OF TWO AUSTINS
# ─────────────────────────────────────────────────────────────────────────────
story += page_title('Page 2 — A Tale of Two Austins: Geographic & Equity Disparities')

story.append(body(
    'One of the most troubling findings of this analysis is not the overall compliance rate '
    '— it is the pattern of <i>where</i> the failures are concentrated. Across Austin’s '
    f'10 council districts, compliance rates range from a high of just '
    f'<b>{s["highest_compliance_pct"]}%</b> in District {s["highest_compliance_district"]} '
    f'({s["best_district_name"]}) to a low of <b>{s["lowest_compliance_pct"]}%</b> in '
    f'District {s["lowest_compliance_district"]} ({s["worst_district_name"]}). This '
    f'<b>{s["equity_gap_points"]}-percentage-point gap</b> is not random. It follows the contours '
    'of income, race, and historical patterns of infrastructure investment — and it tells a '
    'story about which communities Austin has consistently prioritized and which it has left behind.'
))
story.append(Spacer(1, 0.05*inch))

img_dist = FIGS / 'compliance_by_district.png'
if img_dist.exists():
    story.append(Image(str(img_dist), width=6.0*inch, height=2.9*inch, hAlign='CENTER'))
    story.append(Paragraph(
        f'Figure 1: ADA compliance rate by council district. City average: '
        f'{s["pct_fully_compliant"]}% (dashed line). Districts below 20% shown in red.',
        sCap))
story.append(Spacer(1, 0.05*inch))

story.append(Paragraph('The Inverse Equity Pattern', sH2))
story.append(body(
    'A consistent and deeply concerning pattern emerges when compliance data is mapped against '
    'socioeconomic indicators: <b>the neighborhoods with the greatest need for accessible '
    'infrastructure are receiving the least of it.</b> Districts with higher concentrations of '
    'low-income residents, communities of color, and transit-dependent populations consistently '
    'show lower ADA compliance rates. The equity scatter analysis confirms this relationship is '
    'not coincidental — it reflects decades of unequal budget allocation, deferred '
    'maintenance in lower-income neighborhoods, and a planning culture that has not yet embedded '
    'equity as a foundational principle of infrastructure investment.'
))
story.append(body(
    f'Consider: District 1 (North Austin / Rundberg) has the city’s highest compliance at '
    f'{s["highest_compliance_pct"]}% — yet that still means only about one in three segments '
    'is fully compliant. It is a striking indictment of the system’s overall failure. '
    'Meanwhile, communities in East and Southeast Austin — areas with higher proportions of '
    'low-income residents who depend on walking and transit for daily mobility — face '
    'compliance rates in the low-to-mid 20s. These residents cannot easily substitute a car trip '
    'for an inaccessible pedestrian route. For them, the failure of the sidewalk network is not '
    'an abstract equity concern. It is a daily constraint on their freedom of movement.'
))
story.append(Spacer(1, 0.04*inch))

story.append(Paragraph('Schools, Transit, and the Compounding Burden', sH2))
story.append(body(
    f'The equity problem reaches its most acute expression where accessibility matters most. '
    f'Across Austin’s <b>{s["num_schools"]} AISD school campuses</b>, approximately '
    f'<b>{s["n_school_nc"]} adjacent sidewalk segments are non-compliant</b> — meaning '
    'thousands of students with disabilities face daily barriers on routes their peers navigate '
    'without a second thought. The right to access education on equal terms is a civil rights '
    f'guarantee, not a planning aspiration. Near Austin’s <b>1,000 public transit stops</b>, '
    f'<b>{s["n_transit_nc"]} adjacent segments are non-compliant</b> — directly compromising '
    'access for approximately 159,000 daily transit riders, a population that disproportionately '
    'includes low-income residents, the elderly, and people with disabilities. When a bus stop '
    'cannot be safely reached, the transit system’s promise of mobility becomes hollow.'
))

img_eq = FIGS / 'equity_scatter.png'
if img_eq.exists():
    story.append(Image(str(img_eq), width=4.8*inch, height=2.7*inch, hAlign='CENTER'))
    story.append(Paragraph(
        'Figure 2: Districts with higher equity need scores show consistently lower ADA '
        'compliance rates — confirming a structural, not random, pattern of unequal investment.',
        sCap))

story.append(PageBreak())

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — WHO IS LEFT BEHIND
# ─────────────────────────────────────────────────────────────────────────────
story += page_title('Page 3 — Who Is Left Behind: The Human Cost')

story.append(body(
    'Infrastructure data can feel abstract — miles of sidewalk, percentages of compliance, '
    'counts of deficiencies. But behind every non-compliant crosswalk is a person whose '
    'independence, safety, and dignity are compromised. This analysis identifies four populations '
    'whose daily lives are most directly shaped by Austin’s accessibility failures — '
    'and whose experiences must be at the center of the city’s response.'
))
story.append(Spacer(1, 0.06*inch))

panels = [
    pop_panel(
        'Seniors & Older Adults',
        f'{s["seniors_affected"]}',
        'residents 65+\nin Travis County',
        (f'Austin’s senior population — {s["pct_senior"]}% of Travis County '
         'residents — faces the steepest barriers. Mobility limitations are common among '
         'older adults, and the combination of missing curb ramps, hazardous surfaces, and '
         'insufficient signal crossing time creates environments that many seniors cannot navigate '
         'safely. For this group, inaccessible infrastructure does not just limit mobility — '
         'it enforces isolation and diminishes independence.'),
        TEAL),
    pop_panel(
        'Residents with Disabilities',
        f'{s["n_disability"]}',
        'Austinites with\na reported disability',
        (f'At {s["pct_disability"]}% of the total population, Austin’s disability community '
         'represents one of the largest groups directly affected. Mobility, visual, auditory, and '
         'cognitive disabilities each create distinct barriers — from missing ramps for '
         'wheelchair users to absent audible signals for the blind. Current infrastructure meets '
         'almost none of these needs consistently across the city.'),
        RED),
    pop_panel(
        'Students & Families',
        f'{s["n_school_nc"]}',
        'school-adjacent\nnon-compliant segments',
        ('For the roughly 75,500 Austin ISD students, safe school crossings are a daily '
         'necessity and a legal right. Non-compliant segments adjacent to school campuses fall '
         'hardest on students with disabilities, who depend on accessible infrastructure for '
         'equal access to education. The school-to-street connection is a civil rights issue, '
         'not a maintenance afterthought.'),
        GREEN),
    pop_panel(
        'Transit-Dependent Riders',
        f'{s["n_transit_nc"]}',
        'non-compliant segments\nnear transit stops',
        ('Approximately 159,000 Austinites use Capital Metro daily — a population '
         'disproportionately comprising low-income residents, the elderly, and people with '
         'disabilities. Non-compliant segments adjacent to transit stops mean that the first '
         'and last steps of a transit journey are often the most dangerous. Inaccessible '
         'access infrastructure renders the transit system’s promise of mobility hollow.'),
        AMBER),
]

grid = Table(
    [[panels[0], panels[1]], [panels[2], panels[3]]],
    colWidths=[3.1*inch, 3.1*inch],
)
grid.setStyle(TableStyle([
    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING',   (0,0), (-1,-1), 5),
    ('RIGHTPADDING',  (0,0), (-1,-1), 5),
    ('TOPPADDING',    (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(grid)
story.append(Spacer(1, 0.08*inch))

story.append(Paragraph('The Compounding Effect: Health, Independence, and Dignity', sH2))
story.append(body(
    'ADA compliance failures are not merely legal violations — they are public health crises '
    'unfolding in slow motion. When streets are inaccessible, people with mobility limitations '
    'reduce their physical activity. Reduced mobility leads to elevated rates of cardiovascular '
    'disease, obesity, and diabetes. Social isolation follows: the inability to reach stores, '
    'medical appointments, community centers, and neighbors. <b>The medical literature is '
    'unambiguous: accessible built environments directly improve health outcomes, particularly '
    'for older adults and people with disabilities.</b> Austin’s infrastructure gaps are '
    'not just a planning failure. They are a driver of health inequity at population scale '
    '— and every year of continued inaction compounds the cost in human terms.'
))
story.append(body(
    'The compounding nature of these barriers is also critical to understand. A senior resident '
    'in a low-income neighborhood may face a non-compliant curb ramp <i>and</i> a missing audible '
    'signal <i>and</i> a hazardous surface condition — all at the same intersection. Each '
    'deficiency multiplies the difficulty; together, they can make a route simply impassable. For '
    'those without alternatives — no personal vehicle, no family member to drive them — '
    'this is not a minor inconvenience. It is confinement.'
))

story.append(PageBreak())

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — FROM COMPLIANCE TO COMMITMENT
# ─────────────────────────────────────────────────────────────────────────────
story += page_title('Page 4 — From Compliance to Commitment: The Path Forward')

story.append(body(
    'The picture this analysis presents is serious — but it is not hopeless. Every '
    'deficiency identified is one that can be remediated. Every equity gap is one that '
    'deliberate policy can close. The question before the City of Austin is not whether to act, '
    'but how urgently and how wisely. The analysis points toward a clear framework — one '
    'grounded in evidence, structured by priority, and designed to maximize both human impact '
    'and financial efficiency.'
))
story.append(Spacer(1, 0.06*inch))

story.append(Paragraph('Four Principles for a Credible Response', sH2))

story.append(principle_row(RED, 'Safety\nFirst',
    f'The most dangerous conditions — missing ramps at schools, non-functional signals at '
    f'high-volume crossings, failed surfaces near transit stops — must be addressed within '
    f'90 days. These conditions expose the City to ADA enforcement action and, more critically, '
    f'to preventable injuries. The {s["n_school_nc"]} school-adjacent and {s["n_transit_nc"]} '
    f'transit-adjacent non-compliant segments represent the non-negotiable starting point.'))

story.append(principle_row(TEAL, 'Equity as\nPrinciple',
    'Remediation sequencing cannot default to a first-come, first-served approach that perpetuates '
    'historical inequities. The priority scoring framework weights equity at 30% — ensuring '
    'underserved communities, school zones, transit corridors, and healthcare facilities receive '
    'preferential treatment. This is not merely a values statement; it is a structural requirement '
    'for the program to fulfill its legal and moral purpose.'))

story.append(principle_row(GREEN, 'Prevention\nas Strategy',
    f'Preventive maintenance costs ${s["cost_preventive_K"]}K per asset annually versus '
    f'${s["cost_replace_K"]}K for emergency replacement — a {s["roi_pct"]}% cost savings. '
    'A systematic maintenance program pays for itself within a single budget cycle. The city '
    'cannot afford <i>not</i> to invest in prevention: every year of deferral converts today’s '
    '“Poor” conditions into tomorrow’s “Failed”, doubling or tripling '
    'future costs.'))

story.append(principle_row(AMBER, 'Governance\n& Account.',
    'Infrastructure does not maintain itself, and good intentions without organizational structure '
    'produce no results. A dedicated ADA Compliance Coordinator, a standing compliance committee '
    'with monthly meetings, and a public-facing performance dashboard are essential — not '
    'optional — components of any credible improvement program. Without accountability '
    'infrastructure, remediation infrastructure will not follow.'))

story.append(Spacer(1, 0.09*inch))
story.append(Paragraph(
    f'The Financial Case: Why ${s["total_remediation_M"]}M Is the Right Investment', sH2))
story.append(body(
    f'The total estimated remediation cost of <b>${s["total_remediation_M"]}M over five years</b> '
    'is significant — but the cost of inaction is higher. ADA non-compliance creates direct '
    'legal liability: the Department of Justice has increasingly pursued enforcement actions against '
    'municipalities, and settlement costs in comparable cities have reached hundreds of millions of '
    'dollars. Beyond litigation risk, infrastructure deteriorating at 3.2% annually means every '
    f'year of delay grows the bill. The <b>${s["yr1_budget_M"]}M Year 1 investment</b> is not '
    'discretionary spending — it is preventing a far larger obligation from accumulating '
    'silently in the deferred maintenance backlog.'
))
story.append(Spacer(1, 0.05*inch))

story.append(Paragraph('Three Actions That Can Begin This Week', sH2))
story.append(bul(
    f'<b>Authorize the High-Priority Project List ({s["tier2_count"]:,} segments).</b> Approve '
    f'the {s["n_school_nc"]} school-adjacent and {s["n_transit_nc"]} transit-adjacent projects '
    'for immediate mobilization. These can reach active construction within 30 days of council '
    'authorization and represent the clearest liability-reduction investments available.'
))
story.append(bul(
    f'<b>Create the ADA Compliance Coordinator Position (${s["staffing_annual_K"]}K/yr).</b> '
    'A single dedicated FTE provides the organizational nerve center for all remediation, '
    'monitoring, and reporting activity. Without this role, accountability diffuses across '
    'departments and progress stalls. This is the highest-leverage governance investment '
    'the City can make.'
))
story.append(bul(
    f'<b>Commission the Digital Asset Management System (${s["monitoring_K"]}K).</b> '
    'Real-time infrastructure tracking enables data-driven maintenance scheduling, public '
    'transparency, and quarterly progress reporting to Council. The city cannot manage '
    'what it cannot measure.'
))
story.append(Spacer(1, 0.08*inch))

story.append(pull_quote(
    'Every resident — regardless of disability, age, or zip code — has the right to '
    'safely walk to school, to work, to the bus stop, to their doctor. The legal obligation to '
    'provide this has existed since 1990. The moral obligation has existed far longer.'
))
story.append(Spacer(1, 0.08*inch))

story.append(body(
    'Austin has a choice. It can continue on the current trajectory — deferred maintenance, '
    'growing legal liability, and a widening gap between the city’s national reputation for '
    'innovation and the daily experience of its most vulnerable residents. Or it can commit, now, '
    'to the harder and more important work of becoming a city where accessibility is not an '
    'afterthought, but a foundation. This analysis provides the evidence. The path is clear. '
    'What is required now is the will to walk it.'
))
story.append(Spacer(1, 0.06*inch))

story.append(Paragraph(
    f'<i>Independent analysis conducted by <b>Ameritech Consulting Group</b> for the City of '
    f'Austin. This document is not a final audit. Assessment covers January 2020–December '
    f'2024 across all 175,609 active sidewalk segments in Austin’s 10 council districts. '
    f'Data: City of Austin Open Data Portal (vchz-d9ng, p53x-x73x, xwdj-i9he), ArcGIS '
    f'FeatureServer (curb ramps, AISD schools, CMTA stops, Council Districts), U.S. Census '
    f'ACS 2022 (Travis County, TX). '
    f'Tiffany Moore • tiffany@a-techconsulting.com • www.a-techconsulting.com</i>',
    sCite
))

# ── Build ─────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
    topMargin=0.75*inch, bottomMargin=0.65*inch,
    title='Austin ADA Accessibility Analysis — Qualitative Summary',
    author='Ameritech Consulting Group',
    subject='City of Austin Pedestrian Crosswalk & ADA Accessibility Analysis',
)

doc.build(story, onFirstPage=cover_page, onLaterPages=page_hf)
print(f'PDF saved → {OUTPUT}')
print(f'File size: {OUTPUT.stat().st_size / 1024:.0f} KB')
