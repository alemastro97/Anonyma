-- Anonyma Database Schema
-- User management, authentication, and usage tracking

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'demo', -- 'admin', 'premium', 'demo'
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Usage tracking table
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    processing_time FLOAT,
    text_length INTEGER,
    detections_count INTEGER,
    mode VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Usage quotas table
CREATE TABLE IF NOT EXISTS usage_quotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    daily_limit INTEGER DEFAULT 50,
    monthly_limit INTEGER DEFAULT 500,
    daily_used INTEGER DEFAULT 0,
    monthly_used INTEGER DEFAULT 0,
    last_daily_reset TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_monthly_reset TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table (for document processing)
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    progress FLOAT DEFAULT 0.0,
    filename VARCHAR(255),
    format VARCHAR(50),
    mode VARCHAR(50),
    detections_count INTEGER,
    processing_time FLOAT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123 - CHANGE THIS!)
INSERT INTO users (email, username, password_hash, full_name, role, email_verified)
VALUES (
    'admin@anonyma.local',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVq92.6LS', -- admin123
    'Administrator',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert demo user (password: demo123)
INSERT INTO users (email, username, password_hash, full_name, role, email_verified)
VALUES (
    'demo@anonyma.local',
    'demo',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- demo123
    'Demo User',
    'demo',
    true
) ON CONFLICT (email) DO NOTHING;

-- Initialize usage quotas for users
INSERT INTO usage_quotas (user_id, daily_limit, monthly_limit)
SELECT id,
    CASE
        WHEN role = 'admin' THEN 999999
        WHEN role = 'premium' THEN 1000
        ELSE 50
    END,
    CASE
        WHEN role = 'admin' THEN 999999
        WHEN role = 'premium' THEN 10000
        ELSE 500
    END
FROM users
ON CONFLICT (user_id) DO NOTHING;

-- Function to reset daily quotas
CREATE OR REPLACE FUNCTION reset_daily_quotas()
RETURNS void AS $$
BEGIN
    UPDATE usage_quotas
    SET daily_used = 0,
        last_daily_reset = CURRENT_TIMESTAMP
    WHERE last_daily_reset < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Function to reset monthly quotas
CREATE OR REPLACE FUNCTION reset_monthly_quotas()
RETURNS void AS $$
BEGIN
    UPDATE usage_quotas
    SET monthly_used = 0,
        last_monthly_reset = CURRENT_TIMESTAMP
    WHERE EXTRACT(MONTH FROM last_monthly_reset) < EXTRACT(MONTH FROM CURRENT_TIMESTAMP)
       OR EXTRACT(YEAR FROM last_monthly_reset) < EXTRACT(YEAR FROM CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- Create views for analytics
CREATE OR REPLACE VIEW user_usage_summary AS
SELECT
    u.id,
    u.email,
    u.username,
    u.role,
    uq.daily_used,
    uq.daily_limit,
    uq.monthly_used,
    uq.monthly_limit,
    COUNT(DISTINCT ul.id) as total_requests,
    AVG(ul.processing_time) as avg_processing_time,
    SUM(ul.detections_count) as total_detections
FROM users u
LEFT JOIN usage_quotas uq ON u.id = uq.user_id
LEFT JOIN usage_logs ul ON u.id = ul.user_id
GROUP BY u.id, u.email, u.username, u.role, uq.daily_used, uq.daily_limit, uq.monthly_used, uq.monthly_limit;

-- Subscriptions table for Stripe integration
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'cancelled', 'past_due'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);

COMMENT ON TABLE users IS 'User accounts with role-based access control';
COMMENT ON TABLE api_keys IS 'API keys for programmatic access';
COMMENT ON TABLE usage_logs IS 'Detailed usage tracking for analytics';
COMMENT ON TABLE usage_quotas IS 'Per-user usage limits and quotas';
COMMENT ON TABLE sessions IS 'Active user sessions with JWT tokens';
COMMENT ON TABLE jobs IS 'Document processing jobs history';
COMMENT ON TABLE subscriptions IS 'Stripe subscription management';
