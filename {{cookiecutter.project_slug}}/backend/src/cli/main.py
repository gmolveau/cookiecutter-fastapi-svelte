import click

from src.cli.items import items_group
from src.cli.users import users_group


@click.group()
def cli():
    pass


cli.add_command(items_group)
cli.add_command(users_group)
