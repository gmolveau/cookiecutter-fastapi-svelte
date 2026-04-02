import click

from src.database import SessionLocal
from src.services.users import assign_role


@click.group("users")
def users_group():
    pass


@users_group.command("make-superadmin")
@click.option("--email", default=None, help="User email address.")
@click.option("--id", "user_id", default=None, type=int, help="User database ID.")
@click.option("--sub", default=None, help="User OIDC subject (sub).")
@click.option("--name", default=None, help="User name.")
def cli_make_superadmin(
    email: str | None, user_id: int | None, sub: str | None, name: str | None
):
    """Give the superadmin role to a user."""
    if not any([email, user_id, sub, name]):
        click.echo("Provide at least one of --email, --id, --sub, --name.", err=True)
        raise SystemExit(1)

    with SessionLocal() as db:
        user = assign_role(
            db, role_name="superadmin", sub=sub, email=email, name=name, user_id=user_id
        )

    if user is None:
        click.echo("User or superadmin role not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Superadmin role assigned to {user.name} ({user.sub}).")
