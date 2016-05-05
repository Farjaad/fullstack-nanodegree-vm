#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = psycopg2.connect("dbname=tournament")
    cur = DB.cursor()
    cur.execute("delete from match_results;")
    DB.commit()
    DB.close()

def deletePlayers():
    """Remove all the player records from the database."""
    DB = psycopg2.connect("dbname=tournament")
    cur = DB.cursor()
    cur.execute("delete from players;")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = psycopg2.connect("dbname=tournament")
    cur = DB.cursor()
    cur.execute("SELECT COUNT (*) FROM players;")
    results = cur.fetchall()
    DB.close()
    return results[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    DB = psycopg2.connect("dbname=tournament")
    cur = DB.cursor()
    cur.execute("INSERT INTO players (name) VALUES (%s);", (bleach.clean(name),))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.
    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.
    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = psycopg2.connect("dbname=tournament")
    cur = DB.cursor()
    cur.execute("select players.id, players.name, "
                   "count((select match_results.winner from match_results where match_results.winner = players.id)) as win, "
                   "count(match_results.winner ) as games "
                   "from players  left join match_results on "
                   "players.id= match_results.winner or players.id = match_results.loser  group by players.id")
    results = cur.fetchall()
    DB.close()
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.
    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = psycopg2.connect("dbname=tournament")
    cur = DB.cursor()
    cur.execute("INSERT INTO match_results (winner, loser) VALUES ((%s), (%s))", (winner, loser))
    DB.commit()
    DB.close()
    return
 
 
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
    conn = connect()
    c = conn.cursor()
    c.execute("select id from (select * from players order by wins desc) as id;")
    ids = c.fetchall()
    c.execute("select name from (select * from players order by wins desc) as names;")
    names = c.fetchall()
    conn.commit() 
    conn.close()

    l = len(ids)/2
    a=1
    x=0
    f=[]

    while a <= l:

        m = ids[x][0], names[x][0], ids[x+1][0], names[x+1][0]
        f.append(m)
        x  =x+2
        a=a+1


