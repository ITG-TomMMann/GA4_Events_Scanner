## High-Level Objectives

- **Dynamic CSV Analysis**  
    Create an AI agent that accepts CSV input containing web analytics data and performs advanced statistical analysis, including comparing metrics across different time periods (e.g., period A vs. period B).
    
- **Natural Language Processing (NLP) Integration**  
    Incorporate NLP to interpret user queries dynamically. The system should detect if a query is ambiguous or requires additional details—like specific date ranges—and prompt the user for clarification.
    
- **Comprehensive Reporting**  
    Generate a detailed analytical email report that includes:
    
    - A plain-text narrative summarizing findings.
    - Structured tables with key metrics (CTR, impressions, clicks).
    - Visualizations (charts) to support the analysis.
- **Business-Specific Rules**  
    Apply domain-specific rules such as correct CTR calculation (aggregated clicks/impressions) and significance checks for performance comparisons.
    

---

## Mid-Level Objectives

### 1. **Main Application – `app/agents/nl2sql/main.py`**

- **Objective**  
    Serve as the entry point to the AI agent. Handle CSV ingestion, capture/refine user queries via NLP, and orchestrate the entire analysis workflow.
    
- **Functions & Features**
    
    1. **CSV Ingestion**
        - Load the CSV data into a pandas DataFrame with robust error handling (missing file, invalid format, etc.).
    2. **User Query Handling & NLP**
        - Integrate an NLP component that:
            - Interprets the user’s analytical request (e.g., “Evaluate the performance of component X across period A and period B”).
            - Detects if more information is needed (date ranges, transformations).
            - Dynamically prompts the user for follow-up details.
    3. **Workflow Orchestration**
        - Pass the refined query and data to the router.
        - Collect and assemble results (narrative, tables, charts) into an email‐style report.

### 2. **Router Module – `app/agents/nl2sql/router.py`**

- **Objective**  
    Analyze the refined user query and direct it to the correct service function(s) based on keywords or detected intents (e.g., “CTR”, “period comparison”).
    
- **Functions & Features**
    
    1. **Query Routing**
        - Implement `route_request(refined_query, df)` to:
            - Identify if the request is a general CTR analysis, a performance comparison across periods, or a summary.
            - Call the appropriate service function(s) in the `analysis_service` module.
    2. **Dynamic Routing**
        - For queries indicating performance across multiple periods, call a dedicated function like `analyze_performance(df, periodA, periodB)`.
        - Support composite queries by combining multiple analysis results if needed.
    3. **Return Structure**
        - Return a dictionary or similar object that includes textual summaries, tables, and chart file paths.

### 3. **Service Layer – `app/agents/nl2sql/services/analysis_service.py`**

- **Objective**  
    Encapsulate all business logic, data transformations, and computations. This layer performs the heavy lifting: cleaning, analyzing, and visualizing data.
    
- **Functions & Features**
    
    1. **Data Validation & Transformation**
        - Clean and validate the CSV data (check for missing values, convert data types).
        - Filter data by user-specified date ranges or segments (e.g., period A vs. period B).
    2. **Analytical Functions**
        - `analyze_ctr(df)`:
            - Aggregates impressions, clicks, and calculates CTR as `(total_clicks / total_impressions) * 100`.
            - Generates a chart (e.g., bar chart) comparing CTR across elements.
            - Returns a dict with `summary_text`, a `analysis_table`, and `chart` path.
        - `analyze_performance(df, periodA, periodB)`:
            - Filters data for the specified date ranges.
            - Compares metrics (CTR, clicks, impressions) across periods.
            - Generates comparative charts (bar or line).
            - Returns a dict with a narrative summary, a comparative table, and chart path.
    3. **Business Logic & Rules**
        - Ensure correct CTR computation (aggregate first, then compute CTR).
        - If relevant, apply significance checks or threshold-based logic.
    4. **Output Structure**
        - Each function should return a standardized format: