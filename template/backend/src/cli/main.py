import click

from src.cli.users import users_group


@click.group()
def cli():
    pass


cli.add_command(users_group)
