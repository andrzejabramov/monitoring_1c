-- ==============================================================================
-- Инициализация БД мониторинга 1С
-- Файл: 01-init.sql
-- Выполняется автоматически при первом старте контейнера PostgreSQL
-- ==============================================================================

-- Таблица для логов сессий 1С (биллинг и аналитика)
CREATE TABLE IF NOT EXISTS onec_session_log (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    infobase_name VARCHAR(100),
    client_type VARCHAR(50),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    avg_server_cpu_percent FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для ускорения выборок (биллинг по пользователю/времени)
CREATE INDEX IF NOT EXISTS idx_session_user ON onec_session_log(user_name);
CREATE INDEX IF NOT EXISTS idx_session_time ON onec_session_log(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_session_infobase ON onec_session_log(infobase_name);

-- Таблица для настройки лимитов пользователей (на будущее)
CREATE TABLE IF NOT EXISTS onec_user_limits (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) UNIQUE NOT NULL,
    max_sessions INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Пример: дефолтный лимит для всех пользователей = 1 сессия
INSERT INTO onec_user_limits (user_name, max_sessions)
VALUES ('default', 1)
ON CONFLICT (user_name) DO NOTHING;

-- Комментарий для документации
COMMENT ON TABLE onec_session_log IS 'История сессий 1С для биллинга и аналитики';
COMMENT ON TABLE onec_user_limits IS 'Лимиты одновременных сессий по пользователям';