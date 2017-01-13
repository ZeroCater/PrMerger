from __future__ import unicode_literals

from django.urls import reverse
from django.utils.six.moves.urllib.parse import urljoin

from django_rq import job
from github import Github
from interface.models import User, Organization, Repository, PullRequest
from prmerger.settings import WEBHOOK_SECRET


@job
def fetch_additional_github_user_data(user_id, **kwargs):
    user = User.objects.get(pk=user_id)
    github = Github(user.github_login, user.github_access_token)
    webhook_schema = 'https' if kwargs.get('secure') else 'http'
    webhook_path = reverse('interface:webhook')

    for github_repo in github.get_user().get_repos():
        # Save repo to db
        if github_repo.organization:
            owner = Organization.objects.get(identifier=github_repo.organization.id)
        else:
            owner = user

        defaults = {
            'owner': owner,
            'name': github_repo.name,
            'full_name': github_repo.full_name,
        }
        result = Repository.objects.update_or_create(identifier=github_repo.id, defaults=defaults)
        local_repo = result[0]

        # Retrieve and save all of its Pull Requests
        pull_requests = github_repo.get_pulls()
        if pull_requests:
            for pr in pull_requests:
                defaults = {
                    'title': pr.title,
                    'number': pr.number,
                    'comments': pr.comments,
                    'state': pr.state,
                    'opened_by': pr.user.login,
                    'base': pr.base.ref,
                    'url': pr.html_url,
                    'branch': pr.head.ref
                }
                PullRequest.objects.update_or_create(identifier=pr.id, repository=local_repo, defaults=defaults)

        # Add a webhook to be notified about pull_request event
        if not local_repo.webhook_id:
            hook = github_repo.create_hook(
                'web',
                {
                    'content_type': 'json',
                    'url': '{}://{}{}'.format(webhook_schema, kwargs.get('host'), webhook_path),
                    'secret': WEBHOOK_SECRET
                },
                events=['pull_request'],
                active=True
            )
            local_repo.webhook_id = hook.id
            local_repo.save()
