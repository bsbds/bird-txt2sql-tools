from typing import Dict, Any


def build_prompt(state: Dict[str, Any]) -> str:
    """
    Build a comprehensive prompt from the state dictionary.
    """
    question = state.get("question", "")
    external_knowledge = state.get("external_knowledge", "")
    db_id = state.get("db_id", "")
    table_descriptions = state.get("table_descriptions", "")
    schema_info = state.get("schema_info", "")
    sql_dialect = state.get("sql_dialect", "SQLite")
    
    prompt_parts = [
        f"Database: {db_id}",
        f"SQL Dialect: {sql_dialect}",
        "",
        "Schema Information:",
        schema_info,
        "",
        "Table Descriptions:",
        table_descriptions,
    ]
    
    if external_knowledge:
        prompt_parts.extend([
            "",
            "External Knowledge:",
            external_knowledge,
        ])
    
    prompt_parts.extend([
        "",
        "Question:",
        question,
        "",
        "Generate a SQL query that answers the question:"
    ])
    
    return "\n".join(prompt_parts)