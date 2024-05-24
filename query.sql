-- CREATE DATABASE songspot;

USE songspot;

DROP TABLE IF EXISTS songs;

CREATE TABLE songs(
    song_id     varchar(64) not null,
    track_name  varchar(128) not null,
    artist      varchar(128) not null,
    PRIMARY KEY (song_id),
    UNIQUE      (song_id)
);

INSERT INTO songs(song_id, track_name, artist)
    values('ididid', 'song name', 'artist name');

SELECT * FROM songs;