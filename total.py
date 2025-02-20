import pandas as pd

# -----------------------------------------------------------
# 1. RAW DATA (WITH EXTRAPOLATED FEB VISITORS) FOR config_l461
# -----------------------------------------------------------
# Example structure for config_l461. You can replicate for nameplate & velocity_blue.

data_config = {
    "Organic Search": {
        "visitors": {
            "2024-10": 1022,
            "2024-11": 914,
            "2024-12": 1167,
            "2025-01": 1640,
            "2025-02": 1529  # Extrapolated from 927 * 1.65
        },
        "rates": {
            "enquiry": {
                "2024-10": 2.20,
                "2024-11": 2.84,
                "2024-12": 11.94,
                "2025-01": 11.04,
                "2025-02": 1.79
            },
            "uev": {
                "2024-10": 2.83,
                "2024-11": 7.96,
                "2024-12": 12.00,
                "2025-01": 11.22,
                "2025-02": 1.94
            },
            "start": {
                "2024-10": 30.84,
                "2024-11": 31.37,
                "2024-12": 47.47,
                "2025-01": 46.29,
                "2025-02": 23.30
            },
            "comp": {
                "2024-10": 26.15,
                "2024-11": 25.90,
                "2024-12": 43.53,
                "2025-01": 42.08,
                "2025-02": 15.21
            }
        }
    },
    "Paid Display & Video": {
        "visitors": {
            "2024-10": 18,
            "2024-11": 32,
            "2024-12": 40,
            "2025-01": 79,
            "2025-02": 21  # 13 * 1.65
        },
        "rates": {
            "enquiry": {
                "2024-10": 5.88,
                "2024-11": 0.00,
                "2024-12": 0.00,
                "2025-01": 1.28,
                "2025-02": 0.00
            },
            "uev": {
                "2024-10": 5.88,
                "2024-11": 0.00,
                "2024-12": 0.00,
                "2025-01": 1.28,
                "2025-02": 0.00
            },
            "start": {
                "2024-10": 52.94,
                "2024-11": 22.42,
                "2024-12": 20.19,
                "2025-01": 31.19,
                "2025-02": 11.11
            },
            "comp": {
                "2024-10": 17.65,
                "2024-11": 7.88,
                "2024-12": 8.65,
                "2025-01": 20.17,
                "2025-02": 0.00
            }
        }
    },
    "Paid Search": {
        "visitors": {
            "2024-10": 936,
            "2024-11": 983,
            "2024-12": 903,
            "2025-01": 1182,
            "2025-02": 1138  # 689 * 1.65
        },
        "rates": {
            "enquiry": {
                "2024-10": 4.67,
                "2024-11": 2.04,
                "2024-12": 2.45,
                "2025-01": 3.60,
                "2025-02": 6.29
            },
            "uev": {
                "2024-10": 4.88,
                "2024-11": 2.09,
                "2024-12": 2.57,
                "2025-01": 3.67,
                "2025-02": 6.29
            },
            "start": {
                "2024-10": 40.78,
                "2024-11": 38.53,
                "2024-12": 50.96,
                "2025-01": 47.61,
                "2025-02": 42.03
            },
            "comp": {
                "2024-10": 20.86,
                "2024-11": 21.66,
                "2024-12": 38.54,
                "2025-01": 35.42,
                "2025-02": 28.02
            }
        }
    },
    "Paid Social": {
        "visitors": {
            "2024-10": 93,
            "2024-11": 55,
            "2024-12": 61,
            "2025-01": 35,
            "2025-02": 28  # 17 * 1.65
        },
        "rates": {
            "enquiry": {
                "2024-10": 0.00,
                "2024-11": 11.11,
                "2024-12": 0.00,
                "2025-01": 0.66,
                "2025-02": 0.00
            },
            "uev": {
                "2024-10": 0.00,
                "2024-11": 11.11,
                "2024-12": 0.00,
                "2025-01": 0.75,
                "2025-02": 0.00
            },
            "start": {
                "2024-10": 56.18,
                "2024-11": 45.21,
                "2024-12": 30.66,
                "2025-01": 16.45,
                "2025-02": 43.75
            },
            "comp": {
                "2024-10": 19.85,
                "2024-11": 22.80,
                "2024-12": 25.39,
                "2025-01": 8.55,
                "2025-02": 33.33
            }
        }
    },
    "PMAX": {
        "visitors": {
            "2024-10": 204,
            "2024-11": 141,
            "2024-12": 79,
            "2025-01": 158,
            "2025-02": 157  # 95 * 1.65
        },
        "rates": {
            "enquiry": {
                "2024-10": 2.29,
                "2024-11": 3.01,
                "2024-12": 0.25,
                "2025-01": 2.46,
                "2025-02": 0.43
            },
            "uev": {
                "2024-10": 2.34,
                "2024-11": 3.09,
                "2024-12": 0.28,
                "2025-01": 2.49,
                "2025-02": 0.43
            },
            "start": {
                "2024-10": 32.61,
                "2024-11": 42.14,
                "2024-12": 42.90,
                "2025-01": 45.06,
                "2025-02": 32.15
            },
            "comp": {
                "2024-10": 14.80,
                "2024-11": 27.10,
                "2024-12": 27.37,
                "2025-01": 22.38,
                "2025-02": 22.41
            }
        }
    }
}

months = ["2024-10", "2024-11", "2024-12", "2025-01", "2025-02"]

def compute_channel_totals(channel_data):
    """
    Given a dict for a single channel (like data_config["Organic Search"]),
    returns a DataFrame with columns:
      Month, Visitors, Enquiries, UEV, Config Starts, Config Completions
    by multiplying visitors by the respective rates for each month.
    """
    rows = []
    for m in months:
        v = channel_data["visitors"].get(m, 0)
        enq_rate = channel_data["rates"]["enquiry"].get(m, 0) / 100.0
        uev_rate = channel_data["rates"]["uev"].get(m, 0) / 100.0
        start_rate = channel_data["rates"]["start"].get(m, 0) / 100.0
        comp_rate = channel_data["rates"]["comp"].get(m, 0) / 100.0

        enq = v * enq_rate
        uev = v * uev_rate
        starts = v * start_rate
        comps = v * comp_rate

        rows.append({
            "Month": m,
            "Visitors": v,
            "Enquiries": enq,
            "UEV": uev,
            "Config Starts": starts,
            "Config Completions": comps
        })

    return pd.DataFrame(rows)

def sum_channels_as_paid(df_list):
    """
    Sums multiple paid channel DataFrames row-by-row (on Month).
    Returns a single DataFrame for 'Paid'.
    """
    df_merged = df_list[0]
    for df_next in df_list[1:]:
        df_merged = pd.merge(df_merged, df_next, on="Month", suffixes=("", "_dup"), how="outer")
        for col in ["Visitors", "Enquiries", "UEV", "Config Starts", "Config Completions"]:
            df_merged[col] = df_merged[[col, f"{col}_dup"]].sum(axis=1)
            df_merged.drop(columns=[f"{col}_dup"], inplace=True)

    df_merged = df_merged[["Month","Visitors","Enquiries","UEV","Config Starts","Config Completions"]]
    df_merged.sort_values("Month", inplace=True)
    return df_merged

def build_page_type_table(data_dict):
    """
    Takes a dict (like data_config) and produces a final DataFrame
    with 2 rows per month: Organic and Paid.
    """
    # Identify channels
    organic_channels = []
    paid_channels = []
    for ch in data_dict.keys():
        if "Organic" in ch:
            organic_channels.append(ch)
        else:
            paid_channels.append(ch)

    # Sum organic channels
    organic_dfs = [compute_channel_totals(data_dict[ch]) for ch in organic_channels]
    if len(organic_dfs) == 0:
        df_organic = pd.DataFrame()
    else:
        df_organic = sum_channels_as_paid(organic_dfs)
        df_organic.insert(1, "Traffic Type", "Organic")

    # Sum paid channels
    paid_dfs = [compute_channel_totals(data_dict[ch]) for ch in paid_channels]
    if len(paid_dfs) == 0:
        df_paid = pd.DataFrame()
    else:
        df_paid = sum_channels_as_paid(paid_dfs)
        df_paid.insert(1, "Traffic Type", "Paid")

    # Combine
    final_df = pd.concat([df_organic, df_paid], ignore_index=True)
    final_df.sort_values(["Month","Traffic Type"], inplace=True)
    return final_df

# -----------------------------------------------------------
# 2. BUILD TABLE FOR config_l461
# -----------------------------------------------------------
df_config = build_page_type_table(data_config)

# Round numeric columns
for col in ["Visitors","Enquiries","UEV","Config Starts","Config Completions"]:
    df_config[col] = df_config[col].round(0).astype(int)

print("\n=== config_l461: Total Values (Paid vs. Organic) ===")
print(df_config)

# -----------------------------------------------------------
# 3. REPLICATE FOR nameplate, velocity_blue, etc.
# (Define data_nameplate, data_velocity in a similar structure,
#  then call build_page_type_table on them.)
