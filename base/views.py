# Login / Logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

# Register an user
from django.shortcuts import redirect
from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Allow user to access a page only if is authenticated
from django.contrib.auth.mixins import LoginRequiredMixin

# CRUD / Model
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from base.models import Task


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        After authentication is succeded, redirect user to tasks.html
        """
        return reverse_lazy('tasks')


class CustomLogoutView(LogoutView):
    """
    After user is logout, it's redirected to login.html page
    """
    next_page = reverse_lazy('login')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm

    # After an account is created, redirect the user to tasks page
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        """
        Validating form and saving
        """
        user = form.save()
        if user is not None:
            # If everything was great, login the user using Django's modulo
            login(self.request, user)

        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        """
        Verifying if the user is already authenticated.
        If it is, redirect to tasks.html page
        """
        if self.request.user.is_authenticated:
            return redirect('tasks')

        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    # Showing tasks only about the user who created it
    # User get its own data
    def get_context_data(self, **kwargs):
        # Keeping the same data
        context = super().get_context_data(**kwargs)

        # Checking if the user's tasks belongs to the same user that created.
        context['tasks'] = context['tasks'].filter(user=self.request.user)

        # Counting incompleted tasks from user
        context['count'] = context['tasks'].filter(complete=False).count()

        # Search for a task method
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            # context['tasks'] = context['tasks'].filter(title__icontains=search_input)
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)

        # Access on form input search area
        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    # Make sure that a task can be associate only to the logged user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    # template_name = 'base/task_delete.html'
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
