import psycopg2
import util

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

def get_tag_name_set():
  cursor = get_cursor()
  cursor.execute("select tagid,tag from tags")
  return_list = cursor.fetchall()
  tag_info = {r[0]:r[1] for r in return_list}
  return tag_info

def get_movie_info():
  cursor = get_cursor()
  cursor.execute("select movieid,genres from movies where movieid in (select distinct movieid from ratings)")
  return_list = cursor.fetchall()
  movie_info = {r[0]:r[1] for r in return_list}
  return movie_info

def get_user_tag():
  cursor = get_cursor()
  cursor.execute("select userid,movieid,tagid")

def movie_train_ratings():
  cursor = get_cursor()
  cursor.execute("select movieid,avg(rating),count(rating) from rating_train group by movieid order by avg(rating)")
  return_list = cursor.fetchall()
  movie_ratings_set = {r[0]:[r[1],r[2]] for r in return_list}
  return movie_ratings_set

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
    self.movie_info = get_movie_info()
    self.train_movie = movie_train_ratings()
    # self.tag_set = get_movie_tags_set()

  # def movie_list(self):
  #   return self.mv_plots_set.keys()

  # def movie_plot(self,movieid):
  #   return self.mv_plots_set[movieid]

  def user_train_movies(self,userid):
    return self.train_ratings_set[userid]

  def user_test_movies(self,userid):
    return self.test_ratings_set[userid].keys()
    # return self.test_ratings_set[userid]
  
  def movie_genres(self,movieid):
    genres = self.movie_info[movieid]
    if "|" in genres: return genres.split('|')
    return None

  def movie_tag_relevance(self,movieid):
    if movieid in self.tag_set:
      return self.tag_set[movieid]
    return {}

  def get_movie_info(self,movieid):
    return self.train_movie[movieid]

class tags_info():
  def __init__(self):
    self.set = get_tag_name_set()

  def get_name_by_id(tagid):
    return self.set[tagid]

class movie_data_profile():
  """do research on data"""
  def __init__(self):
    self.train_movie = movie_train_ratings()
    self.hot_list = self.hot_movies()
  
  def get_movie_info(self,mvid):
    return self.train_movie[mvid]

  def hot_movies(self,rate=4.0,users=50):
    hot_list = []
    for m in self.train_movie:
      (avg_rating,count) = self.train_movie[m][:]
      if avg_rating >= rate and count > users:
        hot_list.append(m)
    return hot_list

i = info()
movie = movie_data_profile()
def user_alanysis(userid):
  user_test_list = i.user_test_movies(userid)
  user_movies_set = i.user_train_movies(userid)
  user_movie_list = user_movies_set.keys()
  user_avg_rating = sum(user_movie_list)/len(user_movie_list)
  record_list = []
  k = 0
  j = 0
  for m in user_movie_list:
    if m in movie.hot_list: k += 1
  for m in user_test_list:
    if m in movie.hot_list: j += 1
    # rlist = []
    # rlist.append(userid)
    # rlist.append(user_movies_set[m])
    # rlist.append(movie.get_movie_info(m))
    # rlist.append(k)
    # record_list.append(rlist)
  # j = sum([m for m in user_test_list if m in movie.hot_list])
  rate_train = float(k)/len(user_movie_list)
  rate_test = float(j)/len(user_test_list)
  record_list.append([userid,k,rate_train,j,rate_test])
  # record_list.append(k)
  return record_list

def test():
  test_list = get_user_list()
  return_list = []
  for u in test_list:
    print u
    return_list.extend(user_alanysis(u))
  util.write_file(return_list,type='csv',path='user_info/whole_users_add_test.csv')


def main():
  i = info()
  c = [len(i.user_test_movies(u)) for u in i.user_list]
  return c
