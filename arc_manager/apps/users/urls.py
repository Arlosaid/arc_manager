from django.urls import path
from .views import UserListView, SimpleUserCreateView, UserEditView, UserDetailView, UserDeleteAjaxView

app_name = 'users'

urlpatterns = [
    # URLs principales de usuarios
    path('', UserListView.as_view(), name='user_list'),
    path('create/', SimpleUserCreateView.as_view(), name='create'),
    path('<int:pk>/', UserDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', UserEditView.as_view(), name='edit'),

    path('<int:pk>/delete-ajax/', UserDeleteAjaxView.as_view(), name='delete_ajax'),
] 