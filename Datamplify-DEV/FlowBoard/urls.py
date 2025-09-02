from django.urls import path
from FlowBoard.views import FlowBoard, FlowOperation, Flow_List, FlowRun

urlpatterns = [
    path('flow/', FlowBoard.as_view(), name='save_flow'),  # post, put
    path('flow/<id>', FlowOperation.as_view(), name='get_flow'),  # get, delete
    path('list/', Flow_List.as_view(), name='flow_list'),
    path('run/<id>', FlowRun.as_view(), name='run_flow')
]
