from django.urls import path
from FlowBoard.views import FlowBoard, FlowOperation, Flow_List, FlowRun, MappingSuggest
from FlowBoard.mapping_views import MappingGenerator, APIKeyManager

urlpatterns = [
    # Existing FlowBoard endpoints
    path('flow/', FlowBoard.as_view(), name='save_flow'),  # post, put
    path('flow/<id>', FlowOperation.as_view(), name='get_flow'),  # get, delete
    path('list/', Flow_List.as_view(), name='flow_list'),
    path('run/<id>', FlowRun.as_view(), name='run_flow'),
    
    # AI Mapping endpoints
    path('ai/mapping/suggest', MappingSuggest.as_view(), name='ai_mapping_suggest'),
    
    # API Key-based Mapping endpoints
    path('api/mapping/generate', MappingGenerator.as_view(), name='api_mapping_generate'),
    path('api/keys', APIKeyManager.as_view(), name='api_keys_manage'),
    path('api/keys/<str:key_id>', APIKeyManager.as_view(), name='api_key_manage'),
]
