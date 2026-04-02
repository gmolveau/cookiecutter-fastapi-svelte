import click

from src.cli.templates import templates_group
from src.cli.users import users_group


@click.group()
def all_commands():
    pass


# Add script handlers here
all_commands.add_command(templates_group)
all_commands.add_command(users_group)


if __name__ == "__main__":
    all_commands()
