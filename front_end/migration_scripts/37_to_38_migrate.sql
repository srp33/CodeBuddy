CREATE TABLE users2 (
        user_id text PRIMARY KEY,
        name text,
        given_name text,
        family_name text,
        locale text,
        ace_theme text NOT NULL DEFAULT "tomorrow",
        use_auto_complete integer NOT NULL DEFAULT 1,
        enable_vim integer NOT NULL DEFAULT 0,
        email_address text NOT NULL DEFAULT '',
        use_studio_mode integer NOT NULL DEFAULT 0
);

INSERT INTO users2
SELECT user_id, name, given_name, family_name, locale, ace_theme, use_auto_complete, enable_vim, email_address, use_studio_mode
FROM users;

DROP TABLE users;

ALTER TABLE users2 RENAME TO users
