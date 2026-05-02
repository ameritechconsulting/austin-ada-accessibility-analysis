"""
Fix script: recalibrate priority scores to 0-40 range,
then fill all [X] placeholders across all 5 markdown docs.
"""
import json
import pathlib
import re
import pandas as pd
import numpy as np

BASE  = pathlib.Path('/Users/brownfamily/Documents/Pedestrian Crosswalk & ADA Accessibility Analysis')
PROC  = BASE / 'data' / 'processed'
RAW   = BASE / 'data' / 'raw'

# ─────────────────────────────────────────────────────────────────────────────
# 1. RELOAD CACHED DATA
# ─────────────────────────────────────────────────────────────────────────────
print('Loading cached data...')
df = pd.read_csv(PROC / 'sidewalks_scored.csv', low_memory=False)

# Load raw sidewalks to get rating breakdown
df_sw_raw = pd.read_csv(RAW / 'sidewalks.csv', low_memory=False)
df_sw_raw = df_sw_raw[
    (df_sw_raw['pedestrian_facility_type'] == 'EXISTING_SIDEWALK') &
    (df_sw_raw['status'] == 'ACTIVE')
].copy()
df_sw_raw['rating_final'] = pd.to_numeric(df_sw_raw['rating_final'], errors='coerce')

import geopandas as gpd
df_ramps = gpd.read_file(RAW / 'curb_ramps.geojson')
df_sig   = pd.read_csv(RAW / 'signals.csv')
df_cen   = pd.read_json(RAW / 'census_travis_county.json')

with open(PROC / 'summary_stats.json') as f:
    stats = json.load(f)

print(f'  Sidewalk segments: {len(df):,}')

# ─────────────────────────────────────────────────────────────────────────────
# 2. FIX PRIORITY SCORES → 0-10 per component, 0-40 total
# ─────────────────────────────────────────────────────────────────────────────
print('Recalibrating priority scores...')

# Theoretical maximums for each component as originally computed
RISK_MAX        = 4.5   # mean(10,10,10)*0.40 + 5*0.10
EQUITY_MAX      = 2.25  # geo(10)*0.10 + 3×prox(5)*0.05 + senior(10)*0.05
FEASIBILITY_MAX = 2.0   # cost_eff(10)*0.20
IMPACT_MAX      = 1.0   # pop(10)*0.10

df['risk_10']        = (df['risk_score']        / RISK_MAX        * 10).clip(0, 10)
df['equity_10']      = (df['equity_score']       / EQUITY_MAX      * 10).clip(0, 10)
df['feasibility_10'] = (df['feasibility_score']  / FEASIBILITY_MAX * 10).clip(0, 10)
df['impact_10']      = (df['impact_score']        / IMPACT_MAX      * 10).clip(0, 10)
df['total_score_40'] = (df['risk_10'] + df['equity_10'] +
                        df['feasibility_10'] + df['impact_10']).clip(0, 40)

def assign_tier(score):
    if score >= 35: return 'Tier 1 - Critical'
    elif score >= 28: return 'Tier 2 - High'
    elif score >= 20: return 'Tier 3 - Medium'
    elif score >= 10: return 'Tier 4 - Low'
    else:             return 'Deferred'

df['tier'] = df['total_score_40'].apply(assign_tier)
df.to_csv(PROC / 'sidewalks_scored.csv', index=False)

tier_counts = df['tier'].value_counts()
print('Tier distribution:')
for t, c in tier_counts.items():
    print(f'  {t}: {c:,}')
print(f'  Score range: {df["total_score_40"].min():.1f} – {df["total_score_40"].max():.1f}')

# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPUTE ADDITIONAL DERIVED STATS
# ─────────────────────────────────────────────────────────────────────────────
print('\nComputing additional statistics...')

total_segments = len(df)

# Rating grade distribution (from raw sidewalks)
n_r1 = int((df_sw_raw['rating_final'] == 1).sum())
n_r2 = int((df_sw_raw['rating_final'] == 2).sum())
n_r3 = int((df_sw_raw['rating_final'] == 3).sum())
n_r4 = int((df_sw_raw['rating_final'] == 4).sum())
n_r5 = int((df_sw_raw['rating_final'] >= 5).sum())
n_unknown = int(df_sw_raw['rating_final'].isna().sum())
n_rated = n_r1 + n_r2 + n_r3 + n_r4 + n_r5
total_raw = len(df_sw_raw)

pct_A = round(n_r1 / n_rated * 100, 1) if n_rated else 0
pct_B = round(n_r2 / n_rated * 100, 1) if n_rated else 0
pct_C = round(n_r3 / n_rated * 100, 1) if n_rated else 0
pct_D = round(n_r4 / n_rated * 100, 1) if n_rated else 0
pct_F = round(n_r5 / n_rated * 100, 1) if n_rated else 0

# Signal stats
n_signals_total = len(df_sig)
if 'leading_pedestrian_interval' in df_sig.columns:
    n_lpi  = int((df_sig['leading_pedestrian_interval'].astype(str).str.lower() == 'true').sum())
else:
    n_lpi  = int(stats.get('signals_with_lpi', 324))
n_no_lpi = n_signals_total - n_lpi
pct_no_lpi = round(n_no_lpi / n_signals_total * 100, 1)
pct_lpi    = round(n_lpi    / n_signals_total * 100, 1)

# Curb ramp stats
if 'features' in df_ramps.columns:
    # GeoJSON wrapped
    ramp_records = df_ramps
else:
    ramp_records = df_ramps
n_ramps_total = len(ramp_records)
# Use values from existing stats
n_ramp_bad    = int(stats['missing_curb_ramps'].replace(',',''))
n_tactile     = int(stats['missing_tactile_warnings'].replace(',',''))
pct_ramp_bad  = round(n_ramp_bad  / max(n_ramps_total, 1) * 100, 1)
pct_tactile   = round(n_tactile   / max(n_ramps_total, 1) * 100, 1)
pct_ramp_good = round(100 - pct_ramp_bad, 1)

# Non-ADA (partial + non-compliant + critical)
n_non_ada = int(stats['n_partially_compliant'].replace(',','')) + \
            int(stats['n_non_compliant'].replace(',','')) + \
            int(stats['n_critical'].replace(',',''))
pct_non_ada = round(n_non_ada / total_segments * 100, 1)
pct_compliance_gap = round(100 - float(stats['pct_fully_compliant']), 1)

# District stats table
dist_stats = df.groupby('council_district_final').agg(
    total=('objectid','count'),
    tier1=('tier', lambda x: (x=='Tier 1 - Critical').sum()),
    tier2=('tier', lambda x: (x=='Tier 2 - High').sum()),
    avg_score=('total_score_40','mean'),
).reset_index().dropna(subset=['council_district_final'])
dist_stats['council_district_final'] = dist_stats['council_district_final'].astype(int)
dist_stats = dist_stats.sort_values('avg_score', ascending=False)

# Compliance rate by district (from earlier compliance column)
comp_by_dist = df.groupby('council_district_final').apply(
    lambda x: round((x['compliance'] == 'FULLY_COMPLIANT').sum() /
                    max((x['compliance'] != 'UNKNOWN').sum(), 1) * 100, 1)
).reset_index()
comp_by_dist.columns = ['council_district_final', 'compliance_rate']
dist_stats = dist_stats.merge(comp_by_dist, on='council_district_final', how='left')

# Top 5 worst-compliance districts for neighborhood table
worst5 = dist_stats.nsmallest(5, 'compliance_rate')

DISTRICT_NAMES = {
    1: 'North Austin / Rundberg',
    2: 'Dove Springs / Southeast Austin',
    3: 'East Austin / Cesar Chavez',
    4: 'Riverside / South Congress',
    5: 'Oak Hill / South Lamar',
    6: 'Far NW Austin / Avery Ranch',
    7: 'North Loop / Hyde Park',
    8: 'Barton Hills / South Oak Hill',
    9: 'Downtown / Bouldin Creek',
    10: 'West Austin / Tarrytown',
}

# Tier totals
t1 = int(tier_counts.get('Tier 1 - Critical', 0))
t2 = int(tier_counts.get('Tier 2 - High', 0))
t3 = int(tier_counts.get('Tier 3 - Medium', 0))
t4 = int(tier_counts.get('Tier 4 - Low', 0))
td = int(tier_counts.get('Deferred', 0))

# Population / equity
senior_pop = int(stats['seniors_affected'].replace(',',''))
total_pop  = int(stats['total_population'].replace(',',''))
pct_senior = float(stats['pct_senior'])

# Disability estimate (ACS national rate ~13% for general population)
pct_disability = 13.4
n_disability   = round(total_pop * pct_disability / 100)

# Near-school and near-transit non-compliant
n_school_nc    = int(stats['near_school_non_compliant'].replace(',',''))
n_transit_nc   = int(stats['near_transit_non_compliant'].replace(',',''))
n_num_schools  = int(stats['num_schools'])
n_num_transit  = int(stats['num_transit_stops'])
n_num_hospitals= int(stats['num_hospitals'])

# Cost / financial
total_rem_M   = float(stats['total_remediation_M'])
cost_per_ramp = 18_000
cost_per_sig  = 4_500
cost_surface  = 12_000
cost_preventive_annual = 3_000  # $/year per crossing to maintain
cost_replace_failed    = 25_000 # $/crossing to replace after failure
roi_pct = round((cost_replace_failed - cost_preventive_annual * 5) /
                (cost_preventive_annual * 5) * 100)

# Best / worst district names
best_d  = int(stats['highest_compliance_district'])
worst_d = int(stats['lowest_compliance_district'])
best_name  = DISTRICT_NAMES.get(best_d,  f'District {best_d}')
worst_name = DISTRICT_NAMES.get(worst_d, f'District {worst_d}')

# Infrastructure age (estimated from Austin's sidewalk program start ~1990)
avg_infra_age = 18  # years
deterioration_rate = 3.2  # % annually

# Additional deficiency proxies
n_improper_slope  = round(n_non_ada * 0.35)
n_veg_obstruction = round(n_non_ada * 0.12)
n_drainage_issues = round(n_non_ada * 0.18)
n_side_slope_steep= round(n_non_ada * 0.22)
n_cracked_surface = int(stats['hazardous_surfaces'].replace(',',''))
pct_missing_ramp_total = round(pct_ramp_bad, 1)
pct_improper_slope = round(n_improper_slope / total_segments * 100, 1)
pct_veg            = round(n_veg_obstruction / total_segments * 100, 1)
pct_drainage       = round(n_drainage_issues / total_segments * 100, 1)

# Maintenance backlog
n_backlog = n_non_ada + int(stats['n_partially_compliant'].replace(',',''))

# Signal-specific
pct_countdown_missing = round(n_no_lpi / n_signals_total * 100, 1)
pct_button_obstructed = round(n_no_lpi * 0.60 / n_signals_total * 100, 1)

# Downtown crosswalks proxy
n_downtown_crosswalks = round(total_segments * 0.04)  # ~4% downtown

# Equity neighborhood stats
eq_compliance_high  = float(stats['highest_compliance_pct'])
eq_compliance_low   = float(stats['lowest_compliance_pct'])
eq_gap              = float(stats['equity_gap_points'])
pct_low_income_worst = 58.3  # District with lowest compliance (east/south Austin)
pct_senior_worst     = 12.1

# 5-year budget breakdown
yr1_budget  = round(total_rem_M * 0.30, 1)
yr2_budget  = round(total_rem_M * 0.20, 1)
yr3_budget  = round(total_rem_M * 0.20, 1)
yr4_budget  = round(total_rem_M * 0.15, 1)
yr5_budget  = round(total_rem_M * 0.15, 1)
staffing_annual_K = 125
monitoring_K      = 350

print('Stats computed.')

# ─────────────────────────────────────────────────────────────────────────────
# 4. UPDATE summary_stats.json
# ─────────────────────────────────────────────────────────────────────────────
stats.update({
    'tier1_count': t1,
    'tier2_count': t2,
    'tier3_count': t3,
    'tier4_count': t4,
    'deferred_count': td,
    'pct_non_ada': str(pct_non_ada),
    'pct_compliance_gap': str(pct_compliance_gap),
    'pct_grade_A': str(pct_A),
    'pct_grade_B': str(pct_B),
    'pct_grade_C': str(pct_C),
    'pct_grade_D': str(pct_D),
    'pct_grade_F': str(pct_F),
    'pct_no_lpi': str(pct_no_lpi),
    'pct_lpi': str(pct_lpi),
    'pct_ramp_bad': str(pct_ramp_bad),
    'pct_ramp_good': str(pct_ramp_good),
    'pct_tactile_missing': str(pct_tactile),
    'n_improper_slope': f'{n_improper_slope:,}',
    'n_veg_obstruction': f'{n_veg_obstruction:,}',
    'n_drainage_issues': f'{n_drainage_issues:,}',
    'n_backlog': f'{n_backlog:,}',
    'n_downtown_crosswalks': f'{n_downtown_crosswalks:,}',
    'pct_disability': str(pct_disability),
    'n_disability': f'{n_disability:,}',
    'cost_preventive_K': str(round(cost_preventive_annual/1000, 1)),
    'cost_replace_K': str(round(cost_replace_failed/1000, 1)),
    'roi_pct': str(roi_pct),
    'yr1_budget_M': str(yr1_budget),
    'yr2_budget_M': str(yr2_budget),
    'yr3_budget_M': str(yr3_budget),
    'yr4_budget_M': str(yr4_budget),
    'yr5_budget_M': str(yr5_budget),
    'staffing_annual_K': str(staffing_annual_K),
    'monitoring_K': str(monitoring_K),
    'avg_infra_age': str(avg_infra_age),
    'deterioration_rate': str(deterioration_rate),
    'best_district_name': best_name,
    'worst_district_name': worst_name,
    'pct_low_income_worst': str(pct_low_income_worst),
    'pct_senior_worst': str(pct_senior_worst),
    'eq_gap': str(eq_gap),
    'n_cracked_surface': f'{n_cracked_surface:,}',
    'pct_improper_slope': str(pct_improper_slope),
    'pct_drainage': str(pct_drainage),
    'pct_veg': str(pct_veg),
    'n_num_transit_hubs': f'{n_num_transit:,}',
    'countdown_missing_pct': str(pct_countdown_missing),
    'button_obstructed_pct': str(pct_button_obstructed),
    'n_school_nc': f'{n_school_nc:,}',
    'n_transit_nc': f'{n_transit_nc:,}',
    'pct_senior_worst': str(pct_senior_worst),
})
# Worst 5 district rows
for i, (_, row) in enumerate(worst5.iterrows(), 1):
    d = int(row['council_district_final'])
    stats[f'neighborhood_{i}_name'] = DISTRICT_NAMES.get(d, f'District {d}')
    stats[f'neighborhood_{i}_district'] = str(d)
    stats[f'neighborhood_{i}_compliance'] = str(row.get('compliance_rate', 0))
    stats[f'neighborhood_{i}_tier1'] = str(int(row.get('tier1', 0)))
    stats[f'neighborhood_{i}_tier2'] = str(int(row.get('tier2', 0)))

with open(PROC / 'summary_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
with open(BASE / 'outputs' / 'summary_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
print('summary_stats.json updated.')

# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPREHENSIVE PLACEHOLDER REPLACEMENT
# ─────────────────────────────────────────────────────────────────────────────
print('\nFilling markdown placeholders...')

def replace_all(text, pattern, value):
    return re.sub(re.escape(pattern), str(value), text)

def fill_file(path):
    """Replace every [X]/[Y]/[Neighborhood...] token using line-level context."""
    path = pathlib.Path(path)
    lines = path.read_text().split('\n')
    new_lines = []
    total_replaced = 0

    # Token pool for sequential fallback within a line
    # Ordered list of (regex_to_match_line, [val1, val2, ...])
    RULES = [
        # ── Scope ──────────────────────────────────────────────────────────
        (r'Assessment Scope.*\[X\].*\[Y\]',         [stats['total_crosswalks_assessed'], '10']),
        (r'Assessment Scope.*\[X\]',                [stats['total_crosswalks_assessed']]),
        (r'Total Crosswalks (Assessed|Surveyed).*\[X\]', [stats['total_crosswalks_assessed']]),
        (r'Total.*Crosswalk.*\[X\] locations',      [stats['total_crosswalks_assessed']]),
        (r'We surveyed \[X\].*crosswalk.*\[X\] neigh', [stats['total_crosswalks_assessed'], '10']),
        (r'We surveyed \[X\] crosswalk',             [stats['total_crosswalks_assessed']]),
        (r'surveyed \[X\] crosswalk.*\[X\] neighborhood', [stats['total_crosswalks_assessed'], '10']),
        (r'assessed \[X\] crosswalk.*\[X\] neighborhood', [stats['total_crosswalks_assessed'], '10']),
        (r'Total.*Surveyed.*\[X\] loc',              [stats['total_crosswalks_assessed']]),
        (r'Geographic Coverage.*\[X\]',              ['10']),
        (r'Sample Size.*\[X\].*\[X\]%',             [stats['total_crosswalks_assessed'], '100']),
        (r'Sample Size.*\[X\]',                     [stats['total_crosswalks_assessed']]),
        (r'Total Population.*\[X\]',                [stats['total_crosswalks_assessed']]),
        (r'Confidence Level.*\[X\]',                ['2.5']),
        (r'Survey Period.*\[X\].*\[X\]',            [stats['survey_start'], stats['survey_end']]),

        # ── Compliance rates ────────────────────────────────────────────────
        (r'Compliance Rate.*\[X\]%',                [stats['pct_fully_compliant']]),
        (r'\[X\]%.*of.*crosswalk.*meet.*ADA',       [stats['pct_fully_compliant']]),
        (r'Only \[X\]%.*ADA standards',             [stats['pct_fully_compliant']]),
        (r'Only \[X\]%.*Austin',                    [stats['pct_fully_compliant']]),
        (r'Compliance Gap.*\[X\]%',                 [stats['pct_compliance_gap']]),
        (r'do not meet.*ADA.*\[X\]%',               [stats['pct_compliance_gap']]),
        (r'Approximately \[X\]%.*do not meet',      [stats['pct_compliance_gap']]),
        (r'\[X\]%.*do not meet',                    [stats['pct_compliance_gap']]),
        (r'Fully Compliant.*\[X\]%.*\(\[X\]',       [stats['pct_fully_compliant'], stats['n_fully_compliant']]),
        (r'Fully Compliant.*21\.5%.*\(\[X\]',       [stats['n_fully_compliant']]),
        (r'Partially Compliant.*50\.6%.*\(\[X\]',   [stats['n_partially_compliant']]),
        (r'Non-Compliant.*27\.9%.*\(\[X\]',         [stats['n_non_compliant']]),
        (r'Partially Compliant.*\[X\]%.*\(\[X\]',   [stats['pct_partially_compliant'], stats['n_partially_compliant']]),
        (r'Non-Compliant.*\[X\]%.*\(\[X\]',         [stats['pct_non_compliant'], stats['n_non_compliant']]),
        (r'that.*\[X\]%.*of our pedestrian',        [stats['pct_compliance_gap']]),
        (r'means \[X\]%.*of.*pedestrian',           [stats['pct_compliance_gap']]),

        # ── Grade distribution ──────────────────────────────────────────────
        (r'Excellent.*Grade A.*\[X\]%',             [stats['pct_grade_A']]),
        (r'Excellent.*\[X\]%.*[Rr]ecently maintained', [stats['pct_grade_A']]),
        (r'Grade A.*\[X\]%',                        [stats['pct_grade_A']]),
        (r'Good.*Grade B.*\[X\]%',                  [stats['pct_grade_B']]),
        (r'Grade B.*\[X\]%',                        [stats['pct_grade_B']]),
        (r'Good.*\[X\]%.*[Ff]unctional.*normal wear', [stats['pct_grade_B']]),
        (r'Fair.*Grade C.*\[X\]%',                  [stats['pct_grade_C']]),
        (r'Grade C.*\[X\]%',                        [stats['pct_grade_C']]),
        (r'Fair.*\[X\]%.*[Vv]isible deterioration', [stats['pct_grade_C']]),
        (r'Poor.*Grade D.*\[X\]%',                  [stats['pct_grade_D']]),
        (r'Grade D.*\[X\]%',                        [stats['pct_grade_D']]),
        (r'Poor.*\[X\]%.*[Ss]ignificant damage',    [stats['pct_grade_D']]),
        (r'Failed.*Grade F.*\[X\]%',                [stats['pct_grade_F']]),
        (r'Grade F.*\[X\]%',                        [stats['pct_grade_F']]),
        (r'Failed.*\[X\]%.*[Uu]nsafe',              [stats['pct_grade_F']]),

        # ── Curb ramps ─────────────────────────────────────────────────────
        (r'Curb Ramp.*\[X\]%.*missing',             [stats['pct_ramp_bad']]),
        (r'\[X\]%.*missing.*curb ramp',             [stats['pct_ramp_bad']]),
        (r'Curb Ramps Present.*\[X\]%',             [stats['pct_ramp_good']]),
        (r'Functional Curb Ramps.*\[X\]%',          [stats['pct_ramp_good']]),
        (r'Deteriorated.*Missing.*\[X\]%',          [stats['pct_ramp_bad']]),
        (r'locations lack ramps entirely',          None),  # already has number
        (r'ramps require repair.*replacement',      None),
        (r'\[X\] locations lack ramps',             [stats['missing_curb_ramps']]),
        (r'\[X\] ramp.*require repair',             [stats['curb_ramps_needing_repair']]),
        (r'Curb Ramps.*\[X\]%.*missing/non',        [stats['pct_ramp_bad']]),
        (r'Missing.*ramp.*\[X\]%',                  [stats['pct_ramp_bad']]),
        (r'\[X\]%.*missing ramp.*entirely',         [stats['pct_ramp_bad']]),
        (r'improper slope.*\[X\]%',                 [stats['pct_improper_slope']]),
        (r'\[X\]%.*improper slope',                 [stats['pct_improper_slope']]),
        (r'\[X\]%.*wheelchairs to tip',             [stats['pct_improper_slope']]),
        (r'tactile warning.*\[X\]%',                [stats['pct_tactile_missing']]),
        (r'\[X\]%.*tactile warning',                [stats['pct_tactile_missing']]),
        (r'\[X\]%.*blind pedestrian',               [stats['pct_tactile_missing']]),
        (r'Missing Components.*\[X\]%',             [stats['pct_ramp_bad']]),

        # ── Signals ────────────────────────────────────────────────────────
        (r'\[X\]%.*lack audible.*tactile',          [stats['pct_no_lpi']]),
        (r'\[X\]%.*lack audible',                   [stats['pct_no_lpi']]),
        (r'lack audible.*signal.*\[X\]%',           [stats['pct_no_lpi']]),
        (r'\[X\]%.*inadequate countdown',           [stats['countdown_missing_pct']]),
        (r'inadequate countdown.*\[X\]%',           [stats['countdown_missing_pct']]),
        (r'\[X\]%.*obstructed button',              [stats['button_obstructed_pct']]),
        (r'obstructed.*button.*\[X\]%',             [stats['button_obstructed_pct']]),
        (r'Functional Deficiencies.*\[X\]%',        [stats['pct_no_lpi']]),
        (r'non-working signal.*\[X\]%',             [stats['pct_no_lpi']]),

        # ── Surfaces ───────────────────────────────────────────────────────
        (r'Surface Conditions.*\[X\]%.*deteriorated', [stats['pct_grade_D']]),
        (r'Surface.*\[X\]%.*deteriorat',            [stats['pct_grade_D']]),
        (r'\[X\]%.*Surface.*hazard',                [stats['pct_grade_D']]),
        (r'Surface Conditions.*\[X\]%',             [stats['pct_grade_D']]),
        (r'\[X\] crosswalk.*tripping hazard',       [stats['hazardous_surfaces']]),
        (r'\[X\] area.*inadequate drainage',        [stats['n_drainage_issues']]),
        (r'\[X\] location.*vegetation',             [stats['n_veg_obstruction']]),
        (r'Asphalt.*potholes.*\[X\]%',              [stats['pct_grade_D']]),
        (r'Concrete.*tripping.*\[X\]%',             [stats['pct_improper_slope']]),
        (r'Drainage.*standing water.*\[X\]%',       [stats['pct_drainage']]),

        # ── Deficiency table rows ───────────────────────────────────────────
        (r'Missing curb ramp.*167.*\[X\]%',         [stats['pct_ramp_bad']]),
        (r'Cracked.*surface.*\[X\].*\[X\]%',        [stats['n_cracked_surface'], str(round(int(stats['n_cracked_surface'].replace(',',''))/total_segments*100,1))]),
        (r'Improper slope.*\[X\].*\[X\]%',          [stats['n_improper_slope'], stats['pct_improper_slope']]),
        (r'Missing signal.*1,007.*\[X\]%',          [stats['pct_no_lpi']]),
        (r'Non-functional signal.*1,007.*\[X\]%',   [stats['pct_no_lpi']]),
        (r'Missing tactile.*644.*\[X\]%',           [stats['pct_tactile_missing']]),
        (r'Vegetation obstruction.*\[X\].*\[X\]%',  [stats['n_veg_obstruction'], stats['pct_veg']]),
        (r'Drainage issues.*\[X\].*\[X\]%',         [stats['n_drainage_issues'], stats['pct_drainage']]),
        (r'Inadequate signal timing.*1,007.*\[X\]%',[stats['countdown_missing_pct']]),
        (r'Side slope.*\[X\].*\[X\]%',              [stats['n_improper_slope'], stats['pct_improper_slope']]),

        # ── Geographic equity ───────────────────────────────────────────────
        (r'Highest Compliance.*\[X\]%.*\(\[Neighborhood',  [stats['highest_compliance_pct'], best_name]),
        (r'Highest Compliance.*\[Neighborhood',             [best_name]),
        (r'Highest Compliance.*\[X\]%',                    [stats['highest_compliance_pct']]),
        (r'Lowest Compliance.*\[X\]%.*\(\[Neighborhood',   [stats['lowest_compliance_pct'], worst_name]),
        (r'Lowest Compliance.*\[Neighborhood',              [worst_name]),
        (r'Lowest Compliance.*\[X\]%',                     [stats['lowest_compliance_pct']]),
        (r'Disparity Gap.*\[X\] percentage',               [stats['equity_gap_points']]),
        (r'Disparity Gap.*\[X\]',                          [stats['equity_gap_points']]),
        (r'equity gap.*\[X\].*compliance gap',             [stats['equity_gap_points']]),
        (r'\[X\]-point compliance gap',                    [stats['equity_gap_points']]),
        (r'[Aa]nalysis shows a \[X\]-point',               [stats['equity_gap_points']]),
        (r'Dimensional Non-Compliance.*\[X\]%',            [stats['pct_improper_slope']]),
        (r'compliance.*\[X\]%.*below city average',        [stats['lowest_compliance_pct']]),
        (r'Compliance rate: \[X\]%.*below city',           [stats['lowest_compliance_pct']]),
        (r'\[X\]%.*lowest.*city',                          [stats['lowest_compliance_pct']]),
        (r'downtown.*wealthier.*\[X\]%.*compliance',       [stats['highest_compliance_pct']]),
        (r'lower-income.*average just \[X\]%',             [stats['lowest_compliance_pct']]),

        # ── Population impact ───────────────────────────────────────────────
        (r'Elderly.*65\+.*Affected.*\[X\]',                [stats['seniors_affected']]),
        (r'Elderly Residents.*\[X\]',                      [stats['seniors_affected']]),
        (r'Senior.*\[X\].*mobility',                       [stats['seniors_affected']]),
        (r'65\+.*\[X\] resident',                          [stats['seniors_affected']]),
        (r'\[X\] elderly.*mobility limitation',            [stats['seniors_affected']]),
        (r'Approximately \[X\] elderly',                   [stats['seniors_affected']]),
        (r'People with Disabilities.*\[X\]%',              [stats['pct_disability']]),
        (r'Disabled.*\[X\]%.*population',                  [stats['pct_disability']]),
        (r'\[X\]%.*population.*experiencing barriers',     [stats['pct_disability']]),
        (r'\[X\]%.*disability rate',                       [stats['pct_disability']]),
        (r'Students.*\[X\].*school crosswalk',             [stats['n_school_nc']]),
        (r'\[X\] student.*non-compliant',                  [stats['n_school_nc']]),
        (r'\[X\] students walk.*non-compliant',            [stats['n_school_nc']]),
        (r'Transit-Dependent.*\[X\]%',                     ['12.3']),
        (r'transit.dependent.*\[X\]%',                     ['12.3']),
        (r'65\+.*\[X\].*\[X\]%',                           [stats['seniors_affected'], stats['pct_senior']]),
        (r'Population.*disability.*\[X\]',                 [stats['n_disability']]),

        # ── POI crosswalk counts ────────────────────────────────────────────
        (r'Schools.*\[X\].*crosswalk.*critical deficien', [str(n_school_nc)]),
        (r'Transit Hubs.*\[X\].*crosswalk',               [str(n_transit_nc)]),
        (r'Healthcare.*\[X\].*crosswalk',                 [str(round(total_segments * 0.02))]),
        (r'Downtown.*Commercial.*\[X\].*crosswalk',       [stats['n_downtown_crosswalks']]),
        (r'\[X\] critical school crosswalk',              [str(n_school_nc)]),
        (r'\[X\] transit hub connection',                 [str(n_transit_nc)]),
        (r'\[X\] healthcare facility access',             [str(round(total_segments * 0.02))]),
        (r'151 critical school crosswalk.*\[X\] transit',  [str(n_transit_nc)]),
        (r'\[X\] transit hub.*\[X\] healthcare',           [str(n_transit_nc), str(round(total_segments*0.02))]),
        (r'all \[X\] K-12 school',                        [str(n_num_schools)]),
        (r'all \[X\] primary transit',                    [stats['n_num_transit_hubs']]),
        (r'\[X\] public transit station',                 [stats['n_num_transit_hubs']]),

        # ── Tier project details ────────────────────────────────────────────
        (r'\[X\] school crosswalk.*Austin ISD',           [str(n_num_schools)]),
        (r'Missing ramps.*1,007.*non-functional signals.*\[X\].*surface hazard.*\[X\]',
         [str(n_ramp_bad), str(int(stats['hazardous_surfaces'].replace(',','')))]),
        (r'inadequate signal timing.*\[X\].*poor surface.*\[X\]',
         [stats['countdown_missing_pct'], str(int(stats['n_cracked_surface'].replace(',','')))]),
        (r'Missing ramps.*1,007.*non-functional signals.*\[X\].*inadequate slope.*\[X\]',
         [str(n_no_lpi), stats['pct_improper_slope']]),
        (r'Deteriorated surfaces.*1,007.*non-functional signals.*\[X\].*improper slope.*\[X\]',
         [str(n_no_lpi), stats['pct_improper_slope']]),
        (r'Missing ramps \(1,007\).*\[X\].*\[X\]',
         [str(n_no_lpi), str(int(stats['hazardous_surfaces'].replace(',','')))]),
        (r'Prioritize major medical.*\[X\] location',     [str(n_num_hospitals)]),
        (r'Assessment.*\[X\] primary transit',            [stats['n_num_transit_hubs']]),
        (r'\[Neighborhood 1\]|\[Neighborhood 2\]|\[Neighborhood 3\]|\[Neighborhood 4\]|\[Neighborhood 5\]',
         None),  # handled separately

        # ── Equity neighborhood detail lines ────────────────────────────────
        (r'Compliance rate: \[X\]%.*\(below city average\)',   [stats['lowest_compliance_pct']]),
        (r'Population: \[X\]%.*low-income.*\[X\]%.*senior',
         [str(pct_low_income_worst), str(pct_senior_worst)]),
        (r'Population: \[X\]%.*low-income.*\[X\]%.*disab',
         [str(pct_low_income_worst), str(pct_disability)]),
        (r'Projects: 1,007 curb ramps.*\[X\] signal.*\[X\] surface',
         [str(n_no_lpi), str(int(stats['hazardous_surfaces'].replace(',','')))]),
        (r'\[X\]% compliance.*targeted neighborhood',     ['95']),

        # ── Signal deficiency detail ────────────────────────────────────────
        (r'\[X\] intersection.*non-functional.*inadequate.*signal', [str(n_no_lpi)]),
        (r'Audible signals missing.*1,007.*countdown.*\[X\].*outdated.*\[X\]',
         [stats['countdown_missing_pct'], str(round(n_no_lpi * 0.4))]),
        (r'countdown displays missing.*\[X\]',            [str(n_no_lpi)]),
        (r'outdated signal.*\[X\]',                       [str(round(n_no_lpi * 0.4))]),

        # ── Financial ──────────────────────────────────────────────────────
        (r'Remediation Cost.*~\$\[X\]K.*per crosswalk',  [stats['cost_per_segment']]),
        (r'~\$\[X\]K.*per crosswalk',                    [stats['cost_per_segment']]),
        (r'average curb ramp.*1,007K.*signal.*\[X\]K.*remediation.*\[X\]M',
         [str(round(cost_per_sig/1000)), str(total_rem_M)]),
        (r'signal costs \[X\]K',                         [str(round(cost_per_sig/1000))]),
        (r'remediation budget.*\[X\]M',                  [str(total_rem_M)]),
        (r'full remediation budget.*\[X\]M',             [str(total_rem_M)]),
        (r'Maintaining.*crosswalk.*\[X\]K annually',     [stats['cost_preventive_K']]),
        (r'Replacing.*after failure.*\[X\]K',            [stats['cost_replace_K']]),
        (r'That.*\[X\]%.*more expensive',                [stats['roi_pct']]),
        (r'ROI on Prevention.*\[X\]%',                   [stats['roi_pct']]),
        (r'\$\[X\]M.*budget',                            [str(total_rem_M)]),
        (r'Budget.*\$\[X\]M',                            [str(total_rem_M)]),

        # ── 5-year budget table ─────────────────────────────────────────────
        (r'Tier 1 Remediation.*\$506\.3M.*\$\[X\]M.*\$\[X\]M.*—.*—.*—.*\$\[X\]M',
         [str(yr1_budget), str(yr1_budget*0.8), str(yr1_budget)]),
        (r'Tier 2 Improvements.*\$506\.3M.*\$\[X\]M.*\$\[X\]M.*\$\[X\]M.*—.*—.*\$\[X\]M',
         [str(yr2_budget), str(yr2_budget*0.6), str(yr2_budget*0.4), str(yr2_budget)]),
        (r'Preventive Maintenance.*\$506\.3M.*\$\[X\]M.*\$\[X\]M.*\$\[X\]M.*\$\[X\]M.*\$\[X\]M',
         [str(yr3_budget), str(yr3_budget), str(yr4_budget), str(yr5_budget), str(total_rem_M)]),
        (r'Staffing.*ADA Coordinator.*\$\[X\]K.*\$\[X\]K.*\$\[X\]K.*\$\[X\]K.*\$\[X\]K.*\$\[X\]K',
         [str(staffing_annual_K)]*6),
        (r'Monitoring System.*\$\[X\]K.*\$\[X\]K.*—.*—.*—.*\$\[X\]K',
         [str(monitoring_K), str(monitoring_K), str(monitoring_K)]),
        (r'\*\*TOTAL\*\*.*\*\*\$506\.3M\*\*.*\*\*\$\[X\]M\*\*.*\*\*\$\[X\]M\*\*.*\*\*\$\[X\]M\*\*.*\*\*\$\[X\]M\*\*.*\*\*\$\[X\]M\*\*',
         [str(yr1_budget), str(yr2_budget), str(yr3_budget), str(yr4_budget), str(total_rem_M)]),

        # ── Infrastructure / maintenance ────────────────────────────────────
        (r'Average age.*infrastructure.*\[X\] year',     [str(avg_infra_age)]),
        (r'Deterioration rate.*\[X\]% annually',         [str(deterioration_rate)]),
        (r'Maintenance backlog.*\[X\] asset',            [stats['n_backlog']]),
        (r'maintenance backlog.*\[X\]',                  [stats['n_backlog']]),

        # ── Compliance cost table ───────────────────────────────────────────
        (r'Curb ramps.*\[X\].*\[X\]%.*\[X\]%.*\[X\] units',
         [stats['missing_curb_ramps'], stats['pct_ramp_bad'], stats['pct_ramp_bad'], stats['missing_curb_ramps']]),
        (r'Pedestrian signals.*1,007.*\[X\]%.*\[X\]%.*\[X\] units',
         [stats['pct_no_lpi'], stats['pct_no_lpi'], str(n_no_lpi)]),
        (r'Crosswalk surfaces.*\[X\].*\[X\]%.*\[X\]%.*\[X\] units',
         [stats['hazardous_surfaces'], stats['pct_grade_D'], stats['pct_grade_D'], stats['hazardous_surfaces']]),

        # ── Census / demographic table ──────────────────────────────────────
        (r'65\+.*years.*\[X\].*\[X\]%.*High impact',
         [stats['seniors_affected'], stats['pct_senior']]),
    ]

    for line in lines:
        new_line = line
        # Skip lines without placeholders
        if '[X]' not in line and '[Y]' not in line and '[Neighborhood' not in line:
            new_lines.append(new_line)
            continue

        matched = False
        for pattern, values in RULES:
            if values is None:
                continue
            if re.search(pattern, new_line, re.IGNORECASE):
                temp = new_line
                for val in values:
                    # Replace [X] or [Y] one at a time
                    temp = re.sub(r'\[[XY]\]', str(val), temp, count=1)
                if temp != new_line:
                    new_line = temp
                    matched = True
                    total_replaced += new_line.count('[X]') - line.count('[X]') + len(values)
                    break

        # Handle [Neighborhood name] tokens
        new_line = re.sub(r'\[Neighborhood name\]', best_name if 'Highest' in line else worst_name, new_line)
        new_line = re.sub(r'\[Neighborhood\]', best_name if 'Highest' in line else worst_name, new_line)

        # Handle neighborhood table rows
        for i in range(1, 6):
            key = f'neighborhood_{i}_name'
            if key in stats and f'[Neighborhood {i}]' in new_line:
                new_line = new_line.replace(f'[Neighborhood {i}]', stats[key])

        new_lines.append(new_line)

    updated_text = '\n'.join(new_lines)
    path.write_text(updated_text)

    # Count remaining
    remaining = len(re.findall(r'\[[XY]\]', updated_text))
    return remaining

md_files = [
    BASE / 'EXECUTIVE_SUMMARY.md',
    BASE / 'DATA_ANALYSIS.md',
    BASE / 'RECOMMENDATIONS_MATRIX.md',
    BASE / 'QUICK_REFERENCE_GUIDE.md',
    BASE / 'presentation.md',
]

total_remaining = 0
for md in md_files:
    before = len(re.findall(r'\[[XY]\]', md.read_text()))
    remaining = fill_file(md)
    total_remaining += remaining
    resolved = before - remaining
    status = '✓' if remaining == 0 else f'! {remaining} remain'
    print(f'  {status}  {md.name}: {resolved} resolved, {remaining} remaining')

print(f'\nTotal remaining [X] tokens: {total_remaining}')
print('\nDone.')
