from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.functional import cached_property


class User(AbstractUser):
    organizations = models.ManyToManyField('Organization')
    projects = GenericRelation('Project', 'owner_id', 'owner_type')
    repositories = GenericRelation('Repository', 'owner_id', 'owner_type')

    @cached_property
    def social_user(self):
        return self.social_auth.first()

    @property
    def github_login(self):
        return self.social_user.extra_data['login']

    @property
    def github_access_token(self):
        return self.social_user.extra_data['access_token']


class Organization(models.Model):
    identifier = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=200)
    projects = GenericRelation('Project', 'owner_id', 'owner_type')
    repositories = GenericRelation('Repository', 'owner_id', 'owner_type')

    def __unicode__(self):
        return unicode(self.name)


class Repository(models.Model):
    owner_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    owner_id = models.PositiveIntegerField()
    owner = GenericForeignKey('owner_type', 'owner_id')
    identifier = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.name)


class Project(models.Model):
    DELETED = 'deleted'
    PENDING = 'pending'
    MERGED = 'merged'

    STATUSES = (
        (DELETED, DELETED),
        (PENDING, PENDING),
        (MERGED, MERGED)
    )

    name = models.CharField(max_length=100)
    owner_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    owner_id = models.PositiveIntegerField()
    owner = GenericForeignKey('owner_type', 'owner_id')
    status = models.CharField(choices=STATUSES, max_length=20, default=PENDING)

    class Meta:
        unique_together = ('name', 'owner_type', 'owner_id')
        db_table = 'project'

    def __unicode__(self):
        return u'name={}, owner={}/{}'.format(self.name, self.owner_type, self.owner)


class PullRequest(models.Model):
    identifier = models.PositiveIntegerField(unique=True)
    repository = models.ForeignKey(Repository, related_name='pull_requests')
    project = models.ForeignKey('Project', related_name='pull_requests', null=True, blank=True, on_delete=models.CASCADE)
    title = models.TextField()
    number = models.PositiveIntegerField()
    comments = models.PositiveIntegerField()
    is_merged = models.BooleanField(default=False)
    opened_by = models.CharField(max_length=200)
    base = models.CharField(max_length=200)

    def __unicode__(self):
        return u'repo={}, title={}'.format(self.repository, self.title)
