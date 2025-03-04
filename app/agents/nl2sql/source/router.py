import pandas as pd
from typing import Dict, Any, List, Tuple
import re
import logging

# Import the analysis service
from app.agents.nl2sql.services.analysis_service import (
    analyze_ctr,
    analyze_performance,
    generate_summary
)

def route_request(query: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the user query and route it to the appropriate analysis function.
    
    Args:
        query: The user's natural language query
        df: DataFrame containing the CSV data
        
    Returns:
        Dictionary containing the analysis results
    """
    logging.info(f"Routing query: {query}")
    
    # Convert query to lowercase for easier matching
    query_lower = query.lower()
    
    # Initialize results dictionary
    results = {
        "summary": "",
        "tables": {},
        "charts": {}
    }
    
    # Check for period comparison requests
    if re.search(r'compar(e|ing|ison)', query_lower) and re.search(r'period', query_lower):
        logging.info("Detected period comparison request")
        # Extract period information from the query
        period_a, period_b = extract_period_info(query_lower, df)
        
        # Perform period comparison analysis
        comparison_results = analyze_performance(df, period_a, period_b)
        
        # Update results with comparison analysis
        results["summary"] += comparison_results["summary"]
        results["tables"].update(comparison_results["tables"])
        results["charts"].update(comparison_results["charts"])
    
    # Check for CTR analysis requests
    if re.search(r'ctr|click.through.rate', query_lower):
        logging.info("Detected CTR analysis request")
        # Perform CTR analysis
        ctr_results = analyze_ctr(df)
        
        # Update results with CTR analysis
        results["summary"] += "\n\n" + ctr_results["summary"] if results["summary"] else ctr_results["summary"]
        results["tables"].update(ctr_results["tables"])
        results["charts"].update(ctr_results["charts"])
    
    # If no specific analysis was requested, generate a general summary
    if not results["summary"]:
        logging.info("No specific analysis detected, generating general summary")
        summary_results = generate_summary(df)
        
        # Update results with summary
        results["summary"] = summary_results["summary"]
        results["tables"].update(summary_results["tables"])
        results["charts"].update(summary_results["charts"])
    
    return results

def extract_period_info(query: str, df: pd.DataFrame) -> Tuple[Tuple, Tuple]:
    """
    Extract period information from the query.
    
    Args:
        query: The user's natural language query
        df: DataFrame containing the CSV data
        
    Returns:
        Tuple containing period A and period B information
    """
    logging.info("Extracting period information from query")
    
    # Try to find period A dates
    period_a_match = re.search(r'period a[:\s]+(\d{4}-\d{2}-\d{2})[\s\w]+(\d{4}-\d{2}-\d{2})', query, re.IGNORECASE)
    
    # Try to find period B dates
    period_b_match = re.search(r'period b[:\s]+(\d{4}-\d{2}-\d{2})[\s\w]+(\d{4}-\d{2}-\d{2})', query, re.IGNORECASE)
    
    # If dates weren't found, try to infer from the data
    if not period_a_match or not period_b_match:
        logging.info("Dates not explicitly found in query, inferring from data")
        # Assuming the DataFrame has a date column
        date_col = identify_date_column(df)
        
        if date_col:
            logging.info(f"Found date column: {date_col}")
            # Convert to datetime if not already
            df[date_col] = pd.to_datetime(df[date_col])
            
            # Sort dates
            sorted_dates = sorted(df[date_col].unique())
            
            # If we have enough dates, split into two periods
            if len(sorted_dates) >= 2:
                mid_point = len(sorted_dates) // 2
                period_a = (sorted_dates[0], sorted_dates[mid_point-1])
                period_b = (sorted_dates[mid_point], sorted_dates[-1])
                logging.info(f"Inferred periods: A={period_a}, B={period_b}")
                return period_a, period_b
    
    # If we found explicit dates in the query, use those
    if period_a_match and period_b_match:
        logging.info("Using explicit dates from query")
        period_a = (period_a_match.group(1), period_a_match.group(2))
        period_b = (period_b_match.group(1), period_b_match.group(2))
        return period_a, period_b
    
    # Default fallback - use the first and second half of the data
    # This assumes the data is already sorted by date
    logging.info("Using default period split (first half vs second half)")
    mid_point = len(df) // 2
    return (0, mid_point-1), (mid_point, len(df)-1)

def identify_date_column(df: pd.DataFrame) -> str:
    """
    Identify the date column in the DataFrame.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        Name of the date column, or empty string if not found
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
