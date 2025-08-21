from django.urls import path 
from Connections.views import (Server_Connection,Server_Connection_update,get_available_schemas,
    File_Connection,File_operations,Connection_list,ETL_connection_list,Server_tables,FileSchema,ServerFileSchemaView,ListFilesView)
urlpatterns = [
    path('Database_connection/',Server_Connection.as_view(),name= 'Database Server Connection'), #post
    path('Database_connection/<id>',Server_Connection_update.as_view(),name = 'Connection Update'), #update
    path('get_schema/',get_available_schemas,name='get postgres schmea'),
    path('File_connection/',File_Connection.as_view(),name='File Source'),
    path('File_connection/<id>',File_operations.as_view(),name='file put,update,delete'),
    path('Connection_list/',Connection_list.as_view(),name = 'Connections List'),
    path('ETL_connection_list/',ETL_connection_list.as_view(),name='type wise connections'),
    path('Server_tables/<id>/',Server_tables.as_view(),name='get connected database tables'),
    path('file_schema/<id>/',FileSchema.as_view(),name='file columns'),
    path('server_files/',ServerFileSchemaView.as_view(),name='get columns from server files'),
    path('ListFiles/',ListFilesView.as_view(),name='server_files_list')


]
