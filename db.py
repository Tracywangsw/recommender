import psycopg2

def get_cursor():
  conn_str = "host='localhost' dbname='movies' user='dbuser' password='dbuser'"
  # conn_str = "host='localhost' dbname='movielen_1M' user='python' password='python'"
  conn = psycopg2.connect(conn_str)
  cursor = conn.cursor()
  return cursor

def record_count(records):
  records_count = {}
  for r in records:
    (key_item,count_item) = r[:]
    if key_item in records_count:
      if count_item in records_count[key_item]: records_count[key_item][count_item] += 1
      else: records_count[key_item][count_item] = 1
    else: records_count.setdefault(key_item,{count_item:1})
  return records_count

def get_mv_plots():
  cursor = get_cursor()
  cursor.execute("select movieid,plot from plots")
  return_list = cursor.fetchall()
  mv_plots = {r[0]:r[1] for r in return_list}
  return mv_plots

def get_train_ratings():
  cursor = get_cursor()
  cursor.execute("select userid,movieid from rating_train")
  return_list = cursor.fetchall()
  train_rating = record_count(return_list)
  return train_rating

def get_test_ratings():
  cursor = get_cursor()
  cursor.execute("select userid,movieid from rating_test")
  return_list = cursor.fetchall()
  test_rating = record_count(return_list)
  return test_rating

def split_item(item):
  l = len(item)
  item_list = []
  for i in range(l):
    for j in range(i+1,l):
      item_list.append([item[i],item[j]])
  return item_list

def get_movie_from_users(user_list):
  tuple_str = str(user_list)
  cursor = get_cursor()
  cursor.execute("select userid,movieid from rating_train where userid in "+ tuple_str)
  return_list = cursor.fetchall()
  return return_list

def movieid_plot_map(return_list):
  mv_plot = {}
  for r in return_list:
    (mvid,plot) = (r,return_list[r])
    if plot:
      if type(plot) is tuple:
        plot_str = ''
        for p in plot:
          if p: plot_str += p
        mv_plot[mvid] = plot_str
      else: mv_plot[mvid] = plot
    # else: print str(mvid)+": has no plots"
  return mv_plot

class info():
  def __init__(self):
    self.mv_plots_set = get_mv_plots()
    self.train_ratings_set = get_train_ratings()
    self.user_list = self.train_ratings_set.keys()
    self.test_ratings_set = get_test_ratings()

  def user_train_movies(self,userid):
    return self.train_ratings_set[userid].keys()

  def movie_tags(self,movieid):
    if movieid in self.mv_tags_set:
      return self.mv_tags_set[movieid]
    return {}

  def movie_plot(self,movieid):
    return self.mv_plots_set[movieid]

  def user_test_movies(self,userid):
    return self.test_ratings_set[userid].keys()

def main():
  i = info()
  c = [len(i.user_test_movies(u)) for u in i.user_list]
  return c
