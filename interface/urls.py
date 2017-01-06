from django.conf.urls import url
from django.views.generic import TemplateView
from interface import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='welcome.html'), name='welcome'),
    url(r'^orgs$', views.OrganizationListView.as_view(), name='organization-list'),
    url(r'^projects$', views.ProjectListView.as_view(), name='project-list'),
    url(r'^projects/new$', views.ProjectCreateView.as_view(), name='new-project'),
    url(r'^projects/(?P<pk>[0-9]+)$', views.ProjectUpdateView.as_view(), name='edit-project'),
    url(r'^projects/(?P<pk>[0-9]+)/delete$', views.ProjectDeleteView.as_view(), name='delete-project'),
    url(r'^projects/(?P<pk>[0-9]+)/merge$', views.ProjectMergeView.as_view(), name='merge-project'),
    url(r'^logout$', views.logout_user, name='logout'),

    url(r'^api/repos/(?P<pk>[0-9]+)/pull_requests$', views.get_repo_pull_request_options),
    url(r'^api/pull_requests/(?P<pk>[0-9]+)/template', views.get_pull_request_template),
    url(r'^api/set_organization', views.update_session_organization, name='update-session-organization'),
]
