"""
Dependency injection container for Amplenote MCP Server.

This module sets up the application's dependency injection container using
dependency-injector. It defines all the application's dependencies and their
relationships, making the application testable and following IoC principles.
"""

from dependency_injector import containers, providers

from .config import Settings
from .database import DatabaseConnection
from .notes import NotesService
from .tasks import TasksService


class Container(containers.DeclarativeContainer):
    """
    Application dependency injection container.

    This container manages all dependencies and their lifecycle. It provides:
    - Configuration management
    - Database connection factory
    - Service layer instances (Notes, Tasks)

    Usage:
        container = Container()
        notes_service = container.notes_service()
        tasks_service = container.tasks_service()
    """

    # Configuration
    config = providers.Configuration()

    # Settings provider
    settings = providers.Singleton(
        Settings,
    )

    # Database connection factory
    db_connection = providers.Factory(
        DatabaseConnection,
        settings=settings,
    )

    # Service layer
    notes_service = providers.Factory(
        NotesService,
        db_connection=db_connection,
    )

    tasks_service = providers.Factory(
        TasksService,
        db_connection=db_connection,
    )
