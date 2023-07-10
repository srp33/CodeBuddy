ALTER TABLE courses ADD COLUMN llm_config text NULL;

ALTER TABLE assignments ADD COLUMN use_llm integer NOT NULL DEFAULT 0