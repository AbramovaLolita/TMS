from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool  # Заменили на обычный движок
from alembic import context

import sys
from os.path import dirname, abspath

# Добавляем корень проекта в путь, чтобы видеть папку app
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Импортируем ваши настройки и модели
from app.db.database import DATABASE_URL  # Проверьте путь, если файл в app/database.py
from app.db.models import Base # Проверьте, что импортируете Base, где собраны все модели

# Конфигурация Alembic
config = context.config

# Устанавливаем URL из вашего config.py прямо в настройки Alembic
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме (без подключения к БД)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в online режиме (с подключением к БД)."""
    
    # Создаем обычный синхронный движок
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Логика выбора режима запуска
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
