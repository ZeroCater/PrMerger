from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required

from interface.forms import ProjectForm
from interface.utils import (
    user_repos_queryset, user_projects_queryset, project_repos_queryset, get_projects_url, AuthorizedAccessMixin
)
from interface.models import Repository, Organization, PullRequest, Project


class ListOrganizationView(AuthorizedAccessMixin, ListView):
    template_name = 'interface/list_organizations.html'
    context_object_name = 'organizations'

    def get_queryset(self):
        queryset = self.request.user.organizations.all()
        return queryset


class ListProjectView(AuthorizedAccessMixin, ListView):
    template_name = 'interface/list_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = user_projects_queryset(self.request)
        return queryset


class ProjectView(AuthorizedAccessMixin, CreateView, UpdateView):
    form_class = ProjectForm
    template_name = 'interface/new_project.html'
    queryset = Project.objects.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        repositories = project_repos_queryset(self.object) if self.object else user_repos_queryset(request=request)
        context = {
            'repositories': repositories,
            'pull_requests': self.object.pull_requests.all() if self.object else None
        }
        return self.render_to_response(self.get_context_data(**context))

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            return None

        return self.queryset.get(pk=pk)

    def form_valid(self, form):
        owner = self.request.user
        organization_id = self.request.GET.get('organizationId', None)
        if organization_id:
            owner = Organization.objects.get(id=organization_id)

        project = form.save(commit=False)
        project.owner = owner
        project.save()

        for pr_id in self.request.POST.getlist('pull_requests'):
            pull_request = PullRequest.objects.get(id=pr_id)
            pull_request.project = project
            pull_request.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return get_projects_url(self.request)


@login_required
def delete_project_view(request, pk):
    project = Project.objects.get(pk=pk)
    project.delete()
    return HttpResponseRedirect(get_projects_url(request))


@login_required
def merge_pull_requests_view(request):
    pass


@login_required
def get_repo_pull_request_options(request, pk):
    pull_requests = Repository.objects.get(pk=pk).pull_requests.all()
    options = [
        '<option value={}>{}</option>'.format(pr.pk, pr.title)
        for pr in pull_requests
    ]
    options.insert(0, '<option value selected="selected">---------</option>')
    return HttpResponse(options)


@login_required
def get_repository_options(request):
    repos = user_repos_queryset(request)
    options = [
        '<option value={}>{}</option>'.format(repo.pk, repo.name)
        for repo in repos.all()
    ]
    options.insert(0, '<option value selected="selected">---------</option>')
    return HttpResponse(options)


@login_required
def get_pull_request_template(request, pk):
    pull_request = PullRequest.objects.get(id=pk)
    return render(request, 'interface/shared/pull_request.html', {'pull_request': pull_request})
