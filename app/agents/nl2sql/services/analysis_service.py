import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, Any, Tuple, List
import numpy as np
from pathlib import Path
import logging

# Set up the charts directory
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

def analyze_ctr(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze CTR (Click-Through Rate) from the data.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Dictionary containing summary text, tables, and chart paths
    """
    logging.info("Performing CTR analysis")
    
    # Identify impressions and clicks columns
    impressions_col = identify_column(df, ['impressions', 'impression', 'views', 'view'])
    clicks_col = identify_column(df, ['clicks', 'click', 'interactions', 'interaction'])
    
    if not impressions_col or not clicks_col:
        logging.warning("Could not identify impressions or clicks columns")
        return {
            "summary": "Could not identify impressions or clicks columns in the data.",
            "tables": {},
            "charts": {}
        }
    
    logging.info(f"Using columns: impressions={impressions_col}, clicks={clicks_col}")
    
    # Calculate total impressions and clicks
    total_impressions = df[impressions_col].sum()
    total_clicks = df[clicks_col].sum()
    
    # Calculate overall CTR
    overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
    
    # Create a summary table
    summary_df = pd.DataFrame({
        'Metric': ['Impressions', 'Clicks', 'CTR (%)'],
        'Value': [total_impressions, total_clicks, f"{overall_ctr:.2f}%"]
    })
    
    # Generate a bar chart for CTR
    chart_path = generate_ctr_chart(df, impressions_col, clicks_col)
    
    # Generate summary text
    summary_text = f"""
    CTR Analysis Summary:
    
    The overall Click-Through Rate (CTR) is {overall_ctr:.2f}%, based on {total_impressions} impressions and {total_clicks} clicks.
    """
    
    logging.info(f"CTR analysis complete: overall CTR={overall_ctr:.2f}%")
    
    return {
        "summary": summary_text,
        "tables": {"CTR Summary": summary_df},
        "charts": {"CTR Analysis": chart_path}
    }

def analyze_performance(df: pd.DataFrame, period_a: Tuple, period_b: Tuple) -> Dict[str, Any]:
    """
    Compare performance metrics between two periods.
    
    Args:
        df: DataFrame containing the CSV data
        period_a: Tuple defining the first period (start, end)
        period_b: Tuple defining the second period (start, end)
        
    Returns:
        Dictionary containing summary text, tables, and chart paths
    """
    logging.info(f"Comparing performance between periods: A={period_a}, B={period_b}")
    
    # Identify date column
    date_col = identify_date_column(df)
    
    # If no date column was found, use index-based filtering
    if not date_col:
        logging.info("No date column found, using index-based filtering")
        df_a = df.iloc[period_a[0]:period_a[1]+1]
        df_b = df.iloc[period_b[0]:period_b[1]+1]
        period_a_label = f"Period A (rows {period_a[0]}-{period_a[1]})"
        period_b_label = f"Period B (rows {period_b[0]}-{period_b[1]})"
    else:
        logging.info(f"Using date column: {date_col}")
        # Convert to datetime if not already
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Filter by date ranges
        df_a = df[(df[date_col] >= period_a[0]) & (df[date_col] <= period_a[1])]
        df_b = df[(df[date_col] >= period_b[0]) & (df[date_col] <= period_b[1])]
        period_a_label = f"Period A ({period_a[0]} to {period_a[1]})"
        period_b_label = f"Period B ({period_b[0]} to {period_b[1]})"
    
    # Identify metrics columns
    impressions_col = identify_column(df, ['impressions', 'impression', 'views', 'view'])
    clicks_col = identify_column(df, ['clicks', 'click', 'interactions', 'interaction'])
    
    if not impressions_col or not clicks_col:
        logging.warning("Could not identify impressions or clicks columns")
        return {
            "summary": "Could not identify impressions or clicks columns in the data.",
            "tables": {},
            "charts": {}
        }
    
    logging.info(f"Using columns: impressions={impressions_col}, clicks={clicks_col}")
    
    # Calculate metrics for each period
    metrics_a = calculate_metrics(df_a, impressions_col, clicks_col)
    metrics_b = calculate_metrics(df_b, impressions_col, clicks_col)
    
    # Calculate percent changes
    percent_changes = {
        'Impressions': calculate_percent_change(metrics_a['Impressions'], metrics_b['Impressions']),
        'Clicks': calculate_percent_change(metrics_a['Clicks'], metrics_b['Clicks']),
        'CTR': calculate_percent_change(metrics_a['CTR'], metrics_b['CTR'])
    }
    
    # Create comparison table
    comparison_df = pd.DataFrame({
        'Metric': ['Impressions', 'Clicks', 'CTR (%)'],
        period_a_label: [metrics_a['Impressions'], metrics_a['Clicks'], f"{metrics_a['CTR']:.2f}%"],
        period_b_label: [metrics_b['Impressions'], metrics_b['Clicks'], f"{metrics_b['CTR']:.2f}%"],
        'Change (%)': [f"{percent_changes['Impressions']:.2f}%", 
                      f"{percent_changes['Clicks']:.2f}%", 
                      f"{percent_changes['CTR']:.2f}%"]
    })
    
    # Generate comparison charts
    chart_paths = generate_comparison_charts(metrics_a, metrics_b, period_a_label, period_b_label)
    
    # Generate summary text
    summary_text = f"""
    Performance Comparison Summary:
    
    Comparing {period_a_label} to {period_b_label}:
    
    - Impressions: {'increased' if percent_changes['Impressions'] > 0 else 'decreased'} by {abs(percent_changes['Impressions']):.2f}%
    - Clicks: {'increased' if percent_changes['Clicks'] > 0 else 'decreased'} by {abs(percent_changes['Clicks']):.2f}%
    - CTR: {'increased' if percent_changes['CTR'] > 0 else 'decreased'} by {abs(percent_changes['CTR']):.2f}%
    
    """
    
    logging.info("Performance comparison complete")
    
    return {
        "summary": summary_text,
        "tables": {"Performance Comparison": comparison_df},
        "charts": chart_paths
    }

def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a general summary of the data.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Dictionary containing summary text, tables, and chart paths
    """
    logging.info("Generating general data summary")
    
    # Get basic statistics
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # Identify key columns
    date_col = identify_date_column(df)
    impressions_col = identify_column(df, ['impressions', 'impression', 'views', 'view'])
    clicks_col = identify_column(df, ['clicks', 'click', 'interactions', 'interaction'])
    
    summary_text = f"""
    Data Summary:
    
    The dataset contains {num_rows} rows and {num_cols} columns.
    """
    
    # If we found date column, add date range info
    if date_col:
        logging.info(f"Found date column: {date_col}")
        df[date_col] = pd.to_datetime(df[date_col])
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        date_range = (max_date - min_date).days
        
        summary_text += f"""
        Date Range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')} ({date_range} days)
        """
    
    # If we found impressions and clicks, add CTR info
    if impressions_col and clicks_col: 
        logging.info(f"Found metrics columns: impressions={impressions_col}, clicks={clicks_col}")
        total_impressions = df[impressions_col].sum()
        total_clicks = df[clicks_col].sum()
        overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
        
        summary_text += f"""
        Overall Performance:
        - Total Impressions: {total_impressions}
        - Total Clicks: {total_clicks}
        - Overall CTR: {overall_ctr:.2f}%
        """
    
    # Create a summary table of the data
    summary_df = df.describe().T
    
    # Generate overview charts
    chart_paths = {}
    
    if impressions_col and clicks_col:
        chart_paths["Overview"] = generate_overview_chart(df, impressions_col, clicks_col)
    
    logging.info("General summary generation complete")
    
    return {
        "summary": summary_text,
        "tables": {"Data Statistics": summary_df},
        "charts": chart_paths
    }

# Helper functions

def identify_column(df: pd.DataFrame, keywords: list) -> str:
    """
    Identify a column in the DataFrame based on keywords.
    
    Args:
        df: DataFrame to search
        keywords: List of keywords to look for in column names
        
    Returns:
        Column name if found, empty string otherwise
    """
    for keyword in keywords:
        matching_cols = [col for col in df.columns if keyword.lower() in col.lower()]
        if matching_cols:
            return matching_cols[0]
    return ""

def identify_date_column(df: pd.DataFrame) -> str:
    """
    Identify the date column in the DataFrame.
    
    Args:
        df: DataFrame to search
        
    Returns:
        Column name if found, empty string otherwise
    """
    # Look for columns with 'date' in the name
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    
    if date_cols:
        return date_cols[0]
    
    # Try to convert each column to datetime and see which ones succeed
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            return col
        except:
            continue
    
    return ""

def calculate_metrics(df: pd.DataFrame, impressions_col: str, clicks_col: str) -> Dict[str, float]:
    """
    Calculate key metrics from the data.
    
    Args:
        df: DataFrame containing the data
        impressions_col: Name of the impressions column
        clicks_col: Name of the clicks column
        
    Returns:
        Dictionary of calculated metrics
    """
    total_impressions = df[impressions_col].sum()
    total_clicks = df[clicks_col].sum()
    ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
    
    return {
        'Impressions': total_impressions,
        'Clicks': total_clicks,
        'CTR': ctr
    }

def calculate_percent_change(value1: float, value2: float) -> float:
    """
    Calculate percent change from value1 to value2.
    
    Args:
        value1: Initial value
        value2: Final value
        
    Returns:
        Percent change
    """
    if value1 == 0:
        return float('inf') if value2 > 0 else 0
    
    return ((value2 - value1) / value1) * 100

def generate_ctr_chart(df: pd.DataFrame, impressions_col: str, clicks_col: str) -> str:
    """
    Generate a CTR chart.
    
    Args:
        df: DataFrame containing the data
        impressions_col: Name of the impressions column
        clicks_col: Name of the clicks column
        
    Returns:
        Path to the saved chart
    """
    logging.info("Generating CTR chart")
    
    # Create a new figure
    plt.figure(figsize=(10, 6))
    
    # Calculate CTR for each row
    df['CTR'] = (df[clicks_col] / df[impressions_col]) * 100
    
    # If there's a category column, use it for grouping
    category_col = identify_column(df, ['category', 'segment', 'group', 'type'])
    
    if category_col:
        logging.info(f"Using category column for grouping: {category_col}")
        # Group by category and calculate average CTR
        ctr_by_category = df.groupby(category_col)['CTR'].mean().sort_values(ascending=False)
        
        # Create bar chart
        ax = ctr_by_category.plot(kind='bar', color='skyblue')
        plt.title('Average CTR by Category')
        plt.ylabel('CTR (%)')
        plt.xlabel('Category')
        plt.xticks(rotation=45)
        
        # Add data labels
        for i, v in enumerate(ctr_by_category):
            ax.text(i, v + 0.5, f"{v:.2f}%", ha='center')
    else:
        logging.info("No category column found, creating CTR distribution histogram")
        # Create a histogram of CTR values
        plt.hist(df['CTR'], bins=20, color='skyblue', edgecolor='black')
        plt.title('Distribution of CTR Values')
        plt.xlabel('CTR (%)')
        plt.ylabel('Frequency')
    
    # Save the chart
    chart_path = os.path.join(CHARTS_DIR, 'ctr_analysis.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    
    logging.info(f"CTR chart saved to {chart_path}")
    
    return chart_path

def generate_comparison_charts(metrics_a: Dict[str, float], metrics_b: Dict[str, float], 
                              period_a_label: str, period_b_label: str) -> Dict[str, str]:
    """
    Generate charts comparing metrics between two periods.
    
    Args:
        metrics_a: Dictionary of metrics for period A
        metrics_b: Dictionary of metrics for period B
        period_a_label: Label for period A
        period_b_label: Label for period B
        
    Returns:
        Dictionary mapping chart names to file paths
    """
    logging.info("Generating comparison charts")
    
    chart_paths = {}
    
    # Create comparison bar chart
    plt.figure(figsize=(12, 8))
    
    # Set up the metrics to plot
    metrics = ['Impressions', 'Clicks', 'CTR']
    x = np.arange(len(metrics))
    width = 0.35
    
    # Create the bars
    plt.bar(x - width/2, [metrics_a['Impressions'], metrics_a['Clicks'], metrics_a['CTR']], 
            width, label=period_a_label, color='skyblue')
    plt.bar(x + width/2, [metrics_b['Impressions'], metrics_b['Clicks'], metrics_b['CTR']], 
            width, label=period_b_label, color='lightcoral')
    
    # Add labels and title
    plt.xlabel('Metrics')
    plt.ylabel('Values')
    plt.title('Comparison of Key Metrics Between Periods')
    plt.xticks(x, metrics)
    plt.legend()
    
    # Add data labels
    for i, v in enumerate([metrics_a['Impressions'], metrics_a['Clicks'], metrics_a['CTR']]):
        plt.text(i - width/2, v + 0.5, f"{v:.1f}", ha='center')
    
    for i, v in enumerate([metrics_b['Impressions'], metrics_b['Clicks'], metrics_b['CTR']]):
        plt.text(i + width/2, v + 0.5, f"{v:.1f}", ha='center')
    
    # Save the chart
    comparison_path = os.path.join(CHARTS_DIR, 'period_comparison.png')
    plt.tight_layout()
    plt.savefig(comparison_path)
    plt.close()
    
    chart_paths["Period Comparison"] = comparison_path
    
    # Create percent change chart
    plt.figure(figsize=(10, 6))
    
    # Calculate percent changes
    percent_changes = {
        'Impressions': calculate_percent_change(metrics_a['Impressions'], metrics_b['Impressions']),
        'Clicks': calculate_percent_change(metrics_a['Clicks'], metrics_b['Clicks']),
        'CTR': calculate_percent_change(metrics_a['CTR'], metrics_b['CTR'])
    }
    
    # Create the bars with color based on positive/negative change
    colors = ['green' if v > 0 else 'red' for v in percent_changes.values()]
    plt.bar(percent_changes.keys(), percent_changes.values(), color=colors)
    
    # Add labels and title
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.ylabel('Percent Change (%)')
    plt.title(f'Percent Change from {period_a_label} to {period_b_label}')
    
    # Add data labels
    for i, (k, v) in enumerate(percent_changes.items()):
        plt.text(i, v + (5 if v >= 0 else -5), f"{v:.1f}%", ha='center', 
                va='bottom' if v >= 0 else 'top')
    
    # Save the chart
    pct_change_path = os.path.join(CHARTS_DIR, 'percent_change.png')
    plt.tight_layout()
    plt.savefig(pct_change_path)
    plt.close()
    
    chart_paths["Percent Change"] = pct_change_path
    
    logging.info(f"Comparison charts saved to {CHARTS_DIR}")
    
    return chart_paths

def generate_overview_chart(df: pd.DataFrame, impressions_col: str, clicks_col: str) -> str:
    """
    Generate an overview chart of the data.
    
    Args:
        df: DataFrame containing the data
        impressions_col: Name of the impressions column
        clicks_col: Name of the clicks column
        
    Returns:
        Path to the saved chart
    """
    logging.info("Generating overview chart")
    
    # Create a new figure
    plt.figure(figsize=(12, 8))
    
    # If there's a date column, create a time series
    date_col = identify_date_column(df)
    
    if date_col:
        logging.info(f"Using date column for time series: {date_col}")
        # Convert to datetime if not already
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Group by date
        df_grouped = df.groupby(df[date_col].dt.date).agg({
            impressions_col: 'sum',
            clicks_col: 'sum'
        }).reset_index()
        
        # Calculate CTR
        df_grouped['CTR'] = (df_grouped[clicks_col] / df_grouped[impressions_col]) * 100
        
        # Create time series plot
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Plot impressions and clicks on left y-axis
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Count', color='tab:blue')
        ax1.plot(df_grouped[date_col], df_grouped[impressions_col], 'b-', label='Impressions')
        ax1.plot(df_grouped[date_col], df_grouped[clicks_col], 'g-', label='Clicks')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        # Create second y-axis for CTR
        ax2 = ax1.twinx()
        ax2.set_ylabel('CTR (%)', color='tab:red')
        ax2.plot(df_grouped[date_col], df_grouped['CTR'], 'r-', label='CTR')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.title('Impressions, Clicks, and CTR Over Time')
    else:
        logging.info("No date column found, creating simple bar chart")
        # Create a simple bar chart of total impressions and clicks
        plt.bar(['Impressions', 'Clicks'], [df[impressions_col].sum(), df[clicks_col].sum()], 
                color=['skyblue', 'lightgreen'])
        plt.title('Total Impressions and Clicks')
        plt.ylabel('Count')
        
        # Add data labels
        for i, v in enumerate([df[impressions_col].sum(), df[clicks_col].sum()]):
            plt.text(i, v + 0.5, f"{v:.0f}", ha='center')
    
    # Save the chart
    overview_path = os.path.join(CHARTS_DIR, 'data_overview.png')
    plt.tight_layout()
    plt.savefig(overview_path)
    plt.close()
    
    logging.info(f"Overview chart saved to {overview_path}")
    
    return overview_path
