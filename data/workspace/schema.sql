USE wikipedia;

CREATE TABLE IF NOT EXISTS instance (
    instance_id bigint NOT NULL AUTO_INCREMENT,
    instance_name text NOT NULL,
    PRIMARY KEY (instance_id)
);

CREATE TABLE IF NOT EXISTS multistream_data (
    page_id int unsigned NOT NULL,
    body longtext NOT NULL,
    markdown_text longtext NOT NULL,
    PRIMARY KEY (page_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id)
);

CREATE TABLE IF NOT EXISTS target_entities (
    page_id int unsigned NOT NULL,
    entity_type int NOT NULL,
    PRIMARY KEY (page_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id)
);

CREATE TABLE IF NOT EXISTS target_news_entries (
    id bigint NOT NULL AUTO_INCREMENT,
    page_id int unsigned NOT NULL,
    url text NOT NULL,
    title text NOT NULL,
    full_text longtext NOT NULL,
    markdown_text longtext NOT NULL,
    PRIMARY KEY (id),
    INDEX (page_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id)
);

CREATE TABLE IF NOT EXISTS results (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
    instance_id bigint NOT NULL,
    page_id int unsigned NOT NULL,
    canceled bit NOT NULL,
    confidence float NOT NULL,
    rationale mediumtext NOT NULL,
    revolvable bit NOT NULL,
    penance mediumtext NULL,

    PRIMARY KEY (id),
    UNIQUE KEY (instance_id, page_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id)
)