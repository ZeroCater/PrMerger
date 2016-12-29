from django.contrib.admin.sites import site
from interface import models


site.register(models.User)
site.register(models.Organization)
site.register(models.User.organizations.through)
site.register(models.Repository)
site.register(models.Project)
site.register(models.PullRequest)
