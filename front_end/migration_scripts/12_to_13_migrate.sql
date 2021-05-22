ALTER TABLE exercises ADD COLUMN enable_pair_programming integer NOT NULL DEFAULT 0;

ALTER TABLE submissions ADD COLUMN partner_id text DEFAULT NULL;

