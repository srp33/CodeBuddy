ALTER TABLE courses ADD COLUMN virtual_buddy_config text NULL;

ALTER TABLE assignments ADD COLUMN use_virtual_buddy integer NOT NULL DEFAULT 0
