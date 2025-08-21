from django.urls import path 
from Monitor.views import Trigger_dag,DataFlow_status,Dataflow_Task_status,airflow_token_api,DashboardStatsAPIView

urlpatterns = [
path('airflow_token/', airflow_token_api, name='airflow_token_api'),
path('Trigger/<id>',Trigger_dag.as_view(),name = 'Trigger'), 
path('status/',DataFlow_status.as_view(),name='Flow status'), 
path('task_status/',Dataflow_Task_status.as_view(),name='Task status'),

path('Home',DashboardStatsAPIView.as_view(),name='Home Dashboard')


]
