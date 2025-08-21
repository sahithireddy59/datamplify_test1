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
            table_name = ti.xcom_pull(task_ids=previous_id,key=previous_id)
            db_load = Load_into_database(hierarchy_id,user_id, truncate,create, target_table_name,attribute_mapper,previous_id,table_name)
            if db_load['status'] ==200:
                logger.info(' Data Dumped into Target Database')
                deletetion_confirmation = Delete_temp_tables(sources,hierarchy_id,user_id,**kwargs)
                logger.info(deletetion_confirmation)
            else:
                logger.error({db_load['message']})
        pass



def ETL_Filter(filter_condition, dag_id, task_id, previous_id, target_hierarchy_id, user_id,sources, **kwargs):
    """
    Filter The raw Data Based on Condition
    """
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']
    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"

    table_name = ti.xcom_pull(task_ids=previous_id,key=previous_id)
    from_clause = (table_name, previous_id)
    generated_query = Query_generator(from_clause=from_clause, where_clause=filter_condition,schema=schema)

    cte = f""" "{task_id}" AS (\n{generated_query}\n) """


    result = conn.sql(f"""SELECT * FROM postgres_query('pg_db', $$WITH  {cte} SELECT count(*) FROM "{task_id}" $$);""")
    logger.info(f""" [Filter Query]\n WITH {cte} SELECT * FROM "{task_id}" """)
    logger.info(f"Total Records: {result.fetchone()[0]}")
    with engine.begin() as conn1:
        conn1.execute(text(f""" 
            CREATE TABLE "{schema}"."{target_table_name}" AS
            WITH {cte} SELECT * FROM "{task_id}";
        """))
    kwargs['ti'].xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")

    return cte



def Expressions(Expression_list, dag_id, task_id, previous_id, target_hierarchy_id, user_id,sources, **kwargs):
    ti = kwargs['ti']


    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"

    table_name = ti.xcom_pull(task_ids=previous_id,key=previous_id)

    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']

    conn.sql(f"ATTACH '{str(engine.url)}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")
    
    from_clause = (table_name, previous_id)    
    generated_query = Query_generator(attributes=Expression_list,from_clause=from_clause,schema=schema)
    new_cte_query = f""" "{task_id}"  AS (\n{generated_query}\n) """

    result = conn.sql(f"""SELECT * FROM postgres_query('pg_db', $$WITH {new_cte_query} SELECT count(*) FROM "{task_id}" $$);""")
    logger.info(f""" [Expressions Query]\n WITH {new_cte_query} SELECT * FROM "{task_id}" """)
    logger.info(f"Total Records: {result.fetchone()[0]}")
    with engine.begin() as conn1:
        conn1.execute(text(f""" 
            CREATE TABLE "{schema}"."{target_table_name}" AS
            WITH {new_cte_query} SELECT * FROM "{task_id}";
        """))

    ti.xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")

    return target_table_name



def Join(primary_table, joining_list, where_clause, dag_id, task_id, previous_id, attributes, target_hierarchy_id, user_id,sources, **kwargs):
    ti = kwargs['ti']
    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"


    engine_data = generate_engine(target_hierarchy_id, user_id=user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = f"postgresql://{engine.url.username}:{engine.url.password}@{engine.url.host}/{engine.url.database}"
    
    conn = duckdb.connect(database=':memory:')
    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")
    
    from_clause = (primary_table,primary_table)
    generated_query = Query_generator(attributes=attributes,join_list=joining_list,where_clause=where_clause,from_clause=from_clause,schema=schema)
    logger.info(f" generated _query {generated_query}")
    for pid in previous_id:
        table_name = ti.xcom_pull(task_ids=pid,key=pid)
        pattern = rf'\b{re.escape(pid)}\b'
        if re.search(pattern, generated_query):
            generated_query = re.sub(pattern,  table_name, generated_query) 

    new_cte_query = f""" "{task_id}" AS (\n{generated_query}\n) """
    logger.info(new_cte_query)
    with engine.begin() as conn1:
        result = conn1.execute(text(f""" 
            WITH {new_cte_query} SELECT count(*) FROM "{task_id}"
        """))

    logger.info(f""" [Join Query]\n WITH {new_cte_query} SELECT * FROM "{task_id}" """)
    logger.info(f"Total Records: {result.fetchone()[0]}")
    with engine.begin() as conn1:
        conn1.execute(text(f""" 
            CREATE TABLE "{schema}"."{target_table_name}" AS
            WITH {new_cte_query} SELECT * FROM "{task_id}";
        """))

    ti.xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")

    
    return new_cte_query



def Remove_duplicates(group_attributes, having_clause, task_id, dag_id, previous_id, attributes, hierarchy_id, user_id,sources,**kwargs):
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']


    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"

    table_name = ti.xcom_pull(task_ids=previous_id,key=previous_id)
    from_clause = (table_name, previous_id)
    generated_query = Query_generator(
        source_attributes=group_attributes,
        attributes=attributes,
        group_by_clause=group_attributes,
        having_clause=having_clause,
        from_clause=from_clause,
        schema=schema
    )

    cte = f""" "{task_id}" AS (\n{generated_query}\n) """

    result = conn.sql(f""" SELECT * FROM postgres_query('pg_db', $$WITH  {cte} SELECT count(*) FROM "{task_id}" $$);""")
    with engine.begin() as conn1:
        conn1.execute(text(f""" 
            CREATE TABLE "{schema}"."{target_table_name}" AS
            WITH {cte} SELECT * FROM "{task_id}";
        """))

    logger.info(f""" [Remove Duplicates Query]\n WITH  {cte} SELECT * FROM "{task_id}" """)
    logger.info(f"Total Records: {result.fetchone()[0]}")
    kwargs['ti'].xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")


    return {'status':200}


# {
#   "type": "Rank",
#   "id": "rank_1",
#   "previous_id": "SRC_Customers",
#   "rank_by_cols": ["purchase_amount", "order_date"],
#   "rank_type": "RANK",
#   "partition_by_cols": ["region"],
#   "output_col": "rank_value",
#   "ascending": false,
#   "include_ties": true
# }


def Rank(rank_by_cols, rank_type, partition_by_cols, output_col, dag_id, task_id, previous_id, target_hierarchy_id, user_id, sources, ascending=True, include_ties=True, **kwargs):
    """
    Assigns ranking values to rows in a dataset based on specified columns.

    Args:
        rank_by_cols (list): List of columns to rank by
        rank_type (str): Type of rank to apply: 'RANK', 'DENSE_RANK', 'ROW_NUMBER', or 'NTILE'
        partition_by_cols (list): List of columns to partition by (optional)
        output_col (str): Name of the output column to contain the rank values
        dag_id (str): DAG identifier
        task_id (str): Task identifier
        previous_id (str): Previous task identifier to pull data from
        target_hierarchy_id (str): Target hierarchy identifier
        user_id (str): User identifier
        sources (list): Source information
        ascending (bool): Whether to rank in ascending (True) or descending (False) order
        include_ties (bool): Whether to include ties in ranking
        **kwargs: Additional keyword arguments

    Returns:
        str: Name of the created output table
    """
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']
    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"

    # Get source table name
    source_table_name = ti.xcom_pull(task_ids=previous_id, key=previous_id)

    # Determine the correct rank function based on rank_type
    rank_function = rank_type.upper()
    if rank_function not in ['RANK', 'DENSE_RANK', 'ROW_NUMBER', 'NTILE']:
        # Default to RANK if invalid type provided
        rank_function = 'RANK'

    # Format the ORDER BY clause
    order_direction = "ASC" if ascending else "DESC"
    order_by_clause = ", ".join([f'"{previous_id}"."{col}" {order_direction}' for col in rank_by_cols])

    # Format the PARTITION BY clause if partition columns are provided
    partition_by_clause = ""
    if partition_by_cols and len(partition_by_cols) > 0:
        partition_by_str = ", ".join([f'"{previous_id}"."{col}"' for col in partition_by_cols])
        partition_by_clause = f"PARTITION BY {partition_by_str}"

    # Build the column list for the SELECT statement
    # Include all columns from the source table plus the rank column
    column_query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = '{schema}'
        AND table_name = '{source_table_name}'
        ORDER BY ordinal_position
    """

    columns = []
    with engine.connect() as conn1:
        result = conn1.execute(text(column_query))
        columns = [row[0] for row in result]

    # Create attributes for Query_generator
    source_attributes = [(col, 'string', f'"{previous_id}"."{col}"') for col in columns]
    rank_attribute = [(output_col, 'string', f'{rank_function}() OVER ({partition_by_clause} ORDER BY {order_by_clause})')]

    # Generate the query using Query_generator
    from_clause = (source_table_name, previous_id)
    generated_query = Query_generator(
        source_attributes=source_attributes,
        attributes=rank_attribute,
        from_clause=from_clause,
        schema=schema
    )

    # Create CTE
    cte = f""" "{task_id}" AS (
{generated_query}
)"""
    logger.info(f"[Rank Transformation] Generated query with Query_generator:\n{cte}")

    # Execute the query and create the target table using the generated query
    with engine.begin() as conn1:
        conn1.execute(text(f"""
            CREATE TABLE "{schema}"."{target_table_name}" AS
            WITH {cte} SELECT * FROM "{task_id}";
        """))

    # Count records in result
    with engine.begin() as conn1:
        result = conn1.execute(text(f"""
            SELECT COUNT(*) FROM "{schema}"."{target_table_name}"
        """))
        total_count = result.fetchone()[0]

    logger.info(f"Rank transformation created table with {total_count} total records")

    # Store result table name in XCom
    ti.xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")

    return target_table_name



# {
#   "type": "Normalizer",
#   "id": "normalizer_1",
#   "previous_id": "SRC_SalesData",
#   "group_by_cols": ["region", "salesperson"],
#   "pivot_col": "metric_name",
#   "value_cols": ["q1_sales", "q2_sales", "q3_sales", "q4_sales"],
#   "output_cols": ["metric_value"]
# }


def Normalizer(group_by_cols, pivot_col, value_cols, output_cols, dag_id, task_id, previous_id, target_hierarchy_id, user_id, **kwargs):
    """
    Converts denormalized (pivoted) data into normalized form, similar to unpivoting or melting data.

    Args:
        group_by_cols (list): List of columns to group by (remain as-is)
        pivot_col (str): Name of the output column to contain the pivoted column names
        value_cols (list): List of columns to be normalized (unpivoted)
        output_cols (list): Names of output columns for the normalized data
        dag_id (str): DAG identifier
        task_id (str): Task identifier
        previous_id (str): Previous task identifier to pull data from
        target_hierarchy_id (str): Target hierarchy identifier
        user_id (str): User identifier
        sources (list): Source information
        **kwargs: Additional keyword arguments

    Returns:
        str: Name of the created output table
    """
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']
    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"

    # Get source table name
    source_table_name = ti.xcom_pull(task_ids=previous_id, key=previous_id)

    # Build UNION ALL queries for each value column to normalize using Query_generator
    union_queries = []

    for value_col in value_cols:
        # Create attributes for Query_generator
        source_attributes = [(col, 'string', f't."{col}"') for col in group_by_cols]
        pivot_attributes = [
            (pivot_col, 'string', f"'{value_col}'"),
            (output_cols[0], 'string', f't."{value_col}"')
        ]

        # Generate query for this value column
        from_clause = (source_table_name, 't')
        where_clause = f't."{value_col}" IS NOT NULL'

        generated_query = Query_generator(
            source_attributes=source_attributes,
            attributes=pivot_attributes,
            from_clause=from_clause,
            schema=schema,
            where_clause=where_clause
        )

        union_queries.append(generated_query)

    # Combine all queries with UNION ALL
    combined_query = " UNION ALL ".join(union_queries)

    # Create CTE
    cte = f""" "{task_id}" AS (
{combined_query}
)"""
    logger.info(f"[Normalizer Transformation] Generated query with Query_generator:\n{cte}")

    # Execute the combined query and create the target table
    with engine.begin() as conn1:
        conn1.execute(text(f"""
            CREATE TABLE "{schema}"."{target_table_name}" AS
            {combined_query}
        """))

    # Count records in result
    with engine.begin() as conn1:
        result = conn1.execute(text(f"""
            SELECT COUNT(*) FROM "{schema}"."{target_table_name}"
        """))
        total_count = result.fetchone()[0]

    logger.info(f"Normalizer transformation created table with {total_count} total records")

    # Store result table name in XCom
    ti.xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")

    return target_table_name



# previous_ids = ['task1', 'task2']
# column_mappings = [
#     ('name', ['full_name', 'username']),
#     ('email', ['email_address', 'email']),
#     ('age', ['age', None])
# ]
# remove_duplicates = False
# dag_id = "my_dag"
# task_id = "union_task"
# target_hierarchy_id = "target_001"
# user_id = "user_123"
# sources = ['source1', 'source2']

# ------------------------

# {
#         "type": "Union",
#         "id": "union_1",
#         "previous_ids": [
#           "SRC_Immybot",
#           "SRC_Hubspot"
#         ],
#         "column_mappings": [
#           ["id", ["id", "id"]],
#           ["user_id", ["user_id", "user_id"]]
#         ],
#         "remove_duplicates": false
#       },

# kwargs = {'ti': ti}

def Union(previous_ids, column_mappings, remove_duplicates, dag_id, task_id, target_hierarchy_id, user_id, **kwargs):
    """
    Combines data from multiple input sources into a single output, similar to Informatica Union transformation.

    Args:
        previous_ids (list): List of previous task IDs to pull data from
        column_mappings (list): List of output column mappings, where each mapping is:
                               [(output_column, [source1_column, source2_column, ...]), ...]
        remove_duplicates (bool): Whether to remove duplicate rows from the result
        dag_id (str): DAG identifier
        task_id (str): Task identifier
        target_hierarchy_id (str): Target hierarchy identifier
        user_id (str): User identifier
        sources (list): Source information
        **kwargs: Additional keyword arguments

    Returns:
        str: Name of the created output table
    """
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']
    unix_suffix = int(time.time())
    target_table_name = f"extracted_{task_id}_{unix_suffix}"

    # Get source table names
    source_tables = []
    for prev_id in previous_ids:
        table_name = ti.xcom_pull(task_ids=prev_id, key=prev_id)
        source_tables.append((table_name, prev_id))

    # Build UNION query for each source using Query_generator
    union_queries = []

    for idx, (source_table, prev_id) in enumerate(source_tables):
        # Build attributes for this source
        attributes = []

        for output_col, source_cols in column_mappings:
            if idx < len(source_cols) and source_cols[idx]:  # If this source has a mapping for this column
                attributes.append((output_col, 'string', f'"{source_cols[idx]}"'))
            else:
                # If no mapping exists, use NULL with appropriate casting
                attributes.append((output_col, 'string', 'NULL'))

        # Generate query for this source
        from_clause = (source_table, source_table)

        generated_query = Query_generator(
            attributes=attributes,
            from_clause=from_clause,
            schema=schema
        )

        union_queries.append(generated_query)

    # Combine all source queries with UNION or UNION ALL
    union_operator = 'UNION' if remove_duplicates else 'UNION ALL'
    combined_query = f" {union_operator} ".join(union_queries)

    # Create CTE
    cte = f""" "{task_id}" AS (
{combined_query}
)"""
    logger.info(f"[Union Transformation] Generated query with Query_generator:\n{cte}")

    # Execute the combined query and create the target table
    with engine.begin() as conn1:
        conn1.execute(text(f"""
            CREATE TABLE "{schema}"."{target_table_name}" AS
            {combined_query}
        """))

    # Count records in result
    with engine.begin() as conn1:
        result = conn1.execute(text(f"""
            SELECT COUNT(*) FROM "{schema}"."{target_table_name}"
        """))
        total_count = result.fetchone()[0]

    logger.info(f"Union transformation created table with {total_count} total records")

    # Store result table name in XCom
    ti.xcom_push(key=task_id, value=target_table_name)
    conn.sql("DETACH pg_db")

    return target_table_name


def UpdateStrategy(target_table, join_key, update_mappings, dag_id, task_id, previous_id, target_hierarchy_id, user_id, sources, strategy='UPDATE', **kwargs):
    """
    Updates data in target table based on source data and specified update strategies, similar to Informatica

    Args:
        target_table (str): Target table name
        join_key (list): List of key columns to join source and target tables
        update_mappings (list): Column update mapping list, each item contains (target_column, source_column, update_strategy)
                               update_strategy can be 'overwrite', 'add', 'subtract', 'min', 'max', 'concat', etc
        dag_id (str): DAG identifier
        task_id (str): Task identifier
        previous_id (str): Previous task identifier to pull source data from
        target_hierarchy_id (str): Target hierarchy identifier
        user_id (str): User identifier
        sources (list): Source information
        strategy (str): Main update strategy - 'UPDATE', 'INSERT', 'DELETE', 'UPSERT' or 'DD_UPDATE' (like Informatica)
        **kwargs: Additional keyword arguments

    Returns:
        str: Name of the updated table
    """
    conn = duckdb.connect(database=':memory:')
    engine_data = generate_engine(target_hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    conn_str = str(engine.url)

    conn.sql(f"ATTACH '{conn_str}' AS pg_db (TYPE POSTGRES, SCHEMA '{schema}');")

    ti = kwargs['ti']
    unix_suffix = int(time.time())
    temp_table_name = f"temp_update_{task_id}_{unix_suffix}"
    updated_table_name = f"updated_{task_id}_{unix_suffix}"

    # Get source table name
    source_table_name = ti.xcom_pull(task_ids=previous_id, key=previous_id)

    # Build join conditions
    join_conditions = []
    for key in join_key:
        join_conditions.append(f't."{key}" = s."{key}"')
    join_condition = " AND ".join(join_conditions)

    # Create a temporary table by copying target table structure and data
    with engine.begin() as conn1:
        conn1.execute(text(f"""
            CREATE TABLE "{schema}"."{temp_table_name}" AS
            SELECT * FROM "{schema}"."{target_table}";
        """))

    # Operations counters
    updated_count = 0
    inserted_count = 0
    deleted_count = 0

    # Execute different operations based on the main strategy
    if strategy.upper() == 'UPDATE' or strategy.upper() == 'UPSERT' or strategy.upper() == 'DD_UPDATE':
        # Build SET clauses for column-level update strategies
        set_clauses = []
        for target_col, source_col, update_type in update_mappings:
            if update_type.lower() == 'overwrite':
                set_clauses.append(f't."{target_col}" = s."{source_col}"')
            elif update_type.lower() == 'add':
                set_clauses.append(f't."{target_col}" = COALESCE(t."{target_col}", 0) + COALESCE(s."{source_col}", 0)')
            elif update_type.lower() == 'subtract':
                set_clauses.append(f't."{target_col}" = COALESCE(t."{target_col}", 0) - COALESCE(s."{source_col}", 0)')
            elif update_type.lower() == 'min':
                set_clauses.append(f't."{target_col}" = LEAST(COALESCE(t."{target_col}", s."{source_col}"), COALESCE(s."{source_col}", t."{target_col}"))')
            elif update_type.lower() == 'max':
                set_clauses.append(f't."{target_col}" = GREATEST(COALESCE(t."{target_col}", s."{source_col}"), COALESCE(s."{source_col}", t."{target_col}"))')
            elif update_type.lower() == 'concat':
                set_clauses.append(f't."{target_col}" = CONCAT(COALESCE(t."{target_col}", ''), COALESCE(s."{source_col}", ''))')
            else:
                # Default to overwrite
                set_clauses.append(f't."{target_col}" = s."{source_col}"')

        set_clause = ", ".join(set_clauses)

        # Generate a Query_generator query for the join part
        from_clause = (source_table_name, 's')
        join_list = [('INNER JOIN', f'"{schema}"."{temp_table_name}" t', join_condition)]

        # We'll use this for counting only, not for the actual update
        join_query = Query_generator(
            from_clause=from_clause,
            join_list=join_list,
            schema=schema
        )

        # Perform update for existing records with traditional SQL (UPDATE can't use Query_generator directly)
        update_query = f"""
            UPDATE "{schema}"."{temp_table_name}" t
            SET {set_clause}
            FROM "{schema}"."{source_table_name}" s
            WHERE {join_condition};
        """
        logger.info(f"[Update Strategy] Executing update query:\n{update_query}")

        with engine.begin() as conn1:
            conn1.execute(text(update_query))

        # Calculate number of updated records
        with engine.begin() as conn1:
            result = conn1.execute(text(f"""
                SELECT COUNT(*)
                FROM "{schema}"."{temp_table_name}" t
                JOIN "{schema}"."{source_table_name}" s
                ON {join_condition}
            """))
            updated_count = result.fetchone()[0]

        logger.info(f"Updated {updated_count} records in {target_table}")

    if strategy.upper() == 'INSERT' or strategy.upper() == 'UPSERT':
        # For INSERT or UPSERT, add new records that don't exist in target
        insert_columns = []
        insert_values = []

        for target_col, source_col, _ in update_mappings:
            insert_columns.append(f'"{target_col}"')
            insert_values.append(f's."{source_col}"')

        insert_columns_str = ", ".join(insert_columns)
        insert_values_str = ", ".join(insert_values)

        # Generate the NOT EXISTS condition using Query_generator
        source_attributes = [(f"s_{col}", "string", f's."{col}"') for col, _, _ in update_mappings]
        from_clause = (source_table_name, 's')

        # But we'll use traditional SQL for the actual insert operation
        insert_query = f"""
            INSERT INTO "{schema}"."{temp_table_name}" ({insert_columns_str})
            SELECT {insert_values_str}
            FROM "{schema}"."{source_table_name}" s
            WHERE NOT EXISTS (
                SELECT 1 FROM "{schema}"."{temp_table_name}" t
                WHERE {join_condition}
            );
        """
        logger.info(f"[Update Strategy] Executing insert query:\n{insert_query}")

        with engine.begin() as conn1:
            conn1.execute(text(insert_query))

        # Calculate number of inserted records
        with engine.begin() as conn1:
            result = conn1.execute(text(f"""
                SELECT COUNT(*)
                FROM "{schema}"."{source_table_name}" s
                WHERE NOT EXISTS (
                    SELECT 1 FROM "{schema}"."{target_table}" t
                    WHERE {join_condition}
                )
            """))
            inserted_count = result.fetchone()[0]

        logger.info(f"Inserted {inserted_count} new records into {target_table}")

    if strategy.upper() == 'DELETE' or strategy.upper() == 'DD_UPDATE':
        # Generate the NOT EXISTS condition using Query_generator
        target_attributes = [(f"t_{col}", "string", f't."{col}"') for col in join_key]
        from_clause = (temp_table_name, 't')

        # But we'll use traditional SQL for the actual delete operation
        delete_query = f"""
            DELETE FROM "{schema}"."{temp_table_name}" t
            WHERE NOT EXISTS (
                SELECT 1 FROM "{schema}"."{source_table_name}" s
                WHERE {join_condition}
            );
        """
        logger.info(f"[Update Strategy] Executing delete query:\n{delete_query}")

        with engine.begin() as conn1:
            conn1.execute(text(delete_query))

        # Calculate number of deleted records
        with engine.begin() as conn1:
            result = conn1.execute(text(f"""
                SELECT COUNT(*)
                FROM "{schema}"."{target_table}" t
                WHERE NOT EXISTS (
                    SELECT 1 FROM "{schema}"."{source_table_name}" s
                    WHERE {join_condition}
                )
            """))
            deleted_count = result.fetchone()[0]

        logger.info(f"Deleted {deleted_count} records from {target_table}")

    # Create a new table as the final result
    with engine.begin() as conn1:
        conn1.execute(text(f"""
            CREATE TABLE "{schema}"."{updated_table_name}" AS
            SELECT * FROM "{schema}"."{temp_table_name}";
        """))

    # Drop temporary table
    with engine.begin() as conn1:
        conn1.execute(text(f"""
            DROP TABLE IF EXISTS "{schema}"."{temp_table_name}";
        """))

    # Log summary of operations
    logger.info(f"Update Strategy Summary for {target_table}: Updated={updated_count}, Inserted={inserted_count}, Deleted={deleted_count}")

    # Store table name in XCom
    ti.xcom_push(key=task_id, value=updated_table_name)
    conn.sql("DETACH pg_db")

    return updated_table_name



# {
#       "type": "Router",
#       "id": "router_1",
#       "previous_id": "SRC_Customers",
#       "conditions": [
#         ["country = 'USA'", "US_Customers"],
#         ["country != 'USA'", "NonUS_Customers"]
#       ]
#     }

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
        generated_query = Query_generator(from_clause=from_clause, where_clause=condition)

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

        # Store the output table name
        result_tables[output_name] = output_table_name

        # Push to XCom for each output path
        ti.xcom_push(key=f"{task_id}_{output_name}", value=output_table_name)

    # Store the routing map in XCom
    ti.xcom_push(key=task_id, value=result_tables)
    conn.sql("DETACH pg_db")

    return result_tables



