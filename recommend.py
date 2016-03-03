import similarity
import db
import json

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
    if movieid not in dic: dic.setdefault(movieid,1)
    else: dic[movieid] += neighbors_map[userid]
  return dic

def hash2list(map):
  sort_tag = []
  for tag in map: sort_tag.append([map[tag],tag])
  sort_tag.sort()
  sort_tag.reverse()
  return sort_tag

def list2hash(list):
  hashmap = {}
  for l in list:
    (count,item) = l[:]
    hashmap[item] = count
  return hashmap


# user_based recommend

def get_topic_sim_matrix():
  matrix = {}
  for i in range(60):
    path = 'user_similarity/'+str(i)+".txt"
    sim_i = json.load(file(path))
    matrix.update(sim_i)
    print i
  return matrix

global_sim_matrix = get_topic_sim_matrix()
def get_user_neighbors(userid,top):
  user_rank = []
  for other in db_info.user_list:
    if other == userid: continue
    key1 = str((userid,other))
    key2 = str((other,userid))
    if key1 in global_sim_matrix:
      user_rank.append([global_sim_matrix[key1],other])
    elif key2 in global_sim_matrix:
      user_rank.append([global_sim_matrix[key2],other])
    else: print "can not find similarity between"+ key1
  user_rank.sort(reverse=True)
  neighbor_sim_map = {u[1]:u[0] for u in user_rank[0:top]}
  return neighbor_sim_map


def recommend_for_user(userid,top_neighbor=30,top_movie=50):
  neighbors_map = get_user_neighbors(userid,top_neighbor)
  neighbors = tuple(neighbors_map.keys())
  neighbor_movies = db.get_movie_from_users(neighbors)
  movies_count = list_count(neighbor_movies,neighbors_map)
  movies_count = filter_item_for_user(movies_count,userid)
  candidate_list = hash2list(movies_count)
  recommend_list = [candidate_list[i][1] for i in range(0,top_movie)]
  return recommend_list


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