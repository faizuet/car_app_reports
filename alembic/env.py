from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import importlib
import pkgutil
import app.models
from app.core.base import Base


config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

for loader, name, is_pkg in pkgutil.walk_packages(app.models.__path__, app.models.__name__ + "."):
    importlib.import_module(name)

target_metadata = Base.metadata

migration_opts = {"target_metadata": target_metadata,
                  "compare_type": True,
                  "compare_server_default": True}

def run_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True, **migration_opts)
    with context.begin_transaction():
        context.run_migrations()

def run_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}),
                                     prefix="sqlalchemy.",
                                     poolclass=pool.NullPool)
    with connectable.connect() as conn:
        context.configure(connection=conn, **migration_opts)
        with context.begin_transaction():
            context.run_migrations()

run_offline() if context.is_offline_mode() else run_online()

