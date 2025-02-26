def read_markdown(filepath: str) -> str:
    """
    Reads a markdown file and returns its contents as a string.
    
    Parameters:
        filepath (str): The path to the markdown file.
        
    Returns:
        str: The content of the file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
