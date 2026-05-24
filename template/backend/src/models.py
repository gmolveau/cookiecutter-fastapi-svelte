from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    RelationshipProperty,
    mapped_column,
    relationship,
)


class BaseModel(DeclarativeBase):
    """Base class for all ORM models."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    def __repr__(self):
        id_field = [
            f"{column.name}={getattr(self, column.name)!r}"
            for column in self.__table__.columns
            if column.name == "id"
        ]
        other_fields = sorted(
            [
                f"{column.name}={getattr(self, column.name)!r}"
                for column in self.__table__.columns
                if column.name != "id"
                and not isinstance(
                    self.__mapper__.get_property(column.name), RelationshipProperty
                )
            ],
        )
        fields = id_field + other_fields
        return f"<{self.__class__.__name__}({', '.join(fields)})>"


# Many-to-many association table for User <-> Group
user_groups = Table(
    "user_groups",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)


class Role(BaseModel):
    """A role that can be assigned to a user or a group."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")
    groups: Mapped[list["Group"]] = relationship("Group", back_populates="role")


class Group(BaseModel):
    """A group that users can belong to."""

    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)

    role: Mapped["Role | None"] = relationship("Role", back_populates="groups")
    users: Mapped[list["User"]] = relationship(
        "User", secondary=user_groups, back_populates="groups"
    )


class User(BaseModel):
    """An authenticated user."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    sub: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)

    role: Mapped["Role | None"] = relationship("Role", back_populates="users")
    groups: Mapped[list["Group"]] = relationship(
        "Group", secondary=user_groups, back_populates="users"
    )
