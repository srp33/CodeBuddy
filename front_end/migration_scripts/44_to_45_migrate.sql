ALTER TABLE users ADD COLUMN research_cohort text;

UPDATE users
SET research_cohort = CASE WHEN RANDOM() >= 0.5 THEN "A" ELSE "B" END;