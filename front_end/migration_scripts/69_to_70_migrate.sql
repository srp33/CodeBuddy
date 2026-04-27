CREATE TABLE lti_registrations (
    registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL,
    issuer TEXT NOT NULL,
    client_id TEXT NOT NULL,
    auth_login_url TEXT NOT NULL,
    auth_token_url TEXT NOT NULL,
    key_set_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(issuer, client_id)
);

CREATE TABLE lti_deployments (
    deployment_id TEXT PRIMARY KEY,
    registration_id INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES lti_registrations (registration_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE lti_launch_state (
    state TEXT PRIMARY KEY,
    nonce TEXT NOT NULL,
    registration_id INTEGER NOT NULL,
    target_link_uri TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES lti_registrations (registration_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_lti_launch_state_expires_at ON lti_launch_state (expires_at);

CREATE TABLE lti_user_links (
    deployment_id TEXT NOT NULL,
    lti_sub TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(deployment_id, lti_sub),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_lti_user_links_user_id ON lti_user_links (user_id);

CREATE TABLE lti_resource_links (
    deployment_id TEXT NOT NULL,
    context_id TEXT NOT NULL,
    resource_link_id TEXT NOT NULL,
    course_id INTEGER,
    assignment_id INTEGER,
    lineitem_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(deployment_id, context_id, resource_link_id)
);

CREATE INDEX idx_lti_resource_links_course_assignment ON lti_resource_links (course_id, assignment_id);
