import click

from src.database import SessionLocal
from src.services import items as item_service


@click.group("items")
def items_group():
    pass


@items_group.command("delete")
@click.argument("item_id", type=int)
def cli_delete_item(item_id: int):
    """Delete an item by ID."""
    with SessionLocal() as db:
        deleted = item_service.delete_item(db, item_id)

    if not deleted:
        click.echo(f"Item {item_id} not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Item {item_id} deleted.")
