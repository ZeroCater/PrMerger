from __future__ import unicode_literals

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from github import Github
from github.GithubException import GithubException

from interface.forms import ProjectForm
from interface.utils import (
    user_repos_queryset, user_projects_queryset, project_repos_queryset, DEFAULT_ORG_ID, DEFAULT_ORG_NAME
)
from interface.models import Repository, Organization, PullRequest, Project


class OrganizationListView(LoginRequiredMixin, ListView):
    template_name = 'interface/list_organizations.html'
    context_object_name = 'organizations'

    def get_queryset(self):
        queryset = self.request.user.organizations.all()
        return queryset


class ProjectListView(LoginRequiredMixin, ListView):
    template_name = 'interface/list_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = user_projects_queryset(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        org_id = self.request.session.get('organization_id', DEFAULT_ORG_ID)
        organization_name = Organization.objects.get(pk=org_id).name if org_id != DEFAULT_ORG_ID else DEFAULT_ORG_NAME
        status = self.request.GET.get('status', 'pending')
        return super(ProjectListView, self).get_context_data(organization_name=organization_name, status=status)


class ProjectViewMixin(object):
    form_class = ProjectForm
    template_name = 'interface/project_details.html'
    queryset = Project.objects.all()
    permission_denied_message = 'You are not authorized to view this project'
    pk_url_kwarg = 'pk'

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            return None

        try:
            obj = self.queryset.get(pk=pk)
        except Project.DoesNotExist:
            self.raise_exception = True
            return self.handle_no_permission()
        else:
            owner = obj.owner
            if not owner == self.request.user and owner not in self.request.user.organizations.all():
                self.raise_exception = True
                return self.handle_no_permission()
            return obj

    def get_success_url(self):
        redirect_url = reverse('interface:project-list')
        return redirect_url

    def form_invalid(self, form):
        context = {
            'form': form,
            'pull_requests': PullRequest.objects.filter(id__in=self.request.POST.getlist('pull_requests')).all(),
        }
        return self.render_to_response(self.get_context_data(**context))

    def update_included_pull_requests(self, project):
        selected_pr_ids = self.request.POST.getlist('pull_requests')
        PullRequest.objects.filter(id__in=selected_pr_ids).update(project=project)
        return HttpResponseRedirect(self.get_success_url())


class ProjectCreateView(LoginRequiredMixin, ProjectViewMixin, CreateView):
    def get_context_data(self, **kwargs):
        if 'repositories' not in kwargs:
            kwargs.setdefault('repositories', user_repos_queryset(self.request))
        if 'pull_requests' not in kwargs:
            kwargs.setdefault('pull_requests', [])
        return super(ProjectCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        organization_id = self.request.session.get('organization_id', DEFAULT_ORG_ID)
        if organization_id != DEFAULT_ORG_ID:
            owner = Organization.objects.get(id=organization_id)
        else:
            owner = self.request.user

        try:
            project = form.save(commit=False)
            project.owner = owner
            project.save()
        except IntegrityError as error:
            # TODO: this error is not clear. Clarify which organization this is.
            form._errors['name'] = error.message
            return self.form_invalid(form)
        else:
            self.update_included_pull_requests(project)
            return HttpResponseRedirect(self.get_success_url())


class ProjectUpdateView(LoginRequiredMixin, ProjectViewMixin, UpdateView):
    def get_context_data(self, **kwargs):
        if 'repositories' not in kwargs:
            kwargs.setdefault('repositories', project_repos_queryset(self.object))
        if 'pull_requests' not in kwargs:
            kwargs.setdefault('pull_requests', self.object.pull_requests.all())
        return super(ProjectUpdateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            project = form.save(commit=True)
        except IntegrityError as error:
            # TODO: this error is not clear. Clarify which organization this is.
            form._errors['name'] = error.message
            return self.form_invalid(form=form)
        else:
            project.pull_requests.update(project=None)
            self.update_included_pull_requests(project)
            return HttpResponseRedirect(self.get_success_url())


class ProjectDeleteView(LoginRequiredMixin, ProjectViewMixin, DetailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.pull_requests.update(project=None)
        self.object.delete()
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)


class ProjectMergeView(LoginRequiredMixin, ProjectViewMixin, DetailView):
    template_name = 'interface/project_errors.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        github = Github(request.user.github_login, request.user.github_access_token)
        errors = []

        for pr in self.object.pull_requests.prefetch_related('repository').all():
            try:
                repo = github.get_user().get_repo(pr.repository.name)
                pull = repo.get_pull(pr.number)
                pull.merge()

                pr.is_merged = True
                pr.save()
            except GithubException as error:
                errors.append({'pull_request': pr, 'error': error.message if error.message else error})

        if not errors:
            self.object.status = Project.MERGED
            self.object.save()
            redirect_url = self.get_success_url()
            return HttpResponseRedirect(redirect_url)

        self.object.status = Project.FAILED
        self.object.save()
        kwargs = {
            'project': self.object,
            'message': 'Got some unexpected errors while merging pull requests. Please review the errors below.',
            'errors': errors
        }
        return self.render_to_response(self.get_context_data(**kwargs))


@login_required
def update_session_organization(request):
    organization_id = request.POST.get('organizationId')
    msg = 'You are not authorized to view this organization'

    if not organization_id:
        return HttpResponseForbidden(content=msg)

    try:
        organization_id = int(organization_id)
    except ValueError:
        return HttpResponseForbidden(content=msg)
    else:
        if organization_id != DEFAULT_ORG_ID and not request.user.organizations.filter(id=organization_id).exists():
            return HttpResponseForbidden(content=msg)

        request.session['organization_id'] = organization_id
        return HttpResponse(status=200)


@login_required
def get_repo_pull_request_options(request, pk):
    pull_requests = Repository.objects.get(pk=pk).pull_requests.filter(project__isnull=True)
    options = [
        '<option value={}>{}</option>'.format(pr.pk, pr.title)
        for pr in pull_requests
    ]
    options.insert(0, '<option value selected="selected">Select a pull request</option>')
    return HttpResponse(options)


@login_required
def get_pull_request_template(request, pk):
    pull_request = PullRequest.objects.get(id=pk)
    return render(request, 'interface/shared/pull_request.html', {'pull_request': pull_request})
