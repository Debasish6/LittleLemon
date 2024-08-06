from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name="about"),
    path('menu/', views.menu, name="menu"),
    path('book/', views.book, name="book"),
    path('bookings', views.bookings, name="bookings"),
    path('menu-items',views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>',views.SingleMenuItemView.as_view()),
    path('groups/manager/users',views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>',views.RemoveManager.as_view()),
    path('groups/delivery-crew/users',views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>',views.RemoveDeliveryCrew.as_view()),
    path('cart/menu-items',views.Cart_items_views.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.OrderItemView.as_view()), 
    path('category',views.CategoriesView.as_view()),
    path('obtain-auth-token/',obtain_auth_token),
]