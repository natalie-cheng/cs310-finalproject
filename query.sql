-- CREATE DATABASE songspot;

USE songspot;

-- DROP TABLE IF EXISTS songs;

-- CREATE TABLE songs(
--     song_id     varchar(64) not null,
--     track_name  varchar(128) not null,
--     artist      varchar(128) not null,
--     PRIMARY KEY (song_id),
--     UNIQUE      (song_id)
-- );

-- INSERT INTO songs(song_id, track_name, artist)
--     values('ididid', 'song name', 'artist name');

SELECT * FROM songs;

-- DROP USER IF EXISTS 'songspot-read-only';
-- DROP USER IF EXISTS 'songspot-read-write';

-- CREATE USER 'songspot-read-only' IDENTIFIED BY 'abc123!!';
-- CREATE USER 'songspot-read-write' IDENTIFIED BY 'def456!!';

-- GRANT SELECT, SHOW VIEW ON songspot.*
--     TO 'songspot-read-only';

-- GRANT SELECT, SHOW VIEW, INSERT, UPDATE, DROP, CREATE, DELETE ON songspot.*
--     TO 'songspot-read-write';

-- FLUSH PRIVILEGES;