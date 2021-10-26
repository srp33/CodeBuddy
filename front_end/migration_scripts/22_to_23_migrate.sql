ALTER TABLE exercises ADD COLUMN allow_any_response integer NOT NULL DEFAULT 0;

UPDATE exercises
SET allow_any_response = 1
WHERE back_end = 'any_response';

UPDATE exercises
SET back_end = 'not_code'
WHERE back_end = 'any_response' OR back_end = 'free_response'
