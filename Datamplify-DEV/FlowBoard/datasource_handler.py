"""
Datasource Handler - Supports all 22 datasources for FlowBoard transformations
"""
import pandas as pd
from Connections.models import Connections, DatabaseConnections, FileConnections, DataSources
from Connections.utils import generate_engine


class DatasourceHandler:
    """
    Handles reading/writing for all 22 datasources
    """
    
    @staticmethod
    def get_connection_info(connection_id, user_id):
        """
        Get connection details for any datasource type
        """
        try:
            conn = Connections.objects.get(id=connection_id, user_id=user_id)
            datasource_type = conn.type.name.upper()
            
            # Database connections
            if conn.type.type == 'DATABASE':
                db_conn = DatabaseConnections.objects.get(id=conn.table_id)
                engine_data = generate_engine(connection_id, user_id)
                
                return {
                    'type': 'database',
                    'datasource': datasource_type,
                    'engine': engine_data.get('engine'),
                    'cursor': engine_data.get('cursor'),
                    'schema': engine_data.get('schema', 'public'),
                    'connection_details': {
                        'hostname': db_conn.hostname,
                        'port': db_conn.port,
                        'database': db_conn.database,
                        'username': db_conn.username,
                    }
                }
            
            # File connections
            elif conn.type.type == 'FILE':
                file_conn = FileConnections.objects.get(id=conn.table_id)
                
                return {
                    'type': 'file',
                    'datasource': datasource_type,
                    'file_path': file_conn.datapath.path if file_conn.datapath else file_conn.source,
                    'file_type': datasource_type,
                }
            
        except Exception as e:
            raise Exception(f"Error getting datasource connection: {str(e)}")
    
    
    @staticmethod
    def generate_read_code(node, connection_id, user_id):
        """
        Generate Python code to read from any datasource
        """
        conn_info = DatasourceHandler.get_connection_info(connection_id, user_id)
        
        if conn_info['type'] == 'database':
            return DatasourceHandler._generate_database_read(node, conn_info, connection_id)
        elif conn_info['type'] == 'file':
            return DatasourceHandler._generate_file_read(node, conn_info)
    
    
    @staticmethod
    def _generate_database_read(node, conn_info, connection_id):
        """
        Generate pandas read for database sources
        """
        datasource = conn_info['datasource']
        table_name = node.get('tableName', '')
        node_id = node.get('id', '')
        
        # MongoDB - uses PyMongo
        if datasource == 'MONGODB':
            return f"""
# Read from MongoDB
from pymongo import MongoClient
client = MongoClient('{conn_info['connection_details']['hostname']}', {conn_info['connection_details']['port']})
db = client['{conn_info['connection_details']['database']}']
collection = db['{table_name}']
df_{node_id} = pd.DataFrame(list(collection.find()))
if '_id' in df_{node_id}.columns:
    df_{node_id} = df_{node_id}.drop('_id', axis=1)
"""
        
        # Cassandra - uses cassandra-driver
        elif datasource == 'CASSANDRA':
            return f"""
# Read from Cassandra
from cassandra.cluster import Cluster
cluster = Cluster(['{conn_info['connection_details']['hostname']}'])
session = cluster.connect('{conn_info['connection_details']['database']}')
rows = session.execute("SELECT * FROM {table_name}")
df_{node_id} = pd.DataFrame(list(rows))
cluster.shutdown()
"""
        
        # All SQL databases (PostgreSQL, MySQL, Oracle, SQL Server, etc.)
        else:
            sql = f"SELECT * FROM {table_name}"
            return f"""
# Read from {datasource}
df_{node_id} = pd.read_sql(
    "{sql}",
    con=engine_{connection_id}
)
"""
    
    
    @staticmethod
    def _generate_file_read(node, conn_info):
        """
        Generate pandas read for file sources
        """
        file_type = conn_info['file_type']
        file_path = conn_info['file_path']
        node_id = node.get('id', '')
        
        if file_type == 'CSV':
            return f"""
# Read CSV file
df_{node_id} = pd.read_csv('{file_path}')
"""
        
        elif file_type == 'EXCEL':
            return f"""
# Read Excel file
df_{node_id} = pd.read_excel('{file_path}')
"""
        
        elif file_type == 'JSON':
            return f"""
# Read JSON file
df_{node_id} = pd.read_json('{file_path}')
"""
        
        elif file_type == 'XML':
            return f"""
# Read XML file
df_{node_id} = pd.read_xml('{file_path}')
"""
        
        elif file_type == 'PARQUET':
            return f"""
# Read Parquet file
df_{node_id} = pd.read_parquet('{file_path}')
"""
        
        elif file_type == 'AVRO':
            return f"""
# Read Avro file
import fastavro
with open('{file_path}', 'rb') as f:
    reader = fastavro.reader(f)
    df_{node_id} = pd.DataFrame(list(reader))
"""
        
        elif file_type == 'ORC':
            return f"""
# Read ORC file
df_{node_id} = pd.read_orc('{file_path}')
"""
        
        elif file_type == 'TXT':
            return f"""
# Read TXT file (tab-delimited)
df_{node_id} = pd.read_csv('{file_path}', delimiter='\\t')
"""
        
        else:
            raise Exception(f"Unsupported file type: {file_type}")
    
    
    @staticmethod
    def generate_write_code(node, connection_id, user_id, df_name):
        """
        Generate Python code to write to any datasource
        """
        conn_info = DatasourceHandler.get_connection_info(connection_id, user_id)
        
        if conn_info['type'] == 'database':
            return DatasourceHandler._generate_database_write(node, conn_info, df_name, connection_id)
        elif conn_info['type'] == 'file':
            return DatasourceHandler._generate_file_write(node, conn_info, df_name)
    
    
    @staticmethod
    def _generate_database_write(node, conn_info, df_name, connection_id):
        """
        Generate pandas write for database targets
        """
        datasource = conn_info['datasource']
        table_name = node.get('tableName', '')
        
        # MongoDB - uses PyMongo
        if datasource == 'MONGODB':
            return f"""
# Write to MongoDB
from pymongo import MongoClient
client = MongoClient('{conn_info['connection_details']['hostname']}', {conn_info['connection_details']['port']})
db = client['{conn_info['connection_details']['database']}']
collection = db['{table_name}']
records = {df_name}.to_dict('records')
collection.delete_many({{}})  # Clear existing data
collection.insert_many(records)
client.close()
"""
        
        # Cassandra - uses cassandra-driver
        elif datasource == 'CASSANDRA':
            return f"""
# Write to Cassandra
from cassandra.cluster import Cluster
cluster = Cluster(['{conn_info['connection_details']['hostname']}'])
session = cluster.connect('{conn_info['connection_details']['database']}')
# Truncate table
session.execute("TRUNCATE {table_name}")
# Insert records
for _, row in {df_name}.iterrows():
    columns = ', '.join(row.index)
    values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in row.values])
    session.execute(f"INSERT INTO {table_name} ({{columns}}) VALUES ({{values}})")
cluster.shutdown()
"""
        
        # All SQL databases
        else:
            return f"""
# Write to {datasource}
{df_name}.to_sql(
    '{table_name}',
    con=engine_{connection_id},
    if_exists='replace',
    index=False
)
"""
    
    
    @staticmethod
    def _generate_file_write(node, conn_info, df_name):
        """
        Generate pandas write for file targets
        """
        file_type = conn_info['file_type']
        file_path = node.get('outputPath', '/tmp/output')
        
        if file_type == 'CSV':
            return f"""
# Write to CSV
{df_name}.to_csv('{file_path}', index=False)
"""
        
        elif file_type == 'EXCEL':
            return f"""
# Write to Excel
{df_name}.to_excel('{file_path}', index=False, engine='openpyxl')
"""
        
        elif file_type == 'JSON':
            return f"""
# Write to JSON
{df_name}.to_json('{file_path}', orient='records', indent=2)
"""
        
        elif file_type == 'PARQUET':
            return f"""
# Write to Parquet
{df_name}.to_parquet('{file_path}', index=False)
"""
        
        elif file_type == 'AVRO':
            return f"""
# Write to Avro
import fastavro
schema = {{
    'type': 'record',
    'name': 'output',
    'fields': [
        {{'name': col, 'type': ['null', 'string']}} for col in {df_name}.columns
    ]
}}
with open('{file_path}', 'wb') as f:
    fastavro.writer(f, schema, {df_name}.to_dict('records'))
"""
        
        elif file_type == 'ORC':
            return f"""
# Write to ORC
{df_name}.to_orc('{file_path}', index=False)
"""
        
        else:
            return f"""
# Write to TXT (tab-delimited)
{df_name}.to_csv('{file_path}', sep='\\t', index=False)
"""
