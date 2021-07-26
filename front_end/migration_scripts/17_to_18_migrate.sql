CREATE TABLE IF NOT EXISTS users2 (
        user_id text PRIMARY KEY,
        name text,
        given_name text,
        family_name text,
        locale text,
        ace_theme text NOT NULL DEFAULT "tomorrow",
        use_auto_complete integer NOT NULL DEFAULT 1);

INSERT INTO users2
        SELECT user_id, name, given_name, family_name, locale, ace_theme, use_auto_complete
        FROM users;

DROP TABLE IF EXISTS users;

ALTER TABLE users2 RENAME TO users;
