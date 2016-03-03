import lda
import db
import datetime
import numpy as np
import scipy.stats as stats
import multiprocessing as mp
import math
import util
import json
import load_topic_files
import csv
import pickle

db_info = db.info()
movie_topics_map = load_topic_files.main()

def topic_sim(topic_a,topic_b):
  kl = kl_divergence(topic_a,topic_b)
  return math.exp(-1*kl)

def kl_divergence(p,q):
  return np.sum([stats.entropy(p,q),stats.entropy(q,p)])


# user-movie-topic
#       ||
# user-similarity

def get_user_topics(userid):
  user_topics_vector = np.array([0]*50)
  user_ratings = db_info.user_train_movies(userid)
  rating_sum = sum([user_ratings[m] for m in user_ratings])
  for m in user_ratings:
    if m in movie_topics_map:
      normalize = user_ratings[m]/rating_sum
      movie_vector = np.array(movie_topics_map[m])
      user_topics_vector = user_topics_vector+normalize*movie_vector
  return list(user_topics_vector)

def get_user_topic_map():
  topic_map = {}
  for u in db_info.user_list:
    topic_map[u] = get_user_topics(u)
    print u
  return topic_map

def topic_sim_matrix(person,other,person_topic,other_topic):
  sim_matrix = {}
  sim_matrix[(person,other)] = topic_sim(person_topic,other_topic)
  print sim_matrix
  return sim_matrix

def multiprocess(processes,user_list_list,user_topic_map):
  pool = mp.Pool(processes=processes)
  results = [pool.apply_async(topic_sim_matrix, args=(l[0],l[1],user_topic_map[l[0]],user_topic_map[l[1]])) for l in user_list_list]
  dest = dict(results[0].get())
  for r in range(1,len(results)):
    dest.update(results[r].get())
  pool.close()
  pool.join()
  return dest

def calulate_user_similarity(processes):
  user_list = db_info.user_list
  user_list_list = db.split_item(user_list)
  user_topic_map = get_user_topic_map()
  node = len(user_list_list)/60
  for i in range(60):
    exe_list = user_list_list[i*node:(i+1)*node]
    results = multiprocess(processes,exe_list,user_topic_map)
    path = 'user_similarity/user_topic_sim/' + str(i) + '.pickle'
    # with open(path,'w') as f:
    #   pickle.dump(results,f,pickle.HIGHEST_PROTOCOL)
    #   f.close()
    util.write_file(results,path)



def main():
  calulate_user_similarity(4)