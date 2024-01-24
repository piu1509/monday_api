from django.urls import path
from modules.api import views
from django.views.generic.base import TemplateView

app_name = 'api'

urlpatterns = [
	path('', TemplateView.as_view(template_name='home.html'), name='home'),
	path('monday_redirect/',views.redirectMondayView.as_view(), name='redirect_monday'),
	path('logout/', views.Logout.as_view(), name='logout'),
	path('item_list/', views.ListItems.as_view(), name='item_list'),
	path('create_item/', views.CreateItem.as_view(), name='create_item'),
	
	path('item_create/', views.ItemCreate.as_view(), name='item_create'),
	path('create_subitem/', views.SubitemCreate.as_view(), name='create_subitem'),
	path('update_item/<int:id>', views.ItemUpdate.as_view(), name='update_item'),
	path('delete_item/<int:id>', views.ItemDelete.as_view(), name='delete_item'),
]