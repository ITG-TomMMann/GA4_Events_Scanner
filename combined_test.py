import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# 1. Set Up Output Directory
# ---------------------------
output_dir = "combined_chart_jpegs"
os.makedirs(output_dir, exist_ok=True)

# ---------------------------
# 2. Define Extrapolated Data
# ---------------------------
# Note: February values have been extrapolated using a factor of ~1.65

# Range Rover Nameplate Data
data_nameplate = {
    'Month': ['2024-10', '2024-11', '2024-12', '2025-01', '2025-02'],
    'Organic_total_visitors': [100749, 88729, 64368, 68301, 58893],   # 35773*1.65 ≈ 58893
    'PdV_total_visitors':     [158194, 159096, 127374, 105283, 88899],   # 53901*1.65 ≈ 88899
    'Psearch_total_visitors': [163734, 198815, 130741, 112829, 109488],  # 66247*1.65 ≈ 109488
    'Psocial_total_visitors': [255647, 242212, 123149, 248908, 199195],  # 121330*1.65 ≈ 199195
    'Pmax_total_visitors':    [76831, 98267, 13442, 19426, 22400]      # 13612*1.65 ≈ 22400
}

# Velocity Blue Data
data_velocity = {
    'Month': ['2024-10', '2024-11', '2024-12', '2025-01', '2025-02'],
    'Organic_total_visitors': [0, 320, 497, 1688, 1385],            # 840*1.65 ≈ 1385
    'PdV_total_visitors':     [0, 679, 606, 155232, 345225],         # 209852*1.65 ≈ 345225
    'Psearch_total_visitors': [0, 4873, 9060, 75356, 49900],          # 30207*1.65 ≈ 49900
    'Psocial_total_visitors': [0, 214, 1143, 100264, 162386],         # 98440*1.65 ≈ 162386
    'Pmax_total_visitors':    [0, 8352, 5872, 29561, 32520]           # 19755*1.65 ≈ 32520
}

# ---------------------------
# 3. Create DataFrames & Compute Totals
# ---------------------------
# Convert Month to datetime
df_nameplate = pd.DataFrame(data_nameplate)
df_nameplate['Month'] = pd.to_datetime(df_nameplate['Month'], format='%Y-%m', errors='coerce')

df_velocity = pd.DataFrame(data_velocity)
df_velocity['Month'] = pd.to_datetime(df_velocity['Month'], format='%Y-%m', errors='coerce')

# Calculate Total Visitors for each page type (Organic + Paid)
df_nameplate['Total_nameplate'] = (df_nameplate['Organic_total_visitors'] +
                                   df_nameplate['PdV_total_visitors'] +
                                   df_nameplate['Psearch_total_visitors'] +
                                   df_nameplate['Psocial_total_visitors'] +
                                   df_nameplate['Pmax_total_visitors'])

df_velocity['Total_velocity'] = (df_velocity['Organic_total_visitors'] +
                                 df_velocity['PdV_total_visitors'] +
                                 df_velocity['Psearch_total_visitors'] +
                                 df_velocity['Psocial_total_visitors'] +
                                 df_velocity['Pmax_total_visitors'])

# Merge the two DataFrames on Month
df_combined = pd.merge(df_nameplate[['Month', 'Total_nameplate']],
                       df_velocity[['Month', 'Total_velocity']],
                       on='Month', how='outer')
# Calculate Combined Total = Nameplate + Velocity Blue
df_combined['Combined_Total'] = df_combined['Total_nameplate'] + df_combined['Total_velocity']
df_combined.sort_values('Month', inplace=True)

# ---------------------------
# 4. Plot Combined Visitors Chart
# ---------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df_combined['Month'], df_combined['Combined_Total'], marker='o', label='Combined VB + Nameplate')

# Add data labels to each point
for x, y in zip(df_combined['Month'], df_combined['Combined_Total']):
    ax.text(x, y, f"{y:.0f}", fontsize=8, ha='center', va='bottom')

ax.set_xlabel('Month')
ax.set_ylabel('Combined Total Visitors (Extrapolated Feb)')
ax.set_title('Combined Visitors: VB + Nameplate')
ax.legend()
fig.tight_layout()

# ---------------------------
# 5. Save the Chart as JPEG
# ---------------------------
output_filename = os.path.join(output_dir, "Combined_VB_Nameplate_Total_Visitors.jpeg")
fig.savefig(output_filename, format='jpeg', dpi=300)
plt.close(fig)

print(f"Combined visitors chart saved as {output_filename}")
