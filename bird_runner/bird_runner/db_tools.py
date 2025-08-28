import json

from sqlalchemy import create_engine, inspect, Engine, Inspector
from sqlalchemy.exc import SQLAlchemyError


def run_load_db_info(
    db_path: str,
) -> dict:
    """
    Load database information from SQLite file using db_root_path.
    """
    try:
        # Extract schema and table info
        schema_ddl, table_descriptions = _extract_from_database(db_path, "SQLite")

        result = {"schema_info": schema_ddl, "table_descriptions": table_descriptions}

        return result

    except Exception as e:
        raise RuntimeError(f"Error loading database information: {str(e)}")


def _extract_from_database(db_path: str, dialect: str) -> tuple[str, str]:
    """
    Extract schema information directly from database connection.

    Args:
        database_name (str): Name of the database to query
        db_config (Dict[str, Any]): Database connection configuration

    Returns:
        Tuple[str, str]: A tuple containing (schema_ddl, table_descriptions_markdown)
    """

    try:
        # Create connection string based on dialect
        if dialect == "MySQL":
            conn_str = ""
        elif dialect == "PostgreSQL":
            conn_str = ""
        elif dialect == "SQLite":
            conn_str = f"sqlite:///{db_path}"
        else:
            raise ValueError(f"Unsupported database dialect: {dialect}")

        # Create engine and inspector
        engine = create_engine(conn_str)
        inspector = inspect(engine)

        # Get table names
        table_names = inspector.get_table_names()

        # Generate DDL statements
        schema_ddl = _extract_ddl_from_database(engine, inspector, table_names, dialect)

        # Generate table descriptions (basic metadata)
        table_descriptions = _generate_table_descriptions_from_db(
            inspector, table_names
        )

        return schema_ddl, table_descriptions

    except SQLAlchemyError as e:
        raise RuntimeError(f"Database connection error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error extracting database schema: {str(e)}")


def _extract_from_json(database_name: str, json_file_path: str) -> tuple[str, str]:
    """
    Extract schema information from JSON file.

    Args:
        database_name (str): Name of the database to query
        json_file_path (str): Path to the JSON file containing database descriptions

    Returns:
        Tuple[str, str]: A tuple containing (schema_ddl, table_descriptions_markdown)
    """
    try:
        # Read JSON file
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Check if database exists
        if database_name not in data:
            raise ValueError(f"Database '{database_name}' not found in the JSON file")

        # Get database information
        database_info = data[database_name]

        # Extract schema DDL from JSON descriptions
        schema_ddl = _generate_ddl_from_json(database_info)

        # Generate markdown table descriptions
        table_descriptions = _generate_table_descriptions_from_json(database_info)

        return schema_ddl, table_descriptions

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Database description file not found at '{json_file_path}'"
        )
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the database description file")


def _extract_ddl_from_database(
    engine: Engine, inspector: Inspector, table_names: list[str], dialect: str
) -> str:
    """
    Extract actual DDL statements from database.

    Args:
        engine: SQLAlchemy engine
        inspector: SQLAlchemy inspector
        table_names: List of table names
        dialect: Database dialect

    Returns:
        str: Generated DDL statements
    """
    ddl_statements = []

    for table_name in table_names:
        columns = inspector.get_columns(table_name)

        # Build CREATE TABLE statement
        column_defs = []
        for column in columns:
            col_def = f"  {column['name']} {column['type']}"
            if not column.get("nullable", True):
                col_def += " NOT NULL"
            if column.get("default") is not None:
                col_def += f" DEFAULT {column['default']}"
            column_defs.append(col_def)

        if column_defs:
            ddl = f"CREATE TABLE {table_name} (\n" + ",\n".join(column_defs) + "\n);"
            ddl_statements.append(ddl)

    return "\n\n".join(ddl_statements)


def _generate_ddl_from_json(database_info: dict) -> str:
    """
    Generate DDL statements from JSON database information.

    Args:
        database_info (Dict): Database information from JSON file

    Returns:
        str: Generated DDL statements
    """
    ddl_statements = []

    for table_name, table_info in database_info.items():
        columns_description = table_info.get("columns_description", {})

        # Create simplified CREATE TABLE statement
        columns = []
        for column_name, column_desc in columns_description.items():
            # Extract a mock datatype from the description
            if "integer" in column_desc.lower() or "id" in column_desc.lower():
                datatype = "INTEGER"
            elif "date" in column_desc.lower():
                datatype = "DATE"
            elif "real" in column_desc.lower() or "number" in column_desc.lower():
                datatype = "REAL"
            else:
                datatype = "TEXT"

            columns.append(f"  {column_name} {datatype}")

        if columns:
            ddl = f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n);"
            ddl_statements.append(ddl)

    return "\n\n".join(ddl_statements)


def _generate_table_descriptions_from_db(
    inspector: Inspector, table_names: list[str]
) -> str:
    """
    Generate markdown table descriptions from database inspection.

    Args:
        inspector: SQLAlchemy inspector
        table_names: List of table names

    Returns:
        str: Formatted markdown table
    """
    # Build Markdown table
    markdown_table = "| table | table_description | column | column_description |\n"
    markdown_table += "|------|----------|------|----------|\n"

    # Iterate through all tables
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        table_description = f"Table with {len(columns)} columns"

        # If no columns, show at least one row
        if not columns:
            markdown_table += f"| {table_name} | {table_description} |  |  |\n"
        else:
            # Process each column
            first_column = True
            for column in columns:
                column_name = column["name"]
                column_type = str(column["type"])
                column_description = f"Type: {column_type}"
                if not column.get("nullable", True):
                    column_description += ", NOT NULL"

                if first_column:
                    # First column shows table name and description
                    markdown_table += f"| {table_name} | {table_description} | {column_name} | {column_description} |\n"
                    first_column = False
                else:
                    # Subsequent columns don't show table name and description
                    markdown_table += (
                        f"|  |  | {column_name} | {column_description} |\n"
                    )

    return markdown_table


def _generate_table_descriptions_from_json(database_info: dict) -> str:
    """
    Generate markdown table descriptions from JSON database information.

    Args:
        database_info (Dict): Database information from JSON file

    Returns:
        str: Formatted markdown table
    """
    # Build Markdown table
    markdown_table = "| table | table_description | column | column_description |\n"
    markdown_table += "|------|----------|------|----------|\n"

    # Iterate through all tables
    for table_name, table_info in database_info.items():
        table_description = table_info.get("table_description", "No description")

        # Get column information
        columns_description = table_info.get("columns_description", {})

        # If no columns, show at least one row
        if not columns_description:
            markdown_table += f"| {table_name} | {table_description} |  |  |\n"
        else:
            # Process each column
            first_column = True
            for column_name, column_description in columns_description.items():
                if first_column:
                    # First column shows table name and description
                    markdown_table += f"| {table_name} | {table_description} | {column_name} | {column_description} |\n"
                    first_column = False
                else:
                    # Subsequent columns don't show table name and description
                    markdown_table += (
                        f"|  |  | {column_name} | {column_description} |\n"
                    )

    return markdown_table


def load_eval_data(
    eval_path: str,
    db_root_path: str,
    sql_dialect: str,
) -> dict:
    """
    Load evaluation data and extract question, database path, and knowledge information.
    Replicates the functionality of the reference code's eval_data loading and decouple_question_schema.

    Args:
        eval_path (str): Path to evaluation data file
        db_root_path (str): Root path for database files
        sql_dialect (str): SQL dialect

    Returns:
        str: JSON string containing the extracted data
    """
    try:
        # Use structured approach with direct parameters
        sql_dialect = sql_dialect or "SQLite"

        with open(eval_path, "r", encoding="utf-8") as file:
            eval_data = json.load(file)

        # Decouple question schema - equivalent to decouple_question_schema function
        question_list, db_path_list, knowledge_list = _decouple_question_schema(
            datasets=eval_data, db_root_path=db_root_path
        )

        # Validate lengths like in reference code
        assert len(question_list) == len(db_path_list), (
            f"Mismatch: {len(question_list)} questions vs {len(db_path_list)} db paths"
        )
        if knowledge_list:
            assert len(knowledge_list) == len(question_list), (
                f"Mismatch: {len(knowledge_list)} knowledge vs {len(question_list)} questions"
            )

        return {
            "question_list": question_list,
            "db_path_list": db_path_list,
            "knowledge_list": knowledge_list,
            "total_questions": len(question_list),
            "sql_dialect": sql_dialect,
            "db_root_path": db_root_path,
        }

    except FileNotFoundError:
        raise FileNotFoundError(f"Evaluation file not found at '{eval_path}'")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the evaluation file or input data")
    except Exception as e:
        raise RuntimeError(f"Error loading evaluation data: {str(e)}")


def _decouple_question_schema(
    datasets: dict, db_root_path: str
) -> tuple[list[str], list[str], list[str]]:
    """
    Decouple question schema from datasets - equivalent to the reference code's decouple_question_schema function.

    Args:
        datasets: List of evaluation data entries
        db_root_path: Root path for database files

    Returns:
        Tuple[List[str], List[str], List[str]]: question_list, db_path_list, knowledge_list
    """
    question_list = []
    db_path_list = []
    knowledge_list = []

    for i, data in enumerate(datasets):
        question_list.append(data["question"])

        # Construct database path following reference code pattern:
        # cur_db_path = db_root_path + data["db_id"] + "/" + data["db_id"] + ".sqlite"
        cur_db_path = (
            db_root_path + "/" + data["db_id"] + "/" + data["db_id"] + ".sqlite"
        )
        db_path_list.append(cur_db_path)

        # Add knowledge/evidence if available
        knowledge_list.append(data.get("evidence", data.get("knowledge", "")))

    return question_list, db_path_list, knowledge_list


def extract_db_id_from_path(db_path: str) -> str:
    """
    Extract database ID from database path.

    Args:
        db_path (str): Database file path

    Returns:
        str: Database ID
    """
    # Extract db_id from path like: './mini_dev_data/dev_databases/restaurant_1/restaurant_1.sqlite'
    return db_path.split("/")[-1].split(".sqlite")[0]
