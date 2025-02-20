import os
import pandas as pd
import matplotlib.pyplot as plt

# Create an output directory for JPEGs
output_dir = "charts_jpegs"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------
# 1. DEFINE THE EXTRAPOLATED DATA (FEB)
# -------------------------------------------
# Factor ~1.65 to go from 17 days to 28 days.
# Only the 2025-02 "total_visitors" values are extrapolated; rates remain unchanged.

# ---- config_l461 ----
data_config = {
    'Month': ['2024-10', '2024-11', '2024-12', '2025-01', '2025-02'],
    'Organic_total_visitors': [1022, 914, 1167, 1640, 1528],   # 927*1.65 ≈ 1528
    'PdV_total_visitors':     [18,   32,   40,   79,   21],    # 13*1.65 ≈ 21
    'Psearch_total_visitors': [936,  983,  903,  1182, 1135],   # 689*1.65 ≈ 1135
    'Psocial_total_visitors': [93,   55,   61,   35,   28],    # 17*1.65 ≈ 28
    'Pmax_total_visitors':    [204,  141,  79,   158,  156],   # 95*1.65 ≈ 156
    'Organic_engagement': [72.50, 82.64, 91.77, 92.89, 93.46],
    'PdV_engagement':     [85.29, 82.78, 89.10, 93.10, 85.19],
    'Psearch_engagement': [88.54, 86.14, 90.56, 92.87, 90.07],
    'Psocial_engagement': [96.63, 86.73, 93.82, 88.38, 95.83],
    'Pmax_engagement':    [82.34, 77.45, 84.60, 90.17, 80.84],
    'Organic_enquiry': [2.20, 2.84, 11.94, 11.04, 1.79],
    'PdV_enquiry':     [5.88, 0.00, 0.00,   1.28, 0.00],
    'Psearch_enquiry': [4.67, 2.04, 2.45,   3.60, 6.29],
    'Psocial_enquiry': [0.00, 11.11,0.00,   0.66, 0.00],
    'Pmax_enquiry':    [2.29, 3.01, 0.25,   2.46, 0.43],
    'Organic_start': [30.84, 31.37, 47.47, 46.29, 23.30],
    'PdV_start':     [52.94, 22.42, 20.19, 31.19, 11.11],
    'Psearch_start': [40.78, 38.53, 50.96, 47.61, 42.03],
    'Psocial_start': [56.18, 45.21, 30.66, 16.45, 43.75],
    'Pmax_start':    [32.61, 42.14, 42.90, 45.06, 32.15],
    'Organic_comp': [26.15, 25.90, 43.53, 42.08, 15.21],
    'PdV_comp':     [17.65, 7.88,  8.65,  20.17, 0.00],
    'Psearch_comp': [20.86, 21.66, 38.54, 35.42, 28.02],
    'Psocial_comp': [19.85, 22.80, 25.39, 8.55,  33.33],
    'Pmax_comp':    [14.80, 27.10, 27.37, 22.38, 22.41],
    'Organic_uev': [2.83, 7.96, 12.00, 11.22, 1.94],
    'PdV_uev':     [5.88, 0.00, 0.00,   1.28, 0.00],
    'Psearch_uev': [4.88, 2.09, 2.57,   3.67, 6.29],
    'Psocial_uev': [0.00, 11.11,0.00,   0.75, 0.00],
    'Pmax_uev':    [2.34, 3.09, 0.28,   2.49, 0.43],
}

# ---- range_rover_nameplate ----
data_nameplate = {
    'Month': ['2024-10', '2024-11', '2024-12', '2025-01', '2025-02'],
    'Organic_total_visitors': [100749, 88729, 64368, 68301, 58893],  # 35773*1.65 ≈ 58893
    'PdV_total_visitors':     [158194,159096,127374,105283,88899],   # 53901*1.65 ≈ 88899
    'Psearch_total_visitors': [163734,198815,130741,112829,109488],  # 66247*1.65 ≈ 109488
    'Psocial_total_visitors': [255647,242212,123149,248908,199195],  # 121330*1.65 ≈ 199195
    'Pmax_total_visitors':    [76831, 98267, 13442, 19426, 22400],   # 13612*1.65 ≈ 22400
    'Organic_engagement': [60.41, 49.64, 53.72, 50.95, 52.14],
    'PdV_engagement':     [28.62, 24.40, 26.17, 27.52, 26.45],
    'Psearch_engagement': [54.18, 51.63, 54.39, 54.95, 54.32],
    'Psocial_engagement': [37.65, 32.86, 36.11, 26.73, 27.43],
    'Pmax_engagement':    [45.77, 40.83, 48.59, 50.04, 44.38],
    'Organic_enquiry': [2.19, 0.73, 0.55, 0.87, 0.74],
    'PdV_enquiry':     [0.49, 0.53, 0.49, 0.19, 0.44],
    'Psearch_enquiry': [2.09, 1.70, 1.93, 1.52, 1.64],
    'Psocial_enquiry': [0.25, 0.47, 0.39, 0.47, 0.27],
    'Pmax_enquiry':    [1.13, 0.78, 1.53, 1.12, 0.98],
    'Organic_start': [46.85, 40.99, 46.81, 43.59, 39.33],
    'PdV_start':     [27.08, 22.28, 21.55, 22.25, 21.62],
    'Psearch_start': [48.80, 46.99, 48.36, 48.70, 47.06],
    'Psocial_start': [37.87, 31.16, 32.53, 22.72, 22.56],
    'Pmax_start':    [56.40, 50.94, 53.82, 54.11, 46.07],
    'Organic_comp': [29.29, 26.49, 33.49, 30.19, 27.44],
    'PdV_comp':     [9.09, 10.48, 10.86, 12.26, 12.43],
    'Psearch_comp': [24.15,28.52, 31.61, 31.83, 30.63],
    'Psocial_comp': [12.60,13.32, 14.64, 10.91, 12.04],
    'Pmax_comp':    [20.02,20.47, 27.14, 28.13, 24.19],
    'Organic_uev': [2.61, 1.34, 0.95, 1.37, 1.41],
    'PdV_uev':     [0.94, 0.94, 0.77, 0.37, 0.64],
    'Psearch_uev': [2.79, 2.29, 2.50, 2.09, 2.05],
    'Psocial_uev': [0.58, 0.89, 0.89, 1.12, 0.63],
    'Pmax_uev':    [1.46, 1.29, 2.26, 1.70, 1.51],
}

# ---- velocity_blue ----
data_velocity = {
    'Month': ['2024-10', '2024-11', '2024-12', '2025-01', '2025-02'],
    'Organic_total_visitors': [0, 320, 497, 1688, 1385],  # 840*1.65 ≈ 1385
    'PdV_total_visitors':     [0, 679, 606, 155232, 345225],  # 209852*1.65 ≈ 345225
    'Psearch_total_visitors': [0, 4873, 9060, 75356, 49900],   # 30207*1.65 ≈ 49900
    'Psocial_total_visitors': [0, 214, 1143, 100264, 162386],   # 98440*1.65 ≈ 162386
    'Pmax_total_visitors':    [0, 8352, 5872, 29561, 32520],    # 19755*1.65 ≈ 32520
    'Organic_engagement': [None, 44.88, 37.04, 29.02, 30.07],
    'PdV_engagement':     [None, 21.29, 22.43, 14.27, 13.57],
    'Psearch_engagement': [None, 31.91, 41.09, 27.07, 22.04],
    'Psocial_engagement': [None, 17.79, 32.51, 12.95, 13.91],
    'Pmax_engagement':    [None, 25.87, 22.00, 28.87, 19.47],
    'Organic_enquiry': [None, 0.28, 8.59, 0.71, 0.02],
    'PdV_enquiry':     [None, 0.00, 0.01, 0.03, 0.01],
    'Psearch_enquiry': [None, 1.32, 0.46, 0.64, 0.48],
    'Psocial_enquiry': [None, 0.00, 0.00, 0.00, 0.01],
    'Pmax_enquiry':    [None, 0.27, 0.04, 0.88, 0.00],
    'Organic_start': [None, 45.07, 36.25, 28.40, 27.78],
    'PdV_start':     [None, 21.31, 25.10, 15.06, 10.59],
    'Psearch_start': [None, 34.17, 42.79, 28.01, 19.83],
    'Psocial_start': [None, 28.42, 35.94, 13.47, 12.07],
    'Pmax_start':    [None, 37.58, 32.68, 38.78, 23.27],
    'Organic_comp': [None, 25.73, 19.80, 14.22, 13.28],
    'PdV_comp':     [None, 4.65, 4.90, 5.58, 3.88],
    'Psearch_comp': [None, 15.28, 20.27, 13.27, 9.14],
    'Psocial_comp': [None, 3.65, 8.05, 5.41, 4.40],
    'Pmax_comp':    [None, 10.80, 7.48, 12.41, 8.13],
    'Organic_uev': [None, 0.52, 9.08, 3.79, 0.05],
    'PdV_uev':     [None, 0.00, 0.04, 0.40, 0.09],
    'Psearch_uev': [None, 1.47, 0.53, 1.22, 0.77],
    'Psocial_uev': [None, 0.00, 0.00, 0.16, 0.09],
    'Pmax_uev':    [None, 0.44, 0.09, 1.28, 0.00],
}

# -------------------------------------------
# 2. HELPER FUNCTIONS
# -------------------------------------------
def combine_paid_vs_organic(df, prefix=''):
    """
    Summarizes 'Paid' (PdV + Psearch + Psocial + Pmax) vs. 'Organic' for a given metric prefix.
    For total_visitors, we sum the numbers.
    For rates, we calculate a weighted average using each channel's total visitors.
    """
    org_col = f'Organic_{prefix}'
    pdv_col = f'PdV_{prefix}'
    psearch_col = f'Psearch_{prefix}'
    psocial_col = f'Psocial_{prefix}'
    pmax_col = f'Pmax_{prefix}'

    df[org_col] = df[org_col].fillna(0)
    df[pdv_col] = df[pdv_col].fillna(0)
    df[psearch_col] = df[psearch_col].fillna(0)
    df[psocial_col] = df[psocial_col].fillna(0)
    df[pmax_col] = df[pmax_col].fillna(0)

    if prefix == 'total_visitors':
        df['Paid_total_visitors'] = df[pdv_col] + df[psearch_col] + df[psocial_col] + df[pmax_col]
        out_cols = ['Month', 'Organic_total_visitors', 'Paid_total_visitors']
        return df[out_cols]
    else:
        pdv_vis = df['PdV_total_visitors'].fillna(0)
        ps_vis  = df['Psearch_total_visitors'].fillna(0)
        pso_vis = df['Psocial_total_visitors'].fillna(0)
        pmx_vis = df['Pmax_total_visitors'].fillna(0)
        total_paid_vis = pdv_vis + ps_vis + pso_vis + pmx_vis
        total_paid_vis = total_paid_vis.replace(0, 1)  # avoid division by zero

        paid_rate = (
            df[pdv_col] * pdv_vis +
            df[psearch_col] * ps_vis +
            df[psocial_col] * pso_vis +
            df[pmax_col] * pmx_vis
        ) / total_paid_vis

        df[f'Paid_{prefix}'] = paid_rate
        df[f'Organic_{prefix}'] = df[org_col]
        out_cols = ['Month', f'Organic_{prefix}', f'Paid_{prefix}']
        return df[out_cols]

def prep_page_type_data(raw_dict):
    """
    Converts a raw dictionary to a DataFrame, parses Month as datetime,
    and creates a dictionary of DataFrames (one per metric).
    """
    df = pd.DataFrame(raw_dict)
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m', errors='coerce')
    metrics = ['total_visitors', 'engagement', 'enquiry', 'start', 'comp', 'uev']
    dfs = {}
    for m in metrics:
        sub_df = combine_paid_vs_organic(df.copy(), prefix=m)
        dfs[m] = sub_df
    return dfs

def add_data_labels(ax, df, x_col, y_col):
    """
    Adds data labels (text) above each data point on the given axes.
    """
    for x, y in zip(df[x_col], df[y_col]):
        ax.text(x, y, f"{y:.1f}", fontsize=8, ha='center', va='bottom')

def plot_page_type_metric(page_type_dfs, metric_name, page_type_label, filename_suffix):
    """
    Plots a line chart for a given metric (Paid vs. Organic) for the specified page type.
    The chart is saved as a JPEG file with data labels.
    """
    df_metric = page_type_dfs[metric_name].copy().sort_values('Month')
    col_org = [c for c in df_metric.columns if 'Organic_' in c and c != 'Month'][0]
    col_paid = [c for c in df_metric.columns if 'Paid_' in c][0]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df_metric['Month'], df_metric[col_org], marker='o', label='Organic')
    ax.plot(df_metric['Month'], df_metric[col_paid], marker='o', label='Paid')
    add_data_labels(ax, df_metric, 'Month', col_org)
    add_data_labels(ax, df_metric, 'Month', col_paid)

    ax.set_xlabel('Month')
    ylabel_map = {
        'total_visitors': 'Total Visitors',
        'engagement': 'Engagement Rate (%)',
        'enquiry': 'Enquiry Rate (%)',
        'start': 'Config Start Rate (%)',
        'comp': 'Config Completion Rate (%)',
        'uev': 'UEV-ENQ'
    }
    ax.set_ylabel(ylabel_map.get(metric_name, metric_name))
    ax.set_title(f'{page_type_label} - {metric_name} (Paid vs. Organic)')
    ax.legend()
    fig.tight_layout()

    # Save the figure as a JPEG
    out_filename = os.path.join(output_dir, f"{page_type_label}_{metric_name}_{filename_suffix}.jpeg")
    fig.savefig(out_filename, format='jpeg', dpi=300)
    plt.close(fig)

# -------------------------------------------
# 3. PREPARE THE DATAFRAMES (with EXTRAPOLATED Feb)
# -------------------------------------------
config_dfs = prep_page_type_data(data_config)
nameplate_dfs = prep_page_type_data(data_nameplate)
velocity_dfs = prep_page_type_data(data_velocity)

# Create overall total visitors dataframes for each page type
df_config_total = config_dfs['total_visitors'].rename(columns={
    'Organic_total_visitors': 'Organic_config',
    'Paid_total_visitors': 'Paid_config'
})
df_config_total['Total_config'] = df_config_total['Organic_config'] + df_config_total['Paid_config']

df_nameplate_total = nameplate_dfs['total_visitors'].rename(columns={
    'Organic_total_visitors': 'Organic_nameplate',
    'Paid_total_visitors': 'Paid_nameplate'
})
df_nameplate_total['Total_nameplate'] = df_nameplate_total['Organic_nameplate'] + df_nameplate_total['Paid_nameplate']

df_velocity_total = velocity_dfs['total_visitors'].rename(columns={
    'Organic_total_visitors': 'Organic_velocity',
    'Paid_total_visitors': 'Paid_velocity'
})
df_velocity_total['Total_velocity'] = df_velocity_total['Organic_velocity'] + df_velocity_total['Paid_velocity']

# Merge overall totals on Month
df_all_totals = (
    df_config_total[['Month', 'Total_config']]
    .merge(df_nameplate_total[['Month', 'Total_nameplate']], on='Month', how='outer')
    .merge(df_velocity_total[['Month', 'Total_velocity']], on='Month', how='outer')
    .sort_values('Month')
)

# -------------------------------------------
# 4. PLOT CHART #1: ALL TOTAL VISITORS (3 LINES) WITH DATA LABELS, SAVE AS JPEG
# -------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df_all_totals['Month'], df_all_totals['Total_config'], marker='o', label='config_l461')
ax.plot(df_all_totals['Month'], df_all_totals['Total_nameplate'], marker='o', label='range_rover_nameplate')
ax.plot(df_all_totals['Month'], df_all_totals['Total_velocity'], marker='o', label='velocity_blue')

for col, lbl in zip(['Total_config', 'Total_nameplate', 'Total_velocity'],
                    ['config_l461', 'range_rover_nameplate', 'velocity_blue']):
    for x, y in zip(df_all_totals['Month'], df_all_totals[col]):
        ax.text(x, y, f"{y:.0f}", fontsize=8, ha='center', va='bottom')

ax.set_xlabel('Month')
ax.set_ylabel('Total Visitors (Extrapolated Feb)')
ax.set_title('Total Visitors Over Time (All Page Types) - Feb Extrapolated')
ax.legend()
fig.tight_layout()

out_filename_all = os.path.join(output_dir, "All_Total_Visitors.jpeg")
fig.savefig(out_filename_all, format='jpeg', dpi=300)
plt.close(fig)

# -------------------------------------------
# 5. CREATE CHARTS FOR EACH PAGE TYPE AND METRIC, SAVE AS JPEG
# -------------------------------------------
page_types = [
    ('config_l461', config_dfs),
    ('range_rover_nameplate', nameplate_dfs),
    ('velocity_blue', velocity_dfs)
]

metrics_order = ['total_visitors', 'enquiry', 'engagement', 'comp', 'start', 'uev']

for (label, dfs_dict) in page_types:
    for m in metrics_order:
        # Use filename suffix based on page type and metric
        plot_page_type_metric(dfs_dict, m, label, filename_suffix="chart")

print("All JPEG charts generated and saved in the 'charts_jpegs' directory!")
