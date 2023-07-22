ALTER TABLE users ADD COLUMN research_cohort integer;

UPDATE users
SET research_cohort = CASE WHEN RANDOM() >= 0.5 THEN 1 ELSE 0 END;