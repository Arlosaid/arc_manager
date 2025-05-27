from django.urls import path
from .views import UserListView, SimpleCreateUserView, UserEditView, UserDetailView

app_name = 'users'

urlpatterns = [
    # URLs principales de usuarios
    path('', UserListView.as_view(), name='list'),
    path('create/', SimpleCreateUserView.as_view(), name='create'),
    path('<int:pk>/', UserDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', UserEditView.as_view(), name='edit'),
] 