from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)
from .models import Project
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        """
        Ensure users can only see their own projects.
        """
        return Project.objects.filter(owner=self.request.user).order_by('-created_at')

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'client']
    success_url = reverse_lazy('projects:project-list')

    def form_valid(self, form):
        """
        Assign the current user as the owner of the new project.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'client', 'phase']
    success_url = reverse_lazy('projects:project-list')

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project-list')

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

@login_required
@require_POST
def advance_project_phase(request, pk):
    """
    Advances the project to the next phase.
    """
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    current_phase_index = project.Phases.values.index(project.phase)
    
    if current_phase_index < len(project.Phases.values) - 1:
        next_phase = project.Phases.values[current_phase_index + 1]
        project.phase = next_phase
        project.save()
        messages.success(request, _(f"Project advanced to {project.get_phase_display()}"))
    else:
        messages.info(request, _("The project is already in the final phase."))
        
    return redirect('projects:project-detail', pk=project.pk)
