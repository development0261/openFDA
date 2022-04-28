from django.urls import path
from app.views import fetchdata,index,pagination,download

urlpatterns = [
    path('', index, name="index"),
    path('fetchdata/', fetchdata, name="fetchdata"),
    path('pagination/', pagination, name="pagination"),
    path('download/', download, name="download"),
]
