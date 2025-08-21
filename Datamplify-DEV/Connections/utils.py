from Service.utils import decode_value 
from sqlalchemy import create_engine
from urllib.parse import quote
from pathlib import Path
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from pymongo import MongoClient
from Connections import models as conn_models
from sqlalchemy import text
import pyodbc,os






def fetch_filename_extension(file_name):
    try:
        file_name, file_extension = os.path.splitext(file_name.name)
    except:
        server_path = Path(str(file_name)) 
        file_name, file_extension = server_path.stem, server_path.suffix
    return file_name, file_extension


def cassandra_db(cluster):
    try:
        session = cluster.connect()
        # print("Connected to cluster:", cluster.metadata.cluster_name)
        cluster.shutdown()
        data = {
            "status":200,
            "engine":None,
            "cursor":None
        }
        return data
    except Exception as e:
        data={
            "status":400,
            "message" : f"{str(e)}"
        }
        return data
    
def server_path_function(server_path,parameter):
    if server_path==None or server_path=='':
        data = {
            "status":406,
            "message":"database_path is mandatory"
        }
        return data
    else:
        if parameter=="MICROSOFTACCESS":
            # database_path = r'C:\path\to\your\database.accdb'
            url = f'access+pyodbc:///?Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={str(server_path)}'
        elif parameter=="SQLITE":
            # database_path = 'path/to/your/database.db'
            # url = f'sqlite:///{str(server_path)}'
            file_name, file_extension = fetch_filename_extension(server_path)
            if file_extension =='.db' or file_extension=='.sqlite' or file_extension=='.sqlite3' or file_extension=='':
                pass
            else:
                data = {
                    "status":406,
                    "message":"not acceptable/invalid file"
                }
                return data
            try:
                BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust BASE_DIR as needed
                db_file_path = os.path.join(BASE_DIR, str(server_path))
                url = f'sqlite:///{db_file_path}'
            except:
                # database_path = 'path/to/your/database.db'
                url = f'sqlite:///{str(server_path)}'
        data = {
            "status":200,
            "url":url
        }
        return data



def mongo_db(username, password, database, hostname, port):
    try:
        if (username=='' or username==None) and (password =='' or password==None):
            client = MongoClient(hostname, int(port))
        else:
            connection_string = f'mongodb://{username}:{password}@{hostname}:{int(port)}/{database}'
            client = MongoClient(connection_string)
        
        db = client[database]
        data = {
            "status":200,
            "engine":db,
            "cursor":None
        }
        return data
    except Exception as e:
        data={
            "status":400,
            "message" : f"{str(e)}"
        }
        return data

def server_connection(username, password, database, hostname,port,service_name,parameter,server_path):
    try:
        password1234=decode_value(password)
    except:
        pass
    match str(parameter).upper():
        case "POSTGRESQL":
            url = "postgresql://{}:{}@{}:{}/{}".format(username,password1234,hostname,port,database)
        case "ORACLE":
            url = 'oracle+cx_oracle://{}:{}@{}:{}/{}'.format(username,password1234,hostname,port,service_name)
        case "MYSQL":
            url = f'mysql+mysqlconnector://{username}:{password1234}@{hostname}:{port}/{database}'
        case "SNOWFLAKE":
            encoded_password = quote(password1234)
            url = f'snowflake://{username}:{encoded_password}@{hostname}/{database}?port={port}'
        case "IBMDB2":
            url = f'ibm_db_sa://{username}:{password1234}@{hostname}:{port}/{database}'
        case "MICROSOFTSQLSERVER":
            driver='ODBC Driver 17 for SQL Server'
            # connection_string = f'DRIVER={driver};SERVER={hostname};DATABASE={database};Trusted_Connection=yes;' 
            if (username and password1234 == None) or (username and password1234 == '') or (username and password1234 == ""):
                connection_string = f'DRIVER={{{driver}}};SERVER={hostname};DATABASE={database};Trusted_Connection=yes;' #;UID={username};PWD={password1234}
            else:
                connection_string = f'DRIVER={{{driver}}};SERVER={hostname};DATABASE={database};UID={username};PWD={password1234}'  #;Trusted_Connection=yes;
            conn = pyodbc.connect(connection_string)
        case "MICROSOFTACCESS":
            sq_msacces=server_path_function(server_path,parameter)
            if sq_msacces['status']==200:
                url = sq_msacces['url']
            else:
                return sq_msacces
        case "SQLITE":
            sq_msacces=server_path_function(server_path,parameter)
            if sq_msacces['status']==200:
                url = sq_msacces['url']
            else:
                return sq_msacces
        case "SYBASE":
            url = f'sybase+pyodbc://{username}:{password1234}@{hostname}:{port}/{database}'
        case "MONGODB":
            mongo=mongo_db(username, password, database, hostname,port)
            return mongo
        case "CASSANDRA":
            auth_provider = PlainTextAuthProvider(username=username, password=password1234)
            cluster = Cluster([hostname], port=port, auth_provider=auth_provider)
            cassandra = cassandra_db(cluster)
            return cassandra
        case "SAP HANA":
            connection_string = f"hana+hdbcli://{username}:{password1234}@{hostname}:{port}/{database}"
        case "SAP BW":
            connection_string = f"hana+hdbcli://{username}:{password1234}@{hostname}:{port}/{database}"
            
        # engine = create_engine(url, echo=True)
        case "MICROSOFTSQLSERVER": 
            if int(port)==1433:
                engine = conn
                cursor = conn.cursor()
            else:
                data={
                    "status":400,
                    "message":"Invalid port"
                }
                return data
    engine = create_engine(url)
    cursor = engine.connect()

    data={
        "status":200,
        "engine":engine,
        "cursor":cursor
    }
    return data




def generate_engine(id,user_id):
        conn_table_id = conn_models.Connections.objects.get(id=id,user_id = user_id).table_id
        database_details = conn_models.DatabaseConnections.objects.get(id=conn_table_id)
        server_type = conn_models.DataSources.objects.get(id=database_details.server_type.id).name
        data = server_connection(database_details.username,database_details.password,database_details.database,database_details.hostname,
                                 database_details.port,database_details.service_name,server_type,database_details.database_path)
        data['schema'] = database_details.schema
        return data
        # if server_type.lower() =='postgresql':

        #      postgres_url = f"postgresql://{database_details.username}:{password}@{database_details.hostname}:{database_details.port}/{database_details.database}?options=-csearch_path%3D{database_details.schema}"
        # else:
        #      return 'Unspported Database'
        # engine = create_engine(postgres_url)
        # return {"engine":engine,
        #         "schema":database_details.schema}

                


def get_table_details(database_type,cursor,schema='public'):
    match database_type.lower():
        case 'mysql':
            cursor_data = cursor.execute(text("""SELECT
                    TABLE_NAME,
                    GROUP_CONCAT(CONCAT(COLUMN_NAME, ':', DATA_TYPE) ORDER BY ORDINAL_POSITION) AS columns
                FROM
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_SCHEMA = DATABASE()  -- Or specify a specific database name
                GROUP BY
                    TABLE_NAME
                ORDER BY
                    TABLE_NAME;"""))

        case 'oracle':
            cursor_data = cursor.execute(text("""SELECT
                    TABLE_NAME,
                    LISTAGG(COLUMN_NAME || ':' || DATA_TYPE, ', ') WITHIN GROUP (ORDER BY COLUMN_ID) AS columns
                FROM
                    ALL_TAB_COLUMNS
                WHERE
                    OWNER = USER
                GROUP BY
                    TABLE_NAME
                ORDER BY
                    TABLE_NAME"""))

        case 'snowflake':
            cursor_data = cursor.execute(text("""SELECT
                    TABLE_NAME,
                    LISTAGG(COLUMN_NAME || ':' || DATA_TYPE, ', ') WITHIN GROUP (ORDER BY ORDINAL_POSITION) AS columns
                FROM
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_SCHEMA = CURRENT_DATABASE()  -- Or specify a schema/database
                    AND TABLE_CATALOG = CURRENT_SCHEMA()
                GROUP BY
                    TABLE_NAME
                ORDER BY
                    TABLE_NAME;"""))

        case 'sqlite':
            try:
                cursor_data = cursor.execute(text("""SELECT
                        m.name AS table_name,
                        GROUP_CONCAT(p.name || ':' || p.type, ', ') AS columns
                    FROM sqlite_master AS m
                    JOIN pragma_table_info(m.name) AS p
                    GROUP BY m.name
                    ORDER BY m.name;"""))
            except Exception as e:
                print(e)

        case 'microsoftsqlserver':
            cursor_data = cursor.execute("""SELECT
                t.name AS table_name,
                STRING_AGG(c.name + ':' + TYPE_NAME(c.user_type_id), ', ') WITHIN GROUP (ORDER BY c.column_id) AS columns
            FROM sys.tables AS t
            INNER JOIN sys.columns AS c ON t.object_id = c.object_id
            INNER JOIN sys.schemas AS s ON t.schema_id = s.schema_id
            WHERE s.name = 'dbo'  -- Or specify the schema name
            GROUP BY t.name
            ORDER BY t.name;""")

        case 'postgresql':
            cursor_data = cursor.execute(text(f"""SELECT 
                    table_name, 
                    STRING_AGG(column_name || ':' || data_type, ',' ORDER BY ordinal_position) AS columns 
                FROM information_schema.columns 
                WHERE table_schema = '{schema}' 
                GROUP BY table_name 
                ORDER BY table_name;"""))

        case 'mariadb':
            cursor_data = cursor.execute(text("""SELECT
                    TABLE_NAME,
                    GROUP_CONCAT(CONCAT(COLUMN_NAME, ':', DATA_TYPE) ORDER BY ORDINAL_POSITION) AS columns
                FROM
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_SCHEMA = DATABASE()  -- Or specify a specific database name
                GROUP BY
                    TABLE_NAME
                ORDER BY
                    TABLE_NAME;"""))

        case 'db2':
            cursor_data = cursor.execute(text("""SELECT
                    TABNAME AS table_name,
                    LISTAGG(COLNAME || ':' || TYPENAME, ', ') WITHIN GROUP (ORDER BY COLNO) AS columns
                FROM SYSCAT.COLUMNS
                WHERE TABSCHEMA = CURRENT SCHEMA
                GROUP BY TABNAME
                ORDER BY TABNAME;"""))

        case _:
            raise ValueError(f"Unsupported database type: {database_type}")
    tables = []
    for row in cursor_data.fetchall():
        table_name = row[0]  # Get the table name
        column_string = row[1]  # Get the comma-separated string of column::datatype
        column_list = column_string.split(',')  # Split into a list

        # Process each column and extract name + data type
        columns = [{"col": col.split(":")[0].strip(), "dtype": col.split(":")[1].strip()} for col in column_list]

        # Append structured data to the list
        table_data = {"tables": table_name, "columns": columns}
        tables.append(table_data)

    return tables