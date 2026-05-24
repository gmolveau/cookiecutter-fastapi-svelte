import click

from src.database import SessionLocal
from src.services.users import assign_role_to_group, assign_role_to_user


@click.group("users")
def users_group():
    pass


@users_group.command("promote-user-to-superadmin")
@click.option("--email", default=None, help="User email address.")
@click.option("--id", "user_id", default=None, type=int, help="User database ID.")
@click.option("--sub", default=None, help="User OIDC subject (sub).")
@click.option("--name", default=None, help="User name.")
def cli_promote_user_to_superadmin(
    email: str | None, user_id: int | None, sub: str | None, name: str | None
):
    """Give the superadmin role to a user."""
    if not any([email, user_id, sub, name]):
        click.echo("Provide at least one of --email, --id, --sub, --name.", err=True)
        raise SystemExit(1)

    with SessionLocal() as db:
        user = assign_role_to_user(
            db, role_name="superadmin", sub=sub, email=email, name=name, user_id=user_id
        )

    if user is None:
        click.echo("User or superadmin role not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Superadmin role assigned to {user.name} ({user.sub}).")


@users_group.command("promote-group-to-superadmin")
@click.option("--id", "group_id", default=None, type=int, help="Group database ID.")
@click.option("--name", default=None, help="Group name.")
def cli_promote_group_to_superadmin(group_id: int | None, name: str | None):
    """Give the superadmin role to a group."""
    if not any([group_id, name]):
        click.echo("Provide at least one of --id, --name.", err=True)
        raise SystemExit(1)

    with SessionLocal() as db:
        group = assign_role_to_group(
            db, role_name="superadmin", group_id=group_id, name=name
        )

    if group is None:
        click.echo("Group or superadmin role not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Superadmin role assigned to group {group.name} (id={group.id}).")
