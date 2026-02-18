#!/usr/bin/env python3
"""
Тестовый скрипт подключения к БД мониторинга 1С
MVP v0.1 - только проверка записи/чтения
"""

import os
import sys
from datetime import datetime

# Проверка зависимости
try:
    import psycopg2
except ImportError:
    print("❌ Ошибка: модуль psycopg2 не установлен")
    print("   Установите: pip install psycopg2-binary")
    sys.exit(1)


def get_db_config():
    """Чтение конфигурации из переменных окружения"""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_HOST_PORT", "5433")),
        "dbname": os.getenv("DB_NAME", "onec_monitoring"),
        "user": os.getenv("DB_USER", "monitor"),
        "password": os.getenv("DB_PASSWORD", "change_me_in_production"),
    }


def test_connection():
    """Тест подключения и записи в БД"""
    config = get_db_config()

    print(f"🔌 Подключение к БД: {config['host']}:{config['port']}/{config['dbname']}")

    try:
        # Подключение
        conn = psycopg2.connect(**config)
        print("✅ Подключение успешно")

        # Курсор
        cur = conn.cursor()

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
        cur.execute(
            """
            INSERT INTO onec_session_log 
            (session_id, user_name, infobase_name, client_type, start_time, duration_seconds, avg_server_cpu_percent)
            VALUES (%(session_id)s, %(user_name)s, %(infobase_name)s, %(client_type)s, %(start_time)s, %(duration_seconds)s, %(avg_server_cpu_percent)s)
        """,
            test_session,
        )

        conn.commit()
        print("✅ Тестовая запись добавлена")

        # SELECT для подтверждения
        cur.execute(
            """
            SELECT id, session_id, user_name, start_time 
            FROM onec_session_log 
            WHERE session_id = %s
        """,
            ("test-mvp-001",),
        )

        result = cur.fetchone()
        if result:
            print(
                f"✅ Подтверждение чтения: id={result[0]}, session={result[1]}, user={result[2]}"
            )
        else:
            print("❌ Ошибка: запись не найдена после INSERT")
            return False

        # Очистка
        cur.close()
        conn.close()
        print("✅ Соединение закрыто")

        return True

    except psycopg2.Error as e:
        print(f"❌ Ошибка PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
