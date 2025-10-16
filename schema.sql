-- ==============================================================================
-- File: schema.sql
-- This file contains the SQL command to create the 'users' table.
-- You will need to run this command in your PostgreSQL client to set up the database.
-- ==============================================================================
CREATE TABLE users (
  id serial PRIMARY KEY,
  username varchar(255) NOT NULL UNIQUE,     -- Username
  hashed_password varchar(255) NOT NULL      -- Password (hashed, not plain-text)
);

CREATE TABLE joke (
  joke_id serial PRIMARY KEY,
  joke varchar(2056),
  user_id int,
  CONSTRAINT FK_users FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE artist (
  artist_id serial PRIMARY KEY,
  artist_name varchar(256),
  followers int,
  artist_spotify_id varchar(256) NOT NULL UNIQUE
);

CREATE TABLE artist_users (
  user_id int,
  artist_id int,
  CONSTRAINT PK_artist_users PRIMARY KEY (user_id, artist_id),
  CONSTRAINT FK_users FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT FK_artist FOREIGN KEY (artist_id) REFERENCES artist(artist_id)
);

