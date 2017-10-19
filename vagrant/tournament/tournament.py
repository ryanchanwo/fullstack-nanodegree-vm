#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import itertools

import bleach
import psycopg2

_connection_name = "dbname=tournament"


# Taken from stack overflow:
# https://stackoverflow.com/questions/5389507/iterating-over-every-two-elements-in-a-list
def pairwise(iterable):
    a = iter(iterable)
    return itertools.izip(a, a)


def connect():
    """Connect to the PostgreSQL database. Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    with psycopg2.connect(_connection_name) as connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE match_results CASCADE;")
        cursor.execute("TRUNCATE matches CASCADE;")


def deletePlayers():
    """Remove all the player records from the database."""
    with psycopg2.connect(_connection_name) as connection:
        cursor = connection.cursor()
        # This is a bit cumbersome, if the players are removed, we need to also
        # remove their match_results. On deleting the results however, we also
        # need to delete the matches for those results, otherwise we are left
        # with 'zombie' matches (that have no results).
        # TODO: Improve this.
        cursor.execute("DELETE FROM tournament_players RETURNING player_id;")
        deleted_player_ids = cursor.fetchall()

        deleted_match_ids = []
        for player_id in deleted_player_ids:
            cursor.execute("""\
DELETE FROM match_results
    WHERE player_id = %s
    RETURNING match_id;\
""", player_id)

            match_id = cursor.fetchone()
            if match_id:
                deleted_match_ids.append(match_id)

        if deleted_match_ids:
            cursor.executemany("DELETE FROM matches WHERE id = %s;",
                               deleted_match_ids)

        if deleted_player_ids:
            cursor.executemany("DELETE FROM players WHERE id = %s;",
                               deleted_player_ids)


def countPlayers():
    """Returns the number of players currently registered."""
    count = None

    with psycopg2.connect(_connection_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT num FROM player_count;")
        count, = cursor.fetchone()

    if count is None:
        # TODO: Error out.
        pass

    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    # FIXME: At the moment, we automatically enter all players into the
    # 'default' tournament. Once the service has been extended to add
    # tournaments, we can additionally enter players to specific tournaments.
    with psycopg2.connect(_connection_name) as connection:
        cursor = connection.cursor()
        cursor.execute("""\
INSERT INTO players (name)
    VALUES (%s)
    RETURNING id;\
""", (bleach.clean(name), ))

        player_id, = cursor.fetchone()
        cursor.execute("""\
INSERT INTO tournament_players (player_id, tournament_id)
    VALUES (%s, 1);\
""", (player_id, ))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    standings = None

    with psycopg2.connect(_connection_name) as connection:
        cursor = connection.cursor()
        cursor.execute("""\
SELECT tournament_players.player_id,
    players.name,
    coalesce(sum(player_matches.score), 0) AS score,
    count(player_matches) AS match_count

    FROM tournament_players
    LEFT JOIN (
        -- Subquery to build a table representing all the player's matches and
        -- scores in the given tournament.
        SELECT player_id, score
        FROM matches, match_results
        WHERE matches.id = match_results.match_id
            AND matches.tournament_id = 1
    ) AS player_matches
        ON (tournament_players.player_id = player_matches.player_id)
    JOIN players
        ON (tournament_players.player_id = players.id)

    WHERE tournament_id = 1
    GROUP BY tournament_players.player_id, players.name
    ORDER BY score DESC;\
""")
        standings = cursor.fetchall()

    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner: the id number of the player who won
      loser: the id number of the player who lost
    """
    with psycopg2.connect(_connection_name) as connection:
        cursor = connection.cursor()

        # Add a new match.
        cursor.execute("""\
INSERT INTO matches (tournament_id)
    VALUES (1)
    RETURNING id;\
""")
        match_id, = cursor.fetchone()

        # Record the results of the match for both players.
        winner_entry = (match_id, int(winner), 1, )
        loser_entry = (match_id, int(loser), 0, )
        cursor.executemany("""\
INSERT INTO match_results (match_id, player_id, score)
    VALUES (%s, %s, %s);\
""", (winner_entry, loser_entry, ))


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()

    pairings = []
    for player_one, player_two in pairwise(standings):
        # Each player in the standings are represented by a tuple of 4 values.
        # The first two are the name and their id.
        pairings.append(player_one[0:2] + player_two[0:2])

    return pairings
