"""Build the Austin Sidewalk Budget Analysis PDF report."""

import json, pathlib
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdfcanvas
from datetime import date

BASE = pathlib.Path('/Users/brownfamily/Documents/Pedestrian Crosswalk & ADA Accessibility Analysis')
OUT  = BASE / 'outputs'
FIG  = OUT / 'figures'
PDF  = OUT / 'Ameritech_Budget_Analysis.pdf'

with open(OUT / 'budget_stats.json') as f:
    B = json.load(f)

# ── Colors ────────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor('#1B3A6B')
TEAL    = colors.HexColor('#0E7C7B')
ORANGE  = colors.HexColor('#E87722')
LGRAY   = colors.HexColor('#F4F6F9')
MGRAY   = colors.HexColor('#9E9E9E')
DKGRAY  = colors.HexColor('#444444')
WHITE   = colors.white
RED_ERR = colors.HexColor('#C0392B')

TODAY   = date.today().strftime('%B %d, %Y')
TOTAL_PAGES = 4

# ── Page header / footer ──────────────────────────────────────────────────────
def page_header_footer(canv, doc):
    canv.saveState()
    W, H = letter

    # Navy header bar
    canv.setFillColor(NAVY)
    canv.rect(0, H - 0.5*inch, W, 0.5*inch, stroke=0, fill=1)
    canv.setFillColor(WHITE)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawString(0.5*inch, H - 0.33*inch, 'AMERITECH CONSULTING GROUP')
    canv.setFont('Helvetica', 8)
    canv.drawRightString(W - 0.5*inch, H - 0.33*inch,
                         'Austin Sidewalk Infrastructure — Budget Analysis FY2021–FY2025')

    # Light gray footer bar
    canv.setFillColor(LGRAY)
    canv.rect(0, 0, W, 0.45*inch, stroke=0, fill=1)
    canv.setFillColor(MGRAY)
    canv.setFont('Helvetica', 7)
    canv.drawString(0.5*inch, 0.17*inch,
                    'Tiffany Moore  •  Ameritech Consulting Group  •  tiffany@a-techconsulting.com  •  www.a-techconsulting.com  •  GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git')
    canv.drawRightString(W - 0.5*inch, 0.17*inch,
                         f'Page {doc.page} of {TOTAL_PAGES}  |  {TODAY}')
    canv.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, parent=styles['Normal'], **kw)

H1 = S('H1', fontSize=20, leading=24, textColor=NAVY, fontName='Helvetica-Bold',
        spaceAfter=6)
H2 = S('H2', fontSize=13, leading=16, textColor=NAVY, fontName='Helvetica-Bold',
        spaceAfter=4, spaceBefore=10)
H3 = S('H3', fontSize=10, leading=13, textColor=TEAL, fontName='Helvetica-Bold',
        spaceAfter=3, spaceBefore=6)
BODY = S('BODY', fontSize=9.5, leading=14, textColor=DKGRAY,
         fontName='Helvetica', spaceAfter=5)
SMALL = S('SMALL', fontSize=8, leading=11, textColor=MGRAY, fontName='Helvetica')
BOLD  = S('BOLD',  fontSize=9.5, leading=13, textColor=DKGRAY,
          fontName='Helvetica-Bold')
CENTER = S('CENTER', fontSize=9.5, leading=13, textColor=DKGRAY,
           fontName='Helvetica', alignment=TA_CENTER)
DISC  = S('DISC', fontSize=8, leading=11, textColor=MGRAY,
          fontName='Helvetica-Oblique', alignment=TA_CENTER, spaceAfter=2)
ATTR  = S('ATTR', fontSize=7.5, leading=10, textColor=MGRAY, fontName='Helvetica-Oblique')

# ── Helper: stat callout ──────────────────────────────────────────────────────
def stat_box(value, label, color=NAVY):
    tbl = Table([[
        Paragraph(f'<font size="22"><b>{value}</b></font>', S('sv', fontSize=22,
                  fontName='Helvetica-Bold', textColor=color, alignment=TA_CENTER)),
    ],[
        Paragraph(label, S('sl', fontSize=8.5, fontName='Helvetica',
                  textColor=DKGRAY, alignment=TA_CENTER)),
    ]], colWidths=[1.55*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), LGRAY),
        ('BOX',          (0,0), (-1,-1), 0.8, color),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[LGRAY]),
    ]))
    return tbl

def img(name, w=6.5*inch):
    p = FIG / name
    if p.exists():
        return Image(str(p), width=w, height=w*0.55)
    return Paragraph(f'[Chart: {name}]', SMALL)

# ── Build document ────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(PDF), pagesize=letter,
    topMargin=0.65*inch, bottomMargin=0.55*inch,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
)

story = []
W = 7.3 * inch   # usable width

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: Cover + Executive Summary
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 0.2*inch))

# Cover title block
cover = Table([[
    Paragraph('BUDGET ANALYSIS<br/>'
              '<font color="#0E7C7B">FY2021–FY2025</font>',
              S('CT', fontSize=26, fontName='Helvetica-Bold', textColor=NAVY,
                leading=30, alignment=TA_LEFT)),
]], colWidths=[W])
cover.setStyle(TableStyle([
    ('BACKGROUND',   (0,0),(-1,-1), LGRAY),
    ('TOPPADDING',   (0,0),(-1,-1), 16),
    ('BOTTOMPADDING',(0,0),(-1,-1), 16),
    ('LEFTPADDING',  (0,0),(-1,-1), 18),
    ('RIGHTPADDING', (0,0),(-1,-1), 18),
    ('BOX',          (0,0),(-1,-1), 2, NAVY),
    ('LINEBELOW',    (0,0),(-1,0),  3, TEAL),
]))
story.append(cover)
story.append(Spacer(1, 0.08*inch))

story.append(Paragraph(
    'City of Austin — Sidewalk Infrastructure Investment',
    S('sub', fontSize=14, fontName='Helvetica', textColor=TEAL, spaceAfter=2)
))
story.append(Paragraph(
    'Ameritech | Ameritech Consulting Group conducted an independent analysis of the '
    'City of Austin\'s Sidewalk Infrastructure. This is not a final audit.',
    ATTR
))
story.append(Spacer(1, 0.15*inch))
story.append(HRFlowable(width=W, thickness=1, color=NAVY))
story.append(Spacer(1, 0.12*inch))

# Stat callout row
stats_row = Table([[
    stat_box(f'${B["grand_total_m"]:.0f}M', '5-Year Total Investment', NAVY),
    stat_box(f'{B["total_miles"]:.0f} mi', 'Sidewalk Miles Completed', TEAL),
    stat_box(f'{B["total_segments"]:,}', 'Segments Built / Repaired', ORANGE),
    stat_box(B['peak_fy'], 'Peak Spending Year', NAVY),
]], colWidths=[W/4]*4, hAlign='CENTER')
stats_row.setStyle(TableStyle([
    ('LEFTPADDING', (0,0),(-1,-1), 4),
    ('RIGHTPADDING',(0,0),(-1,-1), 4),
]))
story.append(stats_row)
story.append(Spacer(1, 0.15*inch))

# Executive Summary
story.append(Paragraph('Executive Summary', H2))
story.append(Paragraph(
    f'Between <b>FY2021 and FY2025</b>, the City of Austin invested an estimated '
    f'<b>${B["grand_total_m"]:.0f} million</b> in sidewalk infrastructure — encompassing '
    f'new construction, rehabilitation, ADA improvements, and active transportation connectivity. '
    f'This analysis draws on three publicly accessible data sources: '
    f'the <i>City of Austin ArcGIS FeatureServer</i> (Sidewalks_Bond_Complete layer, 16,637 segments), '
    f'the <i>Austin Open Data Portal Budget Performance Dataset</i> (g5k8-8sud, FY2026 baseline), '
    f'and <i>TxDOT Statewide Transportation Improvement Program</i> records for federal grant awards.',
    BODY
))
story.append(Paragraph(
    f'The five-year program delivered <b>{B["total_miles"]:.0f} lane-miles of sidewalk</b> '
    f'across {B["total_segments"]:,} individual segments citywide. Capital construction — funded '
    f'primarily through the 2016 and 2020 Austin Mobility Bonds — accounted for '
    f'${B["capital_total_m"]:.0f}M ({B["capital_total_m"]/B["grand_total_m"]*100:.0f}% of total). '
    f'Operating maintenance programs contributed ${B["operating_total_m"]:.0f}M, '
    f'while federal and grant funding (Transportation Alternatives Program, RAISE grants, '
    f'Safe Routes to School) provided an additional ${B["federal_total_m"]:.0f}M.',
    BODY
))
story.append(Paragraph(
    f'Despite this investment, Ameritech\'s concurrent compliance analysis of 175,609 assessed '
    f'sidewalk segments found that <b>78.5% of the network remains non-compliant or only partially '
    f'compliant with ADA standards</b>. The 5-year spend represents approximately '
    f'{B["grand_total_m"]/506.3*100:.1f}% of the estimated $506.3M needed for full network remediation, '
    f'underscoring a significant and growing infrastructure gap.',
    BODY
))

story.append(Spacer(1, 0.1*inch))
story.append(img('budget_by_source.png', w=W))
story.append(Paragraph(
    'Figure 1. Annual sidewalk infrastructure spending by funding source, FY2021–FY2025. '
    'Capital construction costs estimated using ATD unit rates ($185/LF new, $95/LF rehabilitation). '
    'Operating budgets derived from Austin Open Data Portal budget dataset (g5k8-8sud).',
    DISC
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: Year-by-Year Breakdown Table + Chart
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph('Annual Spending Breakdown', H2))
story.append(Paragraph(
    'The table below shows the estimated allocation across three funding streams for each '
    'Austin fiscal year (October 1 – September 30). Capital figures reflect actual completions '
    'recorded in Austin\'s public ArcGIS layers; operating and federal figures are derived from '
    'the FY2026 baseline budget dataset and TxDOT STIP records respectively.',
    BODY
))
story.append(Spacer(1, 0.1*inch))

# Summary table
tbl_data = [
    ['Fiscal Year', 'Bond Capital\nConstruction', 'Operating\nBudget', 'Federal /\nGrants',
     'Annual\nTotal', 'Miles\nBuilt', 'Segments'],
]
col_w = [0.85*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 0.85*inch, 0.85*inch]

for row in B['rows']:
    tbl_data.append([
        row['fy'],
        f'${row["capital_m"]:.1f}M',
        f'${row["operating_m"]:.1f}M',
        f'${row["federal_m"]:.1f}M',
        f'${row["total_m"]:.1f}M',
        f'{row["miles"]:.1f}',
        f'{row["segments"]:,}',
    ])

# Totals row
tbl_data.append([
    'TOTAL',
    f'${B["capital_total_m"]:.1f}M',
    f'${B["operating_total_m"]:.1f}M',
    f'${B["federal_total_m"]:.1f}M',
    f'${B["grand_total_m"]:.1f}M',
    f'{B["total_miles"]:.1f}',
    f'{B["total_segments"]:,}',
])

tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
tbl.setStyle(TableStyle([
    # Header
    ('BACKGROUND',   (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,0), 8.5),
    ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING',   (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    # Data rows
    ('FONTSIZE',     (0,1), (-1,-2), 9),
    ('ROWBACKGROUNDS',(0,1),(-1,-2),[WHITE, LGRAY]),
    ('GRID',         (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
    # Totals row
    ('BACKGROUND',   (0,-1), (-1,-1), TEAL),
    ('TEXTCOLOR',    (0,-1), (-1,-1), WHITE),
    ('FONTNAME',     (0,-1), (-1,-1), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,-1), (-1,-1), 9),
    # Highlight total column
    ('TEXTCOLOR',    (4,1), (4,-2), NAVY),
    ('FONTNAME',     (4,1), (4,-2), 'Helvetica-Bold'),
]))
story.append(tbl)
story.append(Spacer(1, 0.05*inch))
story.append(Paragraph(
    'Sources: Austin ArcGIS FeatureServer — Sidewalks_Bond_Complete (actual completions). '
    'Operating budget from Austin Open Data Portal g5k8-8sud (FY2026 baseline, back-projected at '
    '~7%/year growth). Federal grants from TxDOT STIP public records.',
    ATTR
))

story.append(Spacer(1, 0.12*inch))
story.append(img('budget_miles_completed.png', w=W))
story.append(Paragraph(
    'Figure 2. Bond-funded sidewalk lane-miles completed per Austin fiscal year. '
    'FY2024 was the peak delivery year with 42.1 miles — driven by acceleration of '
    '2016 Mobility Bond closeout and 2020 Bond program ramp-up.',
    DISC
))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: Cumulative Investment + Gap Analysis
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph('Cumulative Investment & Funding Gap', H2))

story.append(img('budget_cumulative.png', w=W))
story.append(Paragraph(
    'Figure 3. Cumulative sidewalk infrastructure investment FY2021–FY2025. '
    f'Total capital construction (bond-funded) reached ${B["capital_total_m"]:.0f}M by end of FY2025.',
    DISC
))

story.append(Spacer(1, 0.12*inch))
story.append(img('budget_gap_analysis.png', w=W))
story.append(Paragraph(
    'Figure 4. 5-year actual spend vs. estimated remaining remediation need. '
    'Full ADA-compliant remediation of Austin\'s 175,609-segment network is '
    'estimated at $506.3M per Ameritech\'s independent cost analysis.',
    DISC
))

story.append(Spacer(1, 0.1*inch))

# Key Findings callout
findings = [
    [Paragraph('Key Findings', S('kfh', fontSize=11, fontName='Helvetica-Bold',
               textColor=WHITE, alignment=TA_LEFT))],
    [Paragraph(
        f'<b>1. Spending accelerated in FY2024.</b>  Bond capital completions peaked at $34.2M '
        f'(42 miles), driven by closeout of the 2016 Mobility Bond and 2020 Bond construction '
        f'acceleration.<br/><br/>'
        f'<b>2. Operating budget lagged demand.</b>  The dedicated Sidewalk Infrastructure '
        f'operating program grew from ~$5.2M (FY2021) to ~$7.4M (FY2025) — a 42% increase — '
        f'but covers only routine maintenance for the network\'s 175,609 segments.<br/><br/>'
        f'<b>3. Federal dollars are underpowered.</b>  Combined federal/grant funding totaled '
        f'${B["federal_total_m"]:.0f}M over 5 years — only {B["federal_total_m"]/B["grand_total_m"]*100:.0f}% of the '
        f'total program. Peer cities leveraging IIJA formula funds capture 30–40% federal match.<br/><br/>'
        f'<b>4. The gap is widening.</b>  At the FY2021–FY2025 average annual investment of '
        f'${B["grand_total_m"]/5:.0f}M/year, full network remediation would take '
        f'{506.3 / (B["grand_total_m"]/5):.0f} years. Inflation in construction costs compounds this gap.',
        S('kfb', fontSize=9, fontName='Helvetica', textColor=DKGRAY, leading=13)
    )],
]
kf_tbl = Table(findings, colWidths=[W])
kf_tbl.setStyle(TableStyle([
    ('BACKGROUND',   (0,0), (-1,0), NAVY),
    ('BACKGROUND',   (0,1), (-1,-1), LGRAY),
    ('TOPPADDING',   (0,0), (-1,-1), 8),
    ('BOTTOMPADDING',(0,0), (-1,-1), 8),
    ('LEFTPADDING',  (0,0), (-1,-1), 12),
    ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ('BOX',          (0,0), (-1,-1), 1, NAVY),
]))
story.append(kf_tbl)

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: Methodology, Data Sources & Recommendations
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph('Methodology & Data Sources', H2))

story.append(Paragraph('<b>Capital Construction (Bond-Funded)</b>', H3))
story.append(Paragraph(
    'Actual sidewalk segment completions were retrieved from the City of Austin\'s '
    '<i>Sidewalks_Bond_Complete</i> ArcGIS FeatureServer layer '
    '(services.arcgis.com/0L95CJ0VTaxqcmED). '
    'This layer records every segment where construction was completed with bond funding, '
    'including date of completion and linear footage (EPSG:2277, Texas State Plane Central, feet). '
    '16,637 segments were queried and filtered by Austin fiscal year (October 1 – September 30). '
    'Cost per linear foot was estimated using Austin Transportation Department unit rates: '
    '$185/LF for new sidewalk construction and $95/LF for rehabilitation, '
    'with a 35%/65% rehab-to-new blended rate yielding ~$154/LF effective cost.',
    BODY
))

story.append(Paragraph('<b>Operating Budget</b>', H3))
story.append(Paragraph(
    'Operating expenditure data was retrieved from the Austin Open Data Portal '
    'Budget Performance Dataset (dataset ID: g5k8-8sud, updated through FY2026 Q2). '
    'The <i>Sidewalk Infrastructure</i> program and <i>Transportation Engineering</i> activity '
    'within the Austin Transportation & Public Works department were summed to produce the '
    'FY2026 baseline of $7.36M. Prior-year budgets were back-projected using ATD\'s '
    'documented ~7%/year budget growth rate between FY2021 and FY2026, consistent with '
    'Austin\'s published Adopted Budget documents.',
    BODY
))

story.append(Paragraph('<b>Federal & Grant Funding</b>', H3))
story.append(Paragraph(
    'Federal funding estimates are based on publicly reported grant awards from the '
    'Texas Department of Transportation Statewide Transportation Improvement Program (STIP), '
    'including: Transportation Alternatives Program (TAP/STBG-TA), RAISE/BUILD discretionary '
    'grants, and Safe Routes to School (SRTS) formula funds awarded to Austin ISD and '
    'neighboring districts. Amounts represent awarded federal shares; local match is '
    'captured within the capital and operating budget figures above.',
    BODY
))

story.append(Spacer(1, 0.08*inch))
story.append(HRFlowable(width=W, thickness=0.75, color=MGRAY))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph('Policy Recommendations', H2))

recs = [
    ('Increase Annual Operating Investment',
     f'The current ${B["operating_total_m"]/5:.1f}M/year sidewalk operating budget is insufficient '
     f'to maintain the growing network. Ameritech recommends increasing annual operating funding '
     f'to $12M+ by FY2027, consistent with the FY2026 adopted budget trajectory.'),
    ('Pursue Federal Match Aggressively',
     'Austin captured ~14% federal co-funding in FY2021–FY2025. Under the Bipartisan '
     'Infrastructure Law, TAP set-asides are 5× larger than pre-2021 levels. '
     'A dedicated federal grants team within ATD could triple federal capture to $15M+/year.'),
    ('Accelerate 2020 Mobility Bond Delivery',
     f'FY2024\'s {B["rows"][3]["miles"]:.0f}-mile delivery rate is the program high-water mark. '
     'Maintaining this rate through the 2020 Bond program lifespan requires preserving '
     'construction contractor capacity and design-phase pipeline.'),
    ('Adopt a 15-Year Capital Plan',
     'Full network remediation ($506.3M) requires a long-range capital program beyond '
     'individual bond cycles. A 15-year sidewalk capital plan with annual $34M authorization '
     'would close the gap while maintaining manageable annual debt service.'),
    ('Equity-Weighted Spending Allocation',
     'Districts 1, 2, and 10 show the highest compliance deficits. Future bond program '
     'scopes should reserve ≥50% of annual construction budgets for historically '
     'underinvested neighborhoods to close the 17.6-point equity gap identified '
     'in Ameritech\'s compliance analysis.'),
]

for i, (title, body) in enumerate(recs, 1):
    rec_data = [[
        Paragraph(f'{i}', S('rn', fontSize=16, fontName='Helvetica-Bold',
                  textColor=TEAL, alignment=TA_CENTER)),
        Paragraph(f'<b>{title}</b><br/>{body}',
                  S('rb', fontSize=9, fontName='Helvetica', textColor=DKGRAY, leading=13))
    ]]
    rec_tbl = Table(rec_data, colWidths=[0.45*inch, W-0.55*inch])
    rec_tbl.setStyle(TableStyle([
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (0,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('LINEBEFORE',   (1,0), (1,-1), 2, TEAL),
    ]))
    story.append(rec_tbl)
    story.append(Spacer(1, 0.04*inch))

story.append(Spacer(1, 0.1*inch))

# Footer disclaimer box
disc_box = Table([[
    Paragraph(
        f'<b>About This Analysis</b>  ·  Ameritech Consulting Group conducted an independent '
        f'analysis of publicly available City of Austin data. This is not a final audit. '
        f'Budget figures represent estimates derived from public data sources and should be '
        f'verified against official City financial records. Cost-per-linear-foot unit rates '
        f'are based on Austin\'s published contractor bid data and TxDOT cost guidance. '
        f'Tiffany Moore • Ameritech Consulting Group • tiffany@a-techconsulting.com • www.a-techconsulting.com • GitHub: https://github.com/ameritechconsulting/austin-ada-accessibility-analysis.git',
        ATTR
    )
]], colWidths=[W])
disc_box.setStyle(TableStyle([
    ('BACKGROUND',   (0,0), (-1,-1), LGRAY),
    ('BOX',          (0,0), (-1,-1), 0.5, MGRAY),
    ('TOPPADDING',   (0,0), (-1,-1), 7),
    ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ('LEFTPADDING',  (0,0), (-1,-1), 10),
    ('RIGHTPADDING', (0,0), (-1,-1), 10),
]))
story.append(disc_box)

# ── Build PDF ──────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=page_header_footer, onLaterPages=page_header_footer)
print(f'✓  PDF written → {PDF}')
print(f'   Size: {PDF.stat().st_size / 1024:.0f} KB')
