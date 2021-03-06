import similarity
import db
import json
import util
from pureSVD import PureSVDPredictor
# from ranker import Ranker

db_info = db.info()


def filter_item_for_user(origin_items,userid):
  dic_copy = dict(origin_items)
  for m in origin_items:
      if m in db_info.user_train_movies(userid):
        del dic_copy[m]
  return dic_copy

def list_count(tuple_list,neighbors_map):
  dic = {}
  for t in tuple_list:
    (userid,movieid) = t[:]
    if movieid not in dic: dic[movieid] = neighbors_map[userid]
    else: dic[movieid] += neighbors_map[userid]
  return dic


# user_based recommend

def get_topic_sim_matrix(topics):
  matrix = {}
  for i in range(60):
    path = 'user_similarity/user_topic_sim/'+str(topics)+'_topics/'+str(i)+".pickle"
    matrix.update(util.read_file(path))
    print i
  return matrix

def get_tag_sim_matrix():
  matrix = {}
  for i in range(60):
    path = 'user_similarity/user_tag_sim/genres/'+str(i)+".pickle"
    matrix.update(util.read_file(path))
    print i
  return matrix

def save_user_sim_matrix(topics):
  for i in range(60):
    topic_path = 'user_similarity/user_topic_sim/'+str(topics)+'_topics/'+str(i)+".pickle"
    tag_path = 'user_similarity/user_tag_sim/'+str(i)+".pickle"
    topic_i = util.read_file(topic_path)
    tag_i = util.read_file(tag_path)
    for t in topic_i:
      topic_i[t] = topic_i[t]*tag_i[t]
    path = 'user_similarity/user_sim/'+str(topics)+'_hybrid/'+str(i)+".pickle"
    util.write_file(topic_i,path)

def get_user_sim_matrix(topics):
  matrix = {}
  for i in range(60):
    path = 'user_similarity/user_sim/'+str(topics)+'_hybrid/'+str(i)+".pickle"
    matrix.update(util.read_file(path))
    print i
  return matrix

def get_user_neighbors(userid,top):
  user_rank = []
  for other in db_info.user_list:
    if other == userid: continue
    key = (userid,other) if userid<other else (other,userid)
    if key in global_sim_matrix:
      user_rank.append([global_sim_matrix[key],other])
    else: print "can not find similarity between"+ str(key)
  user_rank.sort(reverse=True)
  neighbor_sim_map = {u[1]:u[0] for u in user_rank[0:top]}
  return neighbor_sim_map

# ranker = Ranker(10)
def recommend_for_user(userid,top_neighbor,top_movie,x):
  neighbors_map = get_user_neighbors(userid,top_neighbor)
  neighbors = tuple(neighbors_map.keys())
  neighbor_movies = db.get_movie_from_users(neighbors)
  # movies_count = list_count(neighbor_movies,neighbors_map)
  # movies_count = filter_item_for_user(movies_count,userid)
  # candidate_list = util.hash2list(movies_count)
  # recommend_list = [candidate_list[i][1] for i in range(0,top_movie)]
  
  candidate_list = util.hash2list(score_items(userid,neighbors_map,neighbor_movies,x))
  recommend_list = [candidate_list[i][1] for i in range(len(candidate_list))]

  # item_ids = get_candidate_item_list(userid,neighbor_movies)
  # ratings = recommender.get_ratings(userid, item_ids)
  # recommendations = ranker.maximizeKGreatItems(top_movie, ratings, db_info.movie_user_ratings)
  # recommend_list = [r[1] for r in recommendations]
  return recommend_list[:top_movie]

def get_candidate_item_list(current_user,record_list):
  current_user_movies = db_info.user_train_movies(current_user)
  item_dir = {}
  for r in record_list:
    (userid,movieid) = r[:]
    if movieid not in current_user_movies:
      if movieid not in item_dir: item_dir[movieid] = 0
  return item_dir.keys()

def score_items(current_user,neighbors_map,record_list,n=0):
  dic = {}
  current_user_movies = db_info.user_train_movies(current_user)
  for r in record_list:
    (userid,movieid) = r[:]
    if movieid not in current_user_movies:
      cur_relative = recommender.get_score(current_user,movieid)
      u_relative = recommender.get_score(userid,movieid)
      score = n*neighbors_map[userid]*u_relative + (1-n)*cur_relative
      if movieid not in dic: dic[movieid] = score
      else: dic[movieid] += score
  return dic


def main(method='tag',topics=70,features=50):
  global global_sim_matrix
  global recommender
  training_items = db_info.movie_user_ratings
  training_users = db_info.train_ratings_set
  recommender = PureSVDPredictor(training_items, training_users, features)
  if method == 'tag':
    global_sim_matrix = get_tag_sim_matrix()
  elif method == 'lda':
    global_sim_matrix = get_topic_sim_matrix(topics)
  elif method == 'hybrid':
    global_sim_matrix = get_user_sim_matrix(topics)


# item_based recommendation

def get_movie_sim_matrix():
  matrix = {}
  for i in range(20):
    path = 'movie_similarity/'+str(i)+".txt"
    sim_i = json.load(file(path))
    matrix.update(sim_i)
    print i
  return matrix

# movie_sim_matrix = get_movie_sim_matrix()
def get_movie_neighbors(movieid,top):
  movie_rank = []
  for other in db_info.movie_list():
    if other == movieid: continue
    key1 = str((movieid,other))
    key2 = str((other,movieid))
    if key1 in movie_sim_matrix:
      movie_rank.append([movie_sim_matrix[key1],other])
    elif key2 in movie_sim_matrix:
      movie_rank.append([movie_sim_matrix[key2],other])
    # else: print "can not find similarity between"+ key1
  movie_rank.sort(reverse=True)
  neighbor_sim_map = {m[1]:m[0] for m in movie_rank[0:top]}
  return neighbor_sim_map


def item_recommend_for_user(userid,top_neighbor=30,top_movie=50):
  user_movies = db_info.user_train_movies(userid)
  movie_rate = {}
  for m in user_movies:
    neighbors = get_movie_neighbors(m,top_neighbor)
    for movie in neighbors:
      if movie in user_movies: continue
      if movie in movie_rate:
        movie_rate[movie] += neighbors[movie]
      else:
        movie_rate[movie] = neighbors[movie]
  candidate_list = hash2list(movie_rate)
  recommend_list = [candidate_list[i][1] for i in range(0,top_movie)]
  return recommend_list