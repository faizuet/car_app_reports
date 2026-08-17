from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
import importlib
import pkgutil

import app.models
from app.core.base import Base
from app.core.config import config as app_config

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

for loader, name, is_pkg in pkgutil.walk_packages(app.models.__path__, app.models.__name__ + "."):
    importlib.import_module(name)

target_metadata = Base.metadata

migration_opts = {
    "target_metadata": target_metadata,
    "compare_type": True,
    "compare_server_default": True,
}


def run_migrations_offline() -> None:
    url = app_config.SQLALCHEMY_DATABASE_URI
    context.configure(url=url, literal_binds=True, **migration_opts)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = app_config.SQLALCHEMY_DATABASE_URI

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, **migration_opts)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
