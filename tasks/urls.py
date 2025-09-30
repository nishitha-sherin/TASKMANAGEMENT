
from django.urls import path
from .views import (
    LoginView, LogoutView, DashboardView,
    UserListView, UserCreateView, UserDeleteView,
    AdminListView, AdminCreateView, AdminDeleteView,
    TaskListView, TaskCreateView, TaskReportView,
    UserTaskListView, TaskUpdateView
)

urlpatterns = [
    # Authentication
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # User Management 
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),

    # Admin Management 
    path("admins/", AdminListView.as_view(), name="admin_list"),
    path("admins/create/", AdminCreateView.as_view(), name="admin_create"),
    path("admins/<int:pk>/delete/", AdminDeleteView.as_view(), name="admin_delete"),

    # Task Management
    path("tasks/", TaskListView.as_view(), name="task_list_view"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create_view"),
    path("tasks/reports/", TaskReportView.as_view(), name="task_report_view"),

    # User-specific Task Views
    path("user/tasks/", UserTaskListView.as_view(), name="user_task_list_view"),
    path("tasks/update/<int:task_id>", TaskUpdateView.as_view(), name="task_update_view"),
]
