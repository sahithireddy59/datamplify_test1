from Datamplify.settings import logger 
from Connections.utils import generate_engine
import duckdb,re,keyword,sqlglot,time
from  Datamplify import settings 
from sqlalchemy import text
from sqlglot import exp
from Connections import models as conn_models





def quote_all_identifiers(sql):
    """
    Using Sqlglot add quotes to every column and tablenames in query
    """
    try:
        tree = sqlglot.parse_one(sql, read='postgres')

        def quote_expr(node):
            if isinstance(node, exp.Identifier):
                return exp.to_identifier(node.name, quoted=True)
            if isinstance(node, exp.Column):
                table = node.table
                column = node.name

                table_quoted = exp.to_identifier(table, quoted=True) if table else None
                column_quoted = exp.to_identifier(column, quoted=True)

                return exp.Column(this=column_quoted, table=table_quoted)
            return node

        new_tree = tree.transform(quote_expr)
        return new_tree.sql(dialect='postgres')

    except Exception as e:
        logger.info("Parsing error:", e)
        return sql


def quote_identifier(identifier):
    """
    Adding Quotes bases on Condition
    """
    if not isinstance(identifier, str):
        return identifier  
    safe_pg_identifier = re.compile(r'^[a-z_][a-z0-9_]*$')
    
    if not safe_pg_identifier.match(identifier) or keyword.iskeyword(identifier):
        return f'"{identifier}"'
    return identifier


def process_column_expression(col_expr):
    """
    Identify the table and column and add quotes to it
    """
    if '.' in col_expr:
        table_alias, column_name = col_expr.split('.', 1)
        table_alias = table_alias
        column_name = quote_identifier(column_name)
        return f"{table_alias}.{column_name}"
    else:
        return quote_identifier(col_expr)
    
def Query_generator(source_attributes: list = [],attributes: list =[],from_clause: tuple =(),schema: str ='',join_list: list = None,where_clause: str = '',group_by_clause: list =None,having_clause: str = '',remove_duplicates:bool = False):
    """
    Generate a dynamic Query based on Columns, joins, where ,groupby and having clause
    """
    source_columns = []
    for col in source_attributes:
        if len(col) == 4:
            alias, _, full_col_expr, _ = col
        elif len(col) == 3:
            alias, _, full_col_expr = col
        else:
            raise ValueError(f"Invalid source_attribute format: {col}")
        processed_expr = process_column_expression(full_col_expr)
        source_columns.append(f'{processed_expr} AS {quote_identifier(alias)}')

    # Handle attributes (assume raw SQL expression, just alias them)
    attribute_columns = []
    for col in attributes:
        alias, _, expr= col
        attribute_columns.append(f'{expr} AS "{alias}"')

    # Combine all columns
    all_columns = source_columns + attribute_columns
    columns = ',\n\t'.join(all_columns) if all_columns else '*'

    if schema !='':
        schema +='.'
    from_class = f""" {schema}{from_clause[0]} AS {from_clause[1]} """

    join_clauses = ''
    if join_list:
        join_clauses = '\n'.join(
            f""" {join_type.upper()} {schema}{table_name}  ON {condition} """
            for join_type, table_name,  condition in join_list
        )

    where_sql = f"\nWHERE {where_clause}" if where_clause else ''

    group_by_sql = ''
    if group_by_clause:
        group_exprs = ', '.join(f"{quote_identifier(expr[0])}" for expr in group_by_clause)
        group_by_sql = f"\nGROUP BY {group_exprs}"

    having_sql = f"\nHAVING {having_clause}" if having_clause else ''

    query = f"""SELECT 
        \t{columns}
        FROM {from_class} {join_clauses}{where_sql}{group_by_sql}{having_sql}
        """
    return quote_all_identifiers(query.strip())

# Data Extract From CSV
def Extract_from_CSV(csv_path,dag_id,task_id,user_id,target_hierarchy_id,source_attributes,attributes,source_table_name,hierarchy_id):
    """
    Extract CSV Data from Source File then Dump into Target database as temp table
    
    """
    target_engine_data = generate_engine(target_hierarchy_id, user_id)
    target_engine = target_engine_data['engine']
    target_schema = target_engine_data['schema']
    target_conn_str = str(target_engine.url)

    conn = duckdb.connect(database=':memory:')

    conn.sql(f"ATTACH '{target_conn_str}' AS target_db (TYPE POSTGRES, SCHEMA '{target_schema}');")

    from_clause = (source_table_name, task_id)
    generated_query = Query_generator(
        source_attributes=source_attributes,
        attributes=attributes,
        from_clause=from_clause,
        schema=target_schema
    )
    cte = f""" "{task_id}" AS (\n{generated_query}\n)"""

    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"
    if csv_path=='/var/www/AB_Client/client2/':
        hierarchy_data = conn_models.Connections.objects.get(id=hierarchy_id).table_id
        csv_path = conn_models.FileConnections.objects.get(id=hierarchy_data).source
    
    source_columns = []
    for col in source_attributes:
        if len(col) == 4:
            alias, _, full_col_expr, _ = col
        elif len(col) == 3:
            alias, _, full_col_expr = col
        else:
            raise ValueError(f"Invalid source_attribute format: {col}")
        
        processed_expr = process_column_expression(full_col_expr)
        source_columns.append(f'{processed_expr}')  # Removed aliasing

        attribute_columns = []
        for col in attributes:
            alias, _, expr = col
            attribute_columns.append(expr)  # Removed aliasing

        all_columns = source_columns + attribute_columns
        extract_columns = ',\n\t'.join(all_columns) if all_columns else '*'
    query = f"""
    INSTALL httpfs;
    LOAD httpfs;
    CREATE TABLE target_db.{target_table_name} AS 
    SELECT {extract_columns} FROM read_csv_auto('{csv_path}', AUTO_DETECT=TRUE);
    """
    conn.sql(query)
    return {'status': 200,'target_table':target_table_name,'query': cte}



def Extract_from_database(hierarchy_id, user_id, table_name, task_id, dag_id,
                           source_attributes, attributes, target_hierarchy_id, **kwargs):
    """
    Extract Table Data from Source Connection then Dump into Target database as temp table 
    """
    source_engine_data = generate_engine(hierarchy_id, user_id)
    source_engine = source_engine_data['engine']
    source_schema = source_engine_data['schema']
    source_conn_str = str(source_engine.url)

    target_engine_data = generate_engine(target_hierarchy_id, user_id)
    target_engine = target_engine_data['engine']
    target_schema = target_engine_data['schema']
    target_conn_str = str(target_engine.url)

    conn = duckdb.connect(database=':memory:')

    conn.sql(f"ATTACH '{source_conn_str}' AS source_db (TYPE POSTGRES, SCHEMA '{source_schema}');")

    conn.sql(f"ATTACH '{target_conn_str}' AS target_db (TYPE POSTGRES, SCHEMA '{target_schema}');")

    from_clause = (table_name, task_id)
    generated_query = Query_generator(
        source_attributes=source_attributes,
        attributes=attributes,
        from_clause=from_clause,
        schema=source_schema
    )

    cte = f""" "{task_id}" AS (\n{generated_query}\n)"""
    logger.info(f""" Query: WITH {cte} SELECT * FROM "{task_id}" """)

    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"
    full_target_table = f"target_db.{target_schema}.{target_table_name}"


    conn.sql(f"""
        CREATE TABLE {full_target_table} AS
        SELECT * FROM postgres_query('source_db', $$WITH {cte} SELECT * FROM "{task_id}" $$);
    """)
    logger.info(f"Data extracted and loaded into: {full_target_table}")

    result = conn.sql(f"SELECT COUNT(*) FROM {full_target_table};")
    logger.info(f"Total Records: {result.fetchone()[0]}")

    conn.sql("DETACH source_db;")
    conn.close()

    cte = cte.replace(source_schema,target_schema)

    return {
        'status': 200,
        'target_table': target_table_name,
        'query':cte
    }



def Load_into_database(hierarchy_id, user_id, truncate_table, create_table, target_table, attribute_mapper,previous_id, extract_table_name):
    """
    Load Transformed Data into Target Database
    """
    
    with duckdb.connect(database=':memory:') as conn:

        engine_data = generate_engine(hierarchy_id, user_id=user_id)
        engine = engine_data['engine']
        schema = engine_data['schema']
        
        conn_str = f"""postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}/{engine.url.database}"""
        conn.sql(f"ATTACH '{conn_str}' AS pg_db1 (TYPE POSTGRES, SCHEMA '{schema}');")

        cursor = engine.connect()

        if truncate_table:
            cursor.execute(f'TRUNCATE TABLE pg_db1."{target_table}"')
            logger.info(f"Table Truncated: {target_table}")
        if create_table:
            cursor.execute(text(f'''
                CREATE TABLE "{schema}"."{target_table}" AS 
                SELECT *
                FROM (SELECT * FROM "{schema}"."{extract_table_name}") AS "{extract_table_name}"
                LIMIT 0
            '''))
            logger.info(f"Table Created {target_table}")
            table_params = f""
            trans_params = ' * '
        else:
            table_params1 = ', '.join(f"{i[0]}" for i in attribute_mapper)
            table_params = f"({table_params1})"
            trans_params = ', '.join(f""" cast("{i[2]}" as {i[3]}) as "{i[0]}" """ for i in attribute_mapper)

        result_count = cursor.execute(text(f"""SELECT count(*) FROM "{schema}"."{extract_table_name}";"""))
        row_count = result_count.fetchone()[0]
        if row_count >0:
            insert_query = f"""
            INSERT INTO "{schema}"."{target_table}" {table_params}
            SELECT {trans_params}
            FROM (SELECT * FROM "{schema}"."{extract_table_name}") AS "{extract_table_name}"
            """
            logger.info(f"{insert_query}")
            result = cursor.execute(text(insert_query))
        logger.info(f"Total Records inserted into {target_table} : {row_count}")
        conn.commit()

    return {'status': 200, 'message': 'success'}




def Delete_temp_tables(sources,hierarchy_id,user_id,**kwargs):
    """
    Deleting all temp tables created in Transformation 
    """
    ti = kwargs['ti']
    engine_data = generate_engine(hierarchy_id,user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    with engine.connect() as connection:
        for id, value in sources:
            table_name = ti.xcom_pull(task_ids=id, key=value)
            if table_name:
                drop_query = text(f'DROP TABLE IF EXISTS "{schema}"."{table_name}";')
                connection.execute(drop_query)
            else:
                pass
    return True


def Extraction(dag_id,task_id,source_type,path,hierarchy_id,user_id,source_table_name,source_attributes,attributes,target_hierarchy_id,**kwargs):
        """
        Extract Data from source connection and load into target connection
        """
        if source_type.lower() == 'file':
            logger.info("[INFO] Source is CSV")
            if settings.DATABASES['default']['NAME']=='analytify_qa': 
                path=f'/var/www/AB_Client/client2/{path}'
            else:
                path=path
 
            csv_extract = Extract_from_CSV(path,dag_id,task_id,user_id,target_hierarchy_id,source_attributes,attributes,source_table_name,hierarchy_id)
            if csv_extract['status'] == 200:
                query = csv_extract['query']
                kwargs['ti'].xcom_push(key=task_id, value=query)
                kwargs['ti'].xcom_push(key=source_table_name, value=csv_extract['target_table'])
                return query
            else:
                logger.error(f"""[Error] {csv_extract['message']}""")
        else:
            logger.info('source is database')
            db_extract = Extract_from_database(hierarchy_id,user_id,source_table_name,task_id,dag_id,source_attributes,attributes,target_hierarchy_id)
            if db_extract['status'] == 200:
                query = db_extract['query']
                ti = kwargs['ti']

                ti.xcom_push(key=task_id, value=db_extract['target_table'])
                return query
            else:
                logger.error(f"""[Error] {db_extract['message']}""")



def Loading(hierarchy_id,user_id,dag_id,truncate,create,format,previous_id,target_table_name,attribute_mapper,sources,**kwargs):
        ti = kwargs['ti']
        if format.lower() == 'csv':
            pass
        elif format.lower() == 'database':
            previous_query = ti.xcom_pull(task_ids=previous_id, key=previous_id)
            table_name = ti.xcom_pull(task_ids=previous_id, key=previous_id)
            # Fallback: if coming from a Router, the XCom key is the Router output name.
            # Use target_table_name as the output name to pull its produced temp table.
            if not table_name:
                table_name = ti.xcom_pull(task_ids=previous_id, key=target_table_name)
            db_load = Load_into_database(hierarchy_id,user_id, truncate,create, target_table_name,attribute_mapper,previous_id,table_name)
            if db_load['status'] ==200:
                logger.info(' Data Dumped into Target Database')
                deletetion_confirmation = Delete_temp_tables(sources,hierarchy_id,user_id,**kwargs)
                logger.info(deletetion_confirmation)
            else:
                logger.error({db_load['message']})
        pass


# ... (rest of the code remains the same)


def Router(conditions, dag_id, task_id, previous_id, target_hierarchy_id, user_id, **kwargs):
    """
    Route data based on conditions to different output paths.

    Args:
        conditions (list): List of (condition, output_name) tuples where:
                         - condition: SQL where clause condition
                         - output_name: Name identifier for the output path
        dag_id (str): DAG identifier
        task_id (str): Task identifier
        previous_id (str): Previous task identifier to pull data from
        target_hierarchy_id (str): Target hierarchy identifier
        user_id (str): User identifier
        sources (list): Source information
        **kwargs: Additional keyword arguments

    Returns:
        dict: A dictionary mapping output names to their respective table names
    """
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']
    unix_suffix = int(time.time())

    table_name = ti.xcom_pull(task_ids=previous_id, key=previous_id)

    result_tables = {}

    # Process each condition and create corresponding output tables
    for condition, output_name in conditions:
        output_table_name = f"extracted_{task_id}_{output_name}_{unix_suffix}"

        # Generate query with the specific condition
        from_clause = (table_name, previous_id)
        generated_query = Query_generator(from_clause=from_clause, where_clause=condition, schema=schema)

        cte = f""" "{task_id}_{output_name}" AS (\n{generated_query}\n) """

        # Log the query and count of records
        result = conn.sql(f"""SELECT * FROM postgres_query('pg_db', $$WITH {cte} SELECT count(*) FROM "{task_id}_{output_name}" $$);""")
        logger.info(f""" [Router Query for {output_name}]\n WITH {cte} SELECT * FROM "{task_id}_{output_name}" """)
        logger.info(f"Total Records for {output_name}: {result.fetchone()[0]}")

        # Create the output table
        with engine.begin() as conn1:
            conn1.execute(text(f"""
                CREATE TABLE "{schema}"."{output_table_name}" AS
                WITH {cte} SELECT * FROM "{task_id}_{output_name}";
            """))

        # Store the output table name (mapping) and push XCom
        result_tables[output_name] = output_table_name
        # Push to XCom for each output path using the output name as key
        ti.xcom_push(key=f"{output_name}", value=output_table_name)
        # Optionally also push the generated CTE under a separate key for debugging/inspection
        ti.xcom_push(key=f"{output_name}__cte", value=cte)
    conn.sql("DETACH pg_db")

    return result_tables