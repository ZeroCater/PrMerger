from django_rq import job
from github import Github
from interface.models import User, Organization, Repository, PullRequest


@job
def fetch_additional_github_user_data(user_id):
    user = User.objects.get(pk=user_id)
    github = Github(user.github_login, user.github_access_token)

    for repo in github.get_user().get_repos():
        if repo.organization:
            owner = Organization.objects.get(identifier=repo.organization.id)
        else:
            owner = user

        defaults = {
            'owner': owner,
            'name': repo.full_name
        }
        result = Repository.objects.get_or_create(identifier=repo.id, defaults=defaults)

        pull_requests = repo.get_pulls()
        if pull_requests:
            for pr in pull_requests:
                defaults = {
                    'title': pr.title,
                    'number': pr.number,
                    'comments': pr.comments,
                    'is_merged': pr.is_merged(),
                    'opened_by': pr.user.login,
                    'base': pr.base.ref,
                    'url': pr.html_url
                }
                PullRequest.objects.get_or_create(identifier=pr.id, repository=result[0], defaults=defaults)
