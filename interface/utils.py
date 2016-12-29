from __future__ import unicode_literals

from django.contrib.auth.mixins import AccessMixin
from interface.models import Organization


def user_repos_queryset(request):
    queryset = request.user.repositories\
        .filter(pull_requests__isnull=False, pull_requests__project__isnull=True)\
        .order_by('name')\
        .distinct()

    organization_id = request.GET.get('organizationId', None)
    if organization_id:
        queryset = Organization.objects.get(id=organization_id).repositories\
            .filter(pull_requests__isnull=False, pull_requests__project__isnull=True)\
            .order_by('name')\
            .distinct()

    return queryset


def user_projects_queryset(request):
    queryset = request.user.projects.prefetch_related('pull_requests').all()

    organization_id = request.GET.get('organizationId', None)
    if organization_id:
        queryset = Organization.objects.get(id=organization_id).projects.prefetch_related('pull_requests').all()

    return queryset


def project_repos_queryset(project):
    queryset = project.owner.repositories \
        .filter(pull_requests__isnull=False, pull_requests__project__isnull=True) \
        .order_by('name') \
        .distinct()
    return queryset


def get_projects_url(request):
    organization_id = request.GET.get('organizationId', None)
    redirect_url = '/projects' if not organization_id else '/projects?organizationId=%s' % (organization_id,)
    return redirect_url


class AuthorizedAccessMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        org_id = request.GET.get('organizationId')
        if org_id and not request.user.organizations.filter(id=org_id).exists():
            self.raise_exception = True
            self.permission_denied_message = "You don't have permission to access this organization"
            return self.handle_no_permission()

        return super(AuthorizedAccessMixin, self).dispatch(request, *args, **kwargs)
