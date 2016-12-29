from django.conf.urls import url
from interface import views


urlpatterns = [
    url(r'^$', views.ListOrganizationView.as_view()),
    url(r'^projects$', views.ListProjectView.as_view()),
    url(r'^projects/new$', views.ProjectView.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/edit$', views.ProjectView.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/delete$', views.delete_project_view),
    url(r'^projects/(?P<pk>[0-9]+)/merge-all$', views.merge_pull_requests_view),

    url(r'^api/repos/(?P<pk>[0-9]+)/pull_requests$', views.get_repo_pull_request_options),
    url(r'^api/pull_requests/(?P<pk>[0-9]+)/template', views.get_pull_request_template)
]
