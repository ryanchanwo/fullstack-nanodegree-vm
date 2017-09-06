# "Database code" for the DB Forum.
import datetime

import bleach
import psycopg2


def get_posts():
  """Return all posts from the 'database', most recent first."""
  database = psycopg2.connect("dbname=forum")
  cursor = database.cursor()

  cursor.execute("SELECT content, time FROM posts ORDER BY time DESC;")

  posts = cursor.fetchall()
  database.close()
  return [(bleach.clean(content), time, ) for content, time in posts]


def add_post(content):
  """Add a post to the 'database' with the current timestamp."""
  database = psycopg2.connect("dbname=forum")
  cursor = database.cursor()

  time = datetime.datetime.now()
  cursor.execute("INSERT INTO posts (content) VALUES (%(content)s);",
                 {"content": bleach.clean(content), })

  database.commit()
  database.close()
