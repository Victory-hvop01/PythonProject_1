CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    has_movement BOOLEAN NOT NULL,
    movement_percentage FLOAT NOT NULL,
    analysis_time FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);

CREATE INDEX IF NOT EXISTS idx_analysis_results_has_movement ON analysis_results(has_movement);