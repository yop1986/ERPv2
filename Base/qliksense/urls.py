from django.urls import path, re_path, include

from . import views

app_name = 'qliksense'

urlpatterns = [
	path('inicio/', views.QlikSense.as_view(), name='index'),
	path('inicio/carga_masiva/', views.QlikCargaMasiva.as_view(), name='carga_masiva'),

	path('streams/', views.StreamList.as_view(), name='list_stream'),
	path('streams/create/', views.StreamCreate.as_view(), name='add_stream'),
	path('streams/update/<uuid:pk>/', views.StreamUpdate.as_view(), name='change_stream'),
	path('streams/detail/<uuid:pk>/', views.StreamDetail.as_view(), name='view_stream'),
	path('streams/detail/<uuid:pk>/<str:opt>/', views.StreamDetail.as_view(), name='view_stream'),
	path('streams/delete/<uuid:pk>/', views.StreamDelete.as_view(), name='delete_stream'),

	path('modelos/', views.ModeloList.as_view(), name='list_modelo'),
	path('modelos/<str:opt>/', views.ModeloList.as_view(), name='list_modelo'),
	path('modelos/create/', views.ModeloCreate.as_view(), name='add_modelo'),
	path('modelos/create/<uuid:stream>/', views.ModeloCreate.as_view(), name='add_modelo'),
	path('modelos/update/<uuid:pk>/', views.ModeloUpdate.as_view(), name='change_modelo'),
	path('modelos/detail/<uuid:pk>/', views.ModeloDetail.as_view(), name='view_modelo'),
	path('modelos/detail/<uuid:pk>/<str:opt>/', views.ModeloDetail.as_view(), name='view_modelo'),
	path('modelos/delete/<uuid:pk>/', views.ModeloDelete.as_view(), name='delete_modelo'),
]

