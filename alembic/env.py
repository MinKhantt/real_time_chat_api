from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.db.database import Base
from app.core.config import settings
from app.models.user import User
from app.models.message import Message
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL.replace("+asyncpg", "")  # use sync URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Create a sync engine for Alembic
    connectable = create_engine(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        poolclass=pool.NullPool,
        future=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Run the correct mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
