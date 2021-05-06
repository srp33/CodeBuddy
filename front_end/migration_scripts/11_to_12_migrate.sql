CREATE TABLE IF NOT EXISTS valid_ip_addresses (
                        assignment_id integer NOT NULL,
                        ip_address text DEFAULT NULL,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON UPDATE CASCADE);

ALTER TABLE assignments ADD COLUMN access_restricted integer NOT NULL DEFAULT 0;