-- Table definitions for the tournament project.
-- TODO: Consider using limited-length types for 'name' fields. This appears to be
-- the convention in the PostgreSQL docs. Perhaps to save memory?
-- TODO: The schema at the moment has no notion of match order. This means tournament
-- results must be built procedurally and are time-sensitive. Perhaps matches could be
-- time-stamped to rectify this limitation?

-- Boilerplate to ensure we are setting-up the correct database.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

-- All players registered to the tournament service.
CREATE TABLE players (
    id   serial PRIMARY KEY,
    name text NOT NULL
);

-- All tournaments registered to the service.
-- Player counts are ensured to have an even amount of players. Perhaps this is not
-- a good constraint to impose at database level, but we include it to play around
-- with the CHECK constraint.
CREATE TABLE tournaments (
    id           serial PRIMARY KEY,
    name         text NOT NULL
);

-- Create the default tournament for the sake of the tests.
INSERT INTO tournaments (name)
    VALUES ('default');

-- Players in each tournament.
CREATE TABLE tournament_players (
    player_id     int NOT NULL REFERENCES players (id),
    tournament_id int NOT NULL REFERENCES tournaments (id),
    PRIMARY KEY (player_id, tournament_id)
);

-- All the matches of every tournament.
CREATE TABLE matches (
    id            serial PRIMARY KEY,
    tournament_id int NOT NULL REFERENCES tournaments (id)
);

-- Results of each of the matches.
CREATE TABLE match_results (
    match_id  int NOT NULL REFERENCES matches (id),
    player_id int NOT NULL REFERENCES players (id),
    score     int NOT NULL,
    -- Prevent players from being duplicated for the same match.
    PRIMARY KEY (match_id, player_id)
);

-- Names of the players and the names of the tournaments they are entered in.
CREATE VIEW player_tournament_names AS
    SELECT players.name AS player_name, tournaments.name AS tournament_name
        FROM tournament_players, players, tournaments
        WHERE tournament_players.player_id = players.id
        AND tournament_players.tournament_id = tournaments.id;

-- Number of players registered.
CREATE VIEW player_count AS
    SELECT count(*) AS num
        FROM players;

-- Number of players in each tournament.
CREATE VIEW tournaments_player_count AS
    SELECT tournament_id, count(*) AS num
        FROM tournament_players
        GROUP BY tournament_id;
