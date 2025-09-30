
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import AllowAny
from .models import CustomUser, Task


# ---------------- AUTH ---------------- #

class LoginView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/login.html"

    def get(self, request):
        return Response({})

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials or insufficient permissions")
            return Response({}, template_name="tasks/login.html")


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return redirect("login")


# ---------------- DASHBOARD ---------------- #

class DashboardView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/dashboard.html"

    def get(self, request):
        user = request.user
        context = {}

        if user.role == "superadmin":
            context["total_admins"] = CustomUser.objects.filter(role="admin").count()
            context["total_users"] = CustomUser.objects.filter(role="user").count()
            context["total_tasks"] = Task.objects.count()
            context["completed_tasks"] = Task.objects.filter(status="completed").count()
            context["all_tasks"] = Task.objects.all()
        elif user.role == "admin":
            context["total_users"] = CustomUser.objects.filter(assigned_admin=user).count()
            context["total_tasks"] = Task.objects.filter(
                assigned_to__assigned_admin=user
            ).count()
            context["completed_tasks"] = Task.objects.filter(
                assigned_to__assigned_admin=user, status="completed"
            ).count()
            context["all_tasks"] = Task.objects.filter(assigned_to__assigned_admin=user)
        else:
            context["total_tasks"] = Task.objects.filter(assigned_to=user).count()
            context["completed_tasks"] = Task.objects.filter(
                assigned_to=user, status="completed"
            ).count()
            context["all_tasks"] = Task.objects.filter(assigned_to=user)

        return Response(context)


# ---------------- USER MANAGEMENT (superadmin only) ---------------- #

class UserListView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/user_list.html"

    def get(self, request):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")
        users = CustomUser.objects.filter(role="user")
        return Response({"users": users})


class UserCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/user_form.html"

    def get(self, request):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")
        admins = CustomUser.objects.filter(role="admin")
        return Response({"admins": admins})

    def post(self, request):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")

        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        admin_id = request.data.get("assigned_admin")

        try:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role="user",
            )
            if admin_id:
                user.assigned_admin_id = admin_id
                user.save()
            messages.success(request, "User created successfully")
            return redirect("user_list")
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return Response({}, template_name="tasks/user_form.html")


class UserDeleteView(APIView):

    def get(self, request, pk):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")

        user = get_object_or_404(CustomUser, pk=pk, role="user")
        user.delete()
        messages.success(request, "User deleted successfully")
        return redirect("user_list")


# ---------------- ADMIN MANAGEMENT ---------------- #

class AdminListView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/admin_list.html"

    def get(self, request):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")
        admins = CustomUser.objects.filter(role="admin")
        return Response({"admins": admins})


class AdminCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/admin_form.html"

    def get(self, request):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")
        return Response({})

    def post(self, request):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")

        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        try:
            CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role="admin",
            )
            messages.success(request, "Admin created successfully")
            return redirect("admin_list")
        except Exception as e:
            messages.error(request, f"Error creating admin: {str(e)}")
            return Response({}, template_name="tasks/admin_form.html")


class AdminDeleteView(APIView):

    def get(self, request, pk):
        if request.user.role != "superadmin":
            messages.error(request, "Access denied")
            return redirect("dashboard")

        admin = get_object_or_404(CustomUser, pk=pk, role="admin")
        admin.delete()
        messages.success(request, "Admin deleted successfully")
        return redirect("admin_list")


# ---------------- TASK MANAGEMENT ---------------- #

class TaskListView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/task_list.html"

    def get(self, request):
        if request.user.role == "superadmin":
            tasks = Task.objects.all()
        elif request.user.role == "admin":
            tasks = Task.objects.filter(assigned_to__assigned_admin=request.user)
        else:
            tasks = Task.objects.filter(assigned_to=request.user)

        return Response({"tasks": tasks})


class TaskCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/task_form.html"

    def get(self, request):
        if request.user.role not in ["admin"]:
            messages.error(request, "Access denied")
            return redirect("dashboard")

        if request.user.role == "superadmin":
            users = CustomUser.objects.filter(role="user")
        else:  
            users = CustomUser.objects.filter(assigned_admin=request.user, role="user")

        return Response({"users": users})

    def post(self, request):
        if request.user.role not in ["admin"]:
            messages.error(request, "Access denied")
            return redirect("dashboard")

        title = request.data.get("title")
        description = request.data.get("description")
        assigned_to_id = request.data.get("assigned_to")
        due_date = request.data.get("due_date")

        try:
            Task.objects.create(
                title=title,
                description=description,
                assigned_to_id=assigned_to_id,
                created_by=request.user,
                created_at = datetime.now(),
                due_date=due_date,
            )
            messages.success(request, "Task created successfully")
            return redirect("task_list")
        except Exception as e:
            messages.error(request, f"Error creating task: {str(e)}")
            return Response({}, template_name="tasks/task_form.html")


class TaskReportView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/task_reports.html"

    def get(self, request):
        if request.user.role == "superadmin":
            tasks = Task.objects.filter(status="completed")
        elif request.user.role == "admin":
            tasks = Task.objects.filter(
                assigned_to__assigned_admin=request.user, status="completed"
            )
        else:
            tasks = Task.objects.filter(assigned_to=request.user, status="completed")

        return Response({"tasks": tasks})


# ---------------- USER TASK ---------------- #

class UserTaskListView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/user_task_list.html"

    def get(self, request):
        if request.user.role != "user":
            messages.error(request, "Access denied")
            return redirect("dashboard")
        tasks = Task.objects.filter(assigned_to=request.user)
        return Response({"tasks": tasks})


class TaskUpdateView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "tasks/task_update.html"

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
        return Response({"task": task})

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

        worked_hours = request.data.get("worked_hours")
        completion_report = request.data.get("completion_report")
        
        if not all([worked_hours or task.report]):
            messages.error(request, "worked hours and report is missing")

        
        task.worked_hours = worked_hours
        task.completion_report = completion_report
        task.status = "completed"
        task.save()
        
        messages.success(request, "Task updated successfully")
        return redirect("user_task_list_view")
