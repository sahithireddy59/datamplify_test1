from django.urls import path
from FlowBoard.views import FlowBoard,FlowOperation,Flow_List


urlpatterns = [
    path('flow/',FlowBoard.as_view(),name= 'save_flow'), #post,put
    path('flow/<id>',FlowOperation.as_view(),name = 'get flow'),  #get ,Delete
    path('list/',Flow_List.as_view(),name='Flow List')
    ]
