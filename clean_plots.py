import psycopg2
from imdb import IMDb

def get_cursor():
  conn_str = "host='localhost' dbname='movies' user='dbuser' password='dbuser'"
  # conn_str = "host='localhost' dbname='movielen_1M' user='python' password='python'"
  conn = psycopg2.connect(conn_str)
  cursor = conn.cursor()
  return cursor

class db_handler():
  def __init__(self):
    self.cursor = get_cursor()

  def get_missing_plots_movies(self):
    self.cursor.execute("select distinct movieid from ratings where movieid not in(select distinct movieid from plots)")
    return_list = self.cursor.fetchall()
    movieid_list = [r[0] for r in return_list]
    return movieid_list

  def get_movie_imdbid_map(self):
    self.cursor.execute("select movieid,imdbid from links")
    movie_imdb_list = self.cursor.fetchall()
    md_map = {r[0]:r[1] for r in movie_imdb_list}
    return md_map

  def get_movie_list(self):
    self.cursor.execute("select distinct movieid from plots")
    return_list = self.cursor.fetchall()
    movieid_list = [r[0] for r in return_list]
    return movieid_list

  def insert_plot(self,ilist):
    (movieid,imdbid,plot) = ilist[:]
    mv_list = self.get_movie_list()
    conn_str = "host='localhost' dbname='movies' user='dbuser' password='dbuser'"
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    if movieid in mv_list:
      cursor.execute("update plots set plot = '"+plot+"' where imdbid='"+str(imdbid)+"'")
    else:
      cursor.execute("insert into plots(movieid,imdbid,plot) values("+str(movieid)+",'"+str(imdbid)+"','"+plot+"')")
    conn.commit()


def get_plot():
  db = db_handler()
  mv_list = db.get_missing_plots_movies()
  md_map = db.get_movie_imdbid_map()
  for m in mv_list:
    if m in md_map:
      movie = IMDb().get_movie(md_map[m])
      plot = movie.get('plot')
      # print [m,md_map[m],plot]
      if plot:
        plot_str = ''
        for p in plot: plot_str += p
        plot_str = plot_str.replace("\'", "")
        plot_str = plot_str.replace("\"", "")
        print m
        print plot_str
        rlist = [m,md_map[m],plot_str]
        db.insert_plot(rlist)
    else:
      print m
