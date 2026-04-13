# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context

from app.config import settings
from app.database import Base
import app.models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = settings.db_url
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Говорим Alembic что включать в миграции.
    Игнорируем все PostGIS/Tiger системные таблицы.
    """
    if type_ == "table" and reflected:
        # Игнорировать таблицы из системных схем PostGIS
        if hasattr(object, "schema") and object.schema in ("tiger", "topology"):
            return False
        # Игнорировать конкретные системные таблицы в public схеме
        ignored_tables = {
            "spatial_ref_sys", "topology", "layer",
            "geocode_settings", "geocode_settings_default",
            "pagc_lex", "pagc_gaz", "pagc_rules",
            "loader_platform", "loader_variables", "loader_lookuptables",
            "street_type_lookup", "direction_lookup", "secondary_unit_lookup",
            "state_lookup", "county_lookup", "countysub_lookup", "place_lookup",
            "zip_lookup", "zip_lookup_all", "zip_lookup_base", "zip_state",
            "zip_state_loc", "edges", "addrfeat", "faces", "featnames",
            "addr", "bg", "tabblock", "tabblock20", "tract", "zcta5",
            "cousub", "county", "state", "place",
        }
        if name in ignored_tables:
            return False
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        connection.execute(text("CREATE SEQUENCE IF NOT EXISTS entity_id_seq START 1;"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            user_module_prefix="geoalchemy2.",
            include_object=include_object,  # ← фильтр системных таблиц
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()