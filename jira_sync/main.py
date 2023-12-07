"""
Script for synchronizing tickets from various trackers in JIRA project.
"""

import click
import tomllib

from jira_sync.pagure import Pagure
from jira_sync.jira_wrapper import JIRA

@click.group()
def cli():
    pass

@click.command()
@click.option("--since", help=("How many days ago to look for closed issues."
                               "Expects date in DD.MM.YYYY format (31.12.2021)."))
@click.option("--config", default="config.toml", help="Path to configuration file.")
def sync_tickets(since: str, config: str):
    """
    Sync the ticket from sources provided in configuration file.

    Params:
      since: How many days ago to look for closed issues.
      config: Path to configuration file.
    """
    with open(config, "rb") as config_file:
        config_dict = tomllib.load(config_file)

    jira = JIRA(
        config_dict["General"]["jira_instance"],
        config_dict["General"]["jira_token"],
        config_dict["General"]["jira_project"],
        config_dict["General"]["jira_default_issue_type"],
    )

    pagure_enabled = config_dict["Pagure"]["enabled"]

    # Pagure is enabled in configuration
    if pagure_enabled:
        pagure_issues = []
        pagure = Pagure(config_dict["Pagure"]["pagure_url"])

        # Retrieve all open issues on the project
        for repository in config_dict["Pagure"]["repositories"]:
            pagure_issues.extend(
                pagure.get_project_issues(repository["repo"])
            )

    issue = pagure_issues[0]

    jira_issue = jira.get_issue_by_link(issue["full_url"])

    click.echo(jira_issue)

    if not jira_issue:
        issue_id = jira.create_issue(
            issue["title"],
            issue["content"],
            issue["full_url"]
        )

        click.echo(issue_id)


if __name__ == "__main__":
    cli.add_command(sync_tickets)
    cli()
