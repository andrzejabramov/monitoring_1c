#!/usr/bin/env python3
"""
Тестовый скрипт подключения к БД мониторинга 1С
MVP v0.1 - asyncpg версия
"""

import os
import sys
import asyncio
from datetime import datetime

try:
    import asyncpg
except ImportError:
    print("❌ Ошибка: модуль asyncpg не установлен")
    print("   Установите: pip install asyncpg")
    sys.exit(1)


def get_db_config():
    """Чтение конфигурации из переменных окружения"""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_HOST_PORT", "5433")),
        "database": os.getenv("DB_NAME", "onec_monitoring"),
        "user": os.getenv("DB_USER", "monitor"),
        "password": os.getenv("DB_PASSWORD", "change_me_in_production"),
    }


async def test_connection():
    """Тест подключения и записи в БД"""
    config = get_db_config()

    print(
        f"🔌 Подключение к БД: {config['host']}:{config['port']}/{config['database']}"
    )

    conn = None
    try:
        # Подключение
        conn = await asyncpg.connect(**config)
        print("✅ Подключение успешно")

        # Тестовая запись
        test_session = {
            "session_id": "test-mvp-001",
            "user_name": "test_user",
            "infobase_name": "test_ib",
            "client_type": "TestClient",
            "start_time": datetime.now(),
            "duration_seconds": 120,
            "avg_server_cpu_percent": 45.5,
        }

        # INSERT
        await conn.execute(
            """
            INSERT INTO onec_session_log 
            (session_id, user_name, infobase_name, client_type, start_time, duration_seconds, avg_server_cpu_percent)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
            test_session["session_id"],
            test_session["user_name"],
            test_session["infobase_name"],
            test_session["client_type"],
            test_session["start_time"],
            test_session["duration_seconds"],
            test_session["avg_server_cpu_percent"],
        )

        print("✅ Тестовая запись добавлена")

        # SELECT для подтверждения
        result = await conn.fetchrow(
            """
            SELECT id, session_id, user_name, start_time 
            FROM onec_session_log 
            WHERE session_id = $1
        """,
            "test-mvp-001",
        )

        if result:
            print(
                f"✅ Подтверждение чтения: id={result['id']}, session={result['session_id']}, user={result['user_name']}"
            )
        else:
            print("❌ Ошибка: запись не найдена после INSERT")
            return False

        print("✅ Соединение закрыто")
        return True

    except asyncpg.Error as e:
        print(f"❌ Ошибка PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
