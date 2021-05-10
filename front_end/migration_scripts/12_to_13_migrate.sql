ALTER TABLE assignments ADD COLUMN enable_pair_programming integer NOT NULL DEFAULT 0;

ALTER TABLE submissions ADD COLUMN pair_programming_partner_id text DEFAULT NULL;