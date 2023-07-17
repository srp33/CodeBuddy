ALTER TABLE courses ADD COLUMN virtual_assistant_config text NULL;

ALTER TABLE assignments ADD COLUMN use_virtual_assistant integer NOT NULL DEFAULT 0
