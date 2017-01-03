from django.conf.urls import url
from interface import views


urlpatterns = [
    url(r'^$', views.ListOrganizationView.as_view(), name='organization-list'),
    url(r'^projects$', views.ListProjectView.as_view(), name='project-list'),
    url(r'^projects/new$', views.ProjectView.as_view(), name='new-project'),
    url(r'^projects/(?P<pk>[0-9]+)$', views.ProjectView.as_view(), name='edit-project'),
    url(r'^projects/(?P<pk>[0-9]+)/delete$', views.delete_project_view, name='delete-project'),
    url(r'^projects/(?P<pk>[0-9]+)/merge$', views.merge_project_view, name='merge-project'),

    url(r'^api/repos/(?P<pk>[0-9]+)/pull_requests$', views.get_repo_pull_request_options),
    url(r'^api/pull_requests/(?P<pk>[0-9]+)/template', views.get_pull_request_template),
    url(r'^api/set_organization', views.update_session_organization, name='update-session-organization'),
]
