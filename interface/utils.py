from __future__ import unicode_literals

from interface.models import Organization

DEFAULT_ORG_ID = 0
DEFAULT_ORG_NAME = 'Personal'


def user_repos_queryset(request):
    organization_id = request.session.get('organization_id', DEFAULT_ORG_ID)
    if organization_id != DEFAULT_ORG_ID:
        queryset = Organization.objects.get(id=organization_id).repositories\
            .filter(pull_requests__isnull=False, pull_requests__project__isnull=True)\
            .order_by('name')\
            .distinct()
    else:
        queryset = request.user.repositories \
            .filter(pull_requests__isnull=False, pull_requests__project__isnull=True) \
            .order_by('name') \
            .distinct()

    return queryset


def user_projects_queryset(request):
    organization_id = request.session.get('organization_id', DEFAULT_ORG_ID)
    if organization_id != DEFAULT_ORG_ID:
        queryset = Organization.objects.get(id=organization_id).projects.prefetch_related('pull_requests')
    else:
        queryset = request.user.projects.prefetch_related('pull_requests')

    status = request.GET.get('status', 'pending')
    return queryset.filter(status=status).all()


def project_repos_queryset(project):
    queryset = project.owner.repositories \
        .filter(pull_requests__isnull=False, pull_requests__project__isnull=True) \
        .order_by('name') \
        .distinct()
    return queryset
