CREATE TABLE IF NOT EXISTS event_checkins (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_content TEXT NOT NULL,
  check_in_time TIMESTAMPTZ NOT NULL,
  category VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
  status VARCHAR(50) DEFAULT 'active'
);