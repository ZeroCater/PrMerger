from github import Github
from interface.models import Organization
from interface.tasks import fetch_additional_github_user_data


def retrieve_github_user_data(user, *args, **kwargs):
    github = Github(user.github_login, user.github_access_token)

    # Get user's organizations
    for org in github.get_user().get_orgs():
        result = Organization.objects.get_or_create(identifier=org.id, defaults={'name': org.name})
        user.organizations.add(result[0])

    # Fetching repos & pull requests can take some time.
    # Let's enqueue a worker job to do this in the background.
    fetch_additional_github_user_data.delay(user.id)
