import psycopg2

def get_cursor():
  conn_str = "host='localhost' dbname='movie' user='postgres' password='iswear'"
  # conn_str = "host='localhost' dbname='movielen_1M' user='python' password='python'"
  conn = psycopg2.connect(conn_str)
  cursor = conn.cursor()
  return cursor

def user_movie_rating_map(records):
  res_map = {}
  for r in records:
    (userid,movieid,rating) = r[:]
    if userid not in res_map:
      res_map[userid] = {movieid:rating}
    else:
      if movieid not in res_map[userid]:
        res_map[userid][movieid] = rating
      else:
        print "user rating repeat!!"
  return res_map

def get_mv_plots():
  cursor = get_cursor()
  cursor.execute("select movieid,plot from plots where movieid in (select distinct movieid from ratings)")
  return_list = cursor.fetchall()
  mv_plots = {r[0]:r[1] for r in return_list}
  return mv_plots

def get_train_ratings():
  cursor = get_cursor()
  cursor.execute("select userid,movieid,rating from rating_train")
  return_list = cursor.fetchall()
  train_rating = user_movie_rating_map(return_list)
  return train_rating

def get_test_ratings():
  cursor = get_cursor()
  cursor.execute("select userid,movieid,rating from rating_test")
  return_list = cursor.fetchall()
  test_rating = user_movie_rating_map(return_list)
  return test_rating

def get_movie_from_users(user_list):
  tuple_str = str(user_list)
  cursor = get_cursor()
  cursor.execute("select userid,movieid from rating_train where userid in "+ tuple_str)
  return_list = cursor.fetchall()
  return return_list

def get_movie_tags_set():
  cursor = get_cursor()
  cursor.execute("select movieid,tagid,relevance from tag_relevance where movieid in (select distinct movieid from ratings)")
  return_list = cursor.fetchall()
  tag_relevance = user_movie_rating_map(return_list)
  return tag_relevance

def get_user_list():
  cursor = get_cursor()
  cursor.execute("select distinct userid from ratings order by userid")
  return_list = cursor.fetchall()
  user_list = [r[0] for r in return_list]
  return user_list

def split_item(item):
  l = len(item)
  item_list = []
  for i in range(l):
    for j in range(i+1,l):
      item_list.append([item[i],item[j]])
  return item_list

class info():
  def __init__(self):
    # self.mv_plots_set = get_mv_plots()
    self.train_ratings_set = get_train_ratings()
    self.user_list = self.train_ratings_set.keys()
    self.test_ratings_set = get_test_ratings()
    self.tag_set = get_movie_tags_set()

  # def movie_list(self):
  #   return self.mv_plots_set.keys()

  # def movie_plot(self,movieid):
  #   return self.mv_plots_set[movieid]

  def user_train_movies(self,userid):
    return self.train_ratings_set[userid]

  def user_test_movies(self,userid):
    return self.test_ratings_set[userid].keys()

  def movie_tag_relevance(self,movieid):
    if movieid in self.tag_set:
      return self.tag_set[movieid]
    return {}


def main():
  i = info()
  c = [len(i.user_test_movies(u)) for u in i.user_list]
  return c
