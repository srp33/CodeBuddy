ALTER TABLE users RENAME COLUMN research_cohort TO research_cohort_1;

ALTER TABLE users ADD COLUMN research_cohort_2 text;

UPDATE users
SET research_cohort_2 = CASE WHEN RANDOM() >= 0.5 THEN "A" ELSE "B" END;
