from django.urls import path
from research.views.queries import generate_search_queries
from research.views.selection import select_source
from research.views.fetch import fetch_source_data
from research.views.finalize import finalize_research

urlpatterns = [
    path('api/v1/ai/research/<int:content_id>/generate-queries/', generate_search_queries, name='generate_search_queries'),
    path('api/v1/ai/research/source/<int:source_id>/select/', select_source, name='select_research_source'),
    path('api/v1/ai/research/source/<int:source_id>/fetch/', fetch_source_data, name='fetch_research_source_data'),
    path('api/v1/ai/research/<int:content_id>/finalize/', finalize_research, name='finalize_research'),
]
