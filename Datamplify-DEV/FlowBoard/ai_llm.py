import json
import logging
import os
import re
import requests
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_MODEL = "gemini-2.0-flash-exp"
GOOGLE_AI_AVAILABLE = False

# Initialize Google AI if available
try:
    import google.generativeai as genai
    google_api_key = os.getenv('GOOGLE_AI_API_KEY')
    if google_api_key:
        genai.configure(api_key=google_api_key)
        GOOGLE_AI_AVAILABLE = True
    else:
        logger.warning("GOOGLE_AI_API_KEY not set. Google AI features disabled.")
except ImportError:
    logger.warning("google-generativeai package not found. Google AI features disabled.")

def is_ollama_available(base_url: str = "http://127.0.0.1:11434", timeout: int = 2) -> bool:
    """Check if Ollama is available at the given base URL."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        logger.debug(f"Ollama not available: {e}")
        return False


def query_google_ai(prompt: str, model: str = None) -> Optional[str]:
    """Query Google's Generative AI with the given prompt."""
    if not GOOGLE_AI_AVAILABLE:
        logger.error("Google AI is not properly configured")
        return None
        
    try:
        model_name = model or DEFAULT_MODEL
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.9,
                "max_output_tokens": 1000,
            },
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE_SPEECH": "BLOCK_NONE",
                "SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "DANGEROUS_CONTENT": "BLOCK_NONE",
            },
        )
        
        if hasattr(response, 'text'):
            return response.text.strip()
        logger.error(f"Google AI returned no text. Response: {response}")
        return None
            
    except Exception as e:
        logger.error(f"Error querying Google AI: {e}", exc_info=True)
        return None


def query_ollama_llm(prompt: str, model: str = "llama2") -> Optional[str]:
    """Query local Ollama LLM with the given prompt."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', '').strip()
            
        logger.error(f"Ollama API error: {response.status_code} - {response.text}")
        return None
            
    except Exception as e:
        logger.error(f"Error querying Ollama: {e}")
        return None

def query_llm(prompt: str, provider: str = "google", model: str = None) -> Optional[str]:
    """
    Query the specified AI provider with the given prompt.
    
    Args:
        prompt: The prompt to send to the AI
        provider: AI provider ("google", "ollama", "perplexity", or "heuristic")
        model: Model name to use (provider-specific)
    
    Returns:
        The AI response text, or None if failed/not applicable
    """
    try:
        provider = provider.lower()
        
        if provider == "google":
            return query_google_ai(prompt, model or DEFAULT_MODEL)
        elif provider == "ollama" and is_ollama_available():
            model = model or "llama2"
            return query_ollama_llm(prompt, model)
        elif provider == "perplexity":
            model = model or "sonar"
            return query_perplexity_llm(prompt, model)
        else:
            logger.warning(f"Provider '{provider}' not available, falling back to heuristic")
            return None
    except Exception as e:
        logger.error(f"Error querying {provider} LLM: {e}")
        return None

def create_one_to_one_mapping(
    source_table: str,
    target_table: str,
    connection_params: Dict[str, Any],
    provider: str = "google",
    model: str = None
) -> Dict[str, Any]:
    """
    Create a one-to-one mapping from source table to target table using AI.
    
    Args:
        source_table: Name of the source table (e.g., 'dim_samples')
        target_table: Name of the target table to create (e.g., 'dim_sample_ai')
        connection_params: Database connection parameters
        provider: AI provider to use ("google", "ollama", or "heuristic")
        model: Model name to use (provider-specific)
        
    Returns:
        Dictionary with operation status and details
    """
    try:
        # 1. Get source table schema
        source_columns = get_table_columns(source_table, connection_params)
        
        if not source_columns:
            return {"status": "error", "message": f"Could not fetch schema for {source_table}"}
        
        # 2. Generate target table DDL using AI
        ddl_prompt = f"""
        Generate a CREATE TABLE statement for '{target_table}' with the same structure as '{source_table}'.
        Source table has these columns: {json.dumps(source_columns, indent=2)}
        
        Return only the SQL statement, nothing else.
        """
        
        ddl_sql = query_llm(ddl_prompt, provider=provider, model=model)
        
        if not ddl_sql:
            return {"status": "error", "message": "Failed to generate DDL with AI"}
            
        # 3. Create target table
        execute_sql(ddl_sql, connection_params)
        
        # 4. Create and execute INSERT statement
        columns = [col['name'] for col in source_columns]
        columns_str = ', '.join(columns)
        insert_sql = f"""
        INSERT INTO {target_table} ({columns_str})
        SELECT {columns_str} FROM {source_table}
        """
        
        execute_sql(insert_sql, connection_params)
        
        return {
            "status": "success",
            "message": f"Successfully created and populated {target_table}",
            "rows_copied": get_row_count(target_table, connection_params)
        }
        
    except Exception as e:
        logger.error(f"Error in create_one_to_one_mapping: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def get_database_connection(connection_params: Dict[str, Any]):
    """Create a database connection based on the provided parameters."""
    db_type = connection_params.get('type', 'postgresql')
    
    try:
        if db_type == 'postgresql':
            import psycopg2
            return psycopg2.connect(
                host=connection_params.get('host'),
                database=connection_params.get('database'),
                user=connection_params.get('user'),
                password=connection_params.get('password'),
                port=connection_params.get('port', 5432)
            )
        elif db_type == 'mysql':
            import mysql.connector
            return mysql.connector.connect(
                host=connection_params.get('host'),
                database=connection_params.get('database'),
                user=connection_params.get('user'),
                password=connection_params.get('password'),
                port=connection_params.get('port', 3306)
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    except ImportError as e:
        logger.error(f"Database driver not installed: {e}")
        raise


def get_table_columns(table_name: str, connection_params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Get column information for a table."""
    db_type = connection_params.get('type', 'postgresql')
    
    if db_type == 'postgresql':
        query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
    elif db_type == 'mysql':
        query = f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        AND table_schema = '{connection_params.get('database')}'
        ORDER BY ordinal_position
        """
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    try:
        conn = get_database_connection(connection_params)
        with conn.cursor() as cursor:
            cursor.execute(query, (table_name,)) if db_type == 'postgresql' else cursor.execute(query)
            columns = cursor.fetchall()
            return [{"name": col[0], "type": col[1]} for col in columns]
    except Exception as e:
        logger.error(f"Error fetching columns for table {table_name}: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


def execute_sql(sql: str, connection_params: Dict[str, Any], params: tuple = None) -> Any:
    """Execute SQL statement with parameters."""
    conn = None
    try:
        conn = get_database_connection(connection_params)
        with conn.cursor() as cursor:
            cursor.execute(sql, params) if params else cursor.execute(sql)
            if sql.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error executing SQL: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_row_count(table_name: str, connection_params: Dict[str, Any]) -> int:
    """Get row count of a table."""
    # This is a placeholder - implement based on your database
    # sql = f"SELECT COUNT(*) FROM {table_name}"
    # return execute_query(sql, [], connection_params)[0][0]
    raise NotImplementedError("Implement get_row_count for your database")


def generate_mappings_between_tables(
    source_table: str,
    target_table: str,
    instructions: str,
    connection_params: Dict[str, Any],
    provider: str = "google",
    model: str = None
) -> Dict[str, Any]:
    """
    Generate field mappings between two database tables using natural language instructions.
    
    Args:
        source_table: Name of the source table
        target_table: Name of the target table
        instructions: Natural language instructions for mapping
        connection_params: Database connection parameters
        provider: AI provider to use ("google", "ollama", or "heuristic")
        model: Model name to use (provider-specific)
        
    Returns:
        Dictionary with 'mappings', 'unresolved', and 'status' keys
    """
    try:
        # Get source and target table schemas
        source_columns = get_table_columns(source_table, connection_params)
        target_columns = get_table_columns(target_table, connection_params)
        
        if not source_columns:
            return {"status": "error", "message": f"Could not fetch schema for source table: {source_table}"}
        if not target_columns:
            return {"status": "error", "message": f"Could not fetch schema for target table: {target_table}"}
        
        # Generate mappings using AI
        return generate_mappings_from_columns(
            source_columns=source_columns,
            target_columns=target_columns,
            instructions=instructions,
            provider=provider,
            model=model
        )
    except Exception as e:
        logger.error(f"Error in generate_mappings_between_tables: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def generate_mappings_from_instructions(
    source_columns: List[Dict[str, Any]],
    target_columns: List[Dict[str, Any]],
    instructions: str,
    provider: str = "google",
    model: str = None
) -> Dict[str, Any]:
    """
    Generate field mappings based on natural language instructions.
    
    Args:
        source_columns: List of source column definitions with 'name' and 'type'
        target_columns: List of target column definitions with 'name' and 'type'
        instructions: Natural language instructions for mapping
        provider: AI provider to use ("google", "ollama", or "heuristic")
        model: Model name to use (provider-specific)
        
    Returns:
        Dictionary with 'mappings', 'unresolved', and 'status' keys
    """
    try:
        prompt = f"""
        You are a data mapping assistant. Create field mappings based on the following instructions:
        
        SOURCE COLUMNS:
        {json.dumps(source_columns, indent=2)}
        
        TARGET COLUMNS:
        {json.dumps(target_columns, indent=2)}
        
        INSTRUCTIONS: {instructions}
        
        Return a JSON object with two keys:
        1. "mappings": List of {{"target": "target_col", "source": "source_col", "transform": "transform_func"}}
        2. "unresolved": List of columns that couldn't be mapped
        
        Example:
        {{
          "mappings": [
            {{"target": "customer_id", "source": "id", "transform": null}},
            {{"target": "full_name", "source": "concat(first_name, ' ', last_name)", "transform": "SQL"}}
          ],
          "unresolved": ["some_column"]
        }}
        """
        
        response = query_llm(prompt, provider=provider, model=model)
        if not response:
            return {"status": "error", "message": "Failed to generate mappings with AI"}
            
        # Clean and parse the response
        clean_response = re.sub(r'^```(?:json)?\n|\n```$', '', response, flags=re.MULTILINE).strip()
        result = json.loads(clean_response)
        
        # Validate response structure
        if not isinstance(result, dict) or "mappings" not in result:
            raise ValueError("Invalid response format from AI")
            
        return {
            "status": "success",
            "mappings": result.get("mappings", []),
            "unresolved": result.get("unresolved", [])
        }
        
    except Exception as e:
        logger.error(f"Error in generate_mappings_from_instructions: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def suggest_mappings_llm(
    source: List[Dict[str, Any]],
    target: List[Dict[str, Any]],
    model: str = None,
    provider: str = "google",
    temperature: float = 0.2
) -> Dict[str, Any]:
    """
    Generate field mappings between source and target schemas using AI.
    
    Args:
        source: List of source column definitions
        target: List of target column definitions
        model: Model name to use (provider-specific)
        provider: AI provider ("google", "ollama", or "heuristic")
        temperature: Temperature for the AI response (0.0 to 1.0)
    
    Returns:
        Dictionary with 'mappings' and 'unresolved' keys
    """
    try:
        prompt = """You are a data mapping expert. Given source and target schemas, 
        suggest how to map fields from source to target. Consider:
        - Column names (with fuzzy matching for typos/abbreviations)
        - Data types (with safe casting where possible)
        - Any transformations needed
        
        Source Schema:
        {source_schema}
        
        Target Schema:
        {target_schema}
        
        Return a JSON object with two keys:
        1. "mappings": List of {{target, source, transform, cast, confidence, rationale}}
        2. "unresolved": List of {{target, reasons}} for unmapped targets
        
        Example:
        {{
          "mappings": [
            {{
              "target": "customer_id",
              "source": "id",
              "transform": null,
              "cast": "TEXT",
              "confidence": 0.95,
              "rationale": "Direct mapping with type casting"
            }}
          ],
          "unresolved": [
            {{
              "target": "full_name",
              "reasons": ["No clear source field matches"]
            }}
          ]
        }}""".format(
            source_schema=json.dumps(source, indent=2),
            target_schema=json.dumps(target, indent=2)
        )
        
        if provider == "google" and not GOOGLE_AI_AVAILABLE:
            logger.warning("Google AI is not available, falling back to heuristic")
            provider = "heuristic"
        
        if provider == "heuristic":
            return {"mappings": [], "unresolved": []}
        
        response = query_llm(prompt, provider, model)
        if not response:
            logger.warning("LLM query failed, falling back to heuristic")
            return {"mappings": [], "unresolved": []}
        
        # Clean and parse the response
        clean_response = re.sub(r'^```(?:json)?\n|\n```$', '', response, flags=re.MULTILINE).strip()
        
        try:
            result = json.loads(clean_response)
            if not isinstance(result, dict) or "mappings" not in result:
                raise ValueError("Invalid response format")
            
            # Ensure all required fields are present in each mapping
            for mapping in result.get("mappings", []):
                mapping.setdefault("transform", None)
                mapping.setdefault("cast", None)
                mapping.setdefault("confidence", 0.9)
                mapping.setdefault("rationale", "AI-suggested mapping")
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}\nResponse: {response}")
            return {"mappings": [], "unresolved": []}
            
    except Exception as e:
        logger.error(f"Error in suggest_mappings_llm: {e}", exc_info=True)
        return {"mappings": [], "unresolved": []}
