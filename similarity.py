import lda
import db
import datetime
import numpy as np
import scipy.stats as stats
import multiprocessing as mp
import math
import pdb
import json
import load_topic_files

db_info = db.info()
movie_topics_map = load_topic_files.main()

class user_topics(object):
  """find user concerning topics with the plots of movies the user likes"""
  def __init__(self,userid):
    super(user_topics, self).__init__()
    self.userid = userid

  def get_user_topics(self):
    user_topics_vector = np.array([0]*50)
    user_ratings = db_info.user_train_movies(self.userid)
    rating_sum = sum([user_ratings[m] for m in user_ratings])
    for m in user_ratings:
      if m in movie_topics_map:
        normalize = user_ratings[m]/rating_sum
        # movie_vector = [normalize*movie_topics_map[i] for i in movie_topics_map]
        # user_topics_list = map(sum,zip(user_topics_list,movie_vector))
        movie_vector = np.array(movie_topics_map[m])
        user_topics_vector = user_topics_vector+normalize*movie_vector
    return list(user_topics_vector)

def get_user_topic_map(model):
  topic_map = {}
  for u in db_info.user_list:
    topic_map[u] = user_topics(u).get_user_topics(model)
    print u
  return topic_map

def topic_sim(topic_a,topic_b):
  kl = kl_divergence(topic_a,topic_b)
  return math.exp(-1*kl)

def kl_divergence(p,q):
  return np.sum([stats.entropy(p,q),stats.entropy(q,p)])

# user_topic_map = get_user_topic_map(model)
def topic_sim_matrix(person,other,person_topic,other_topic):
  sim_matrix = {}
  # topic_person = user_topic_map[person]
  # topic_other = user_topic_map[other]
  sim_matrix[str((person,other))] = topic_sim(person_topic,other_topic)
  print sim_matrix
  return sim_matrix

def multiprocess(processes,model,user_list_list,user_topic_map):
  pool = mp.Pool(processes=processes)
  # user_topic_map = get_user_topic_map(model)
  results = [pool.apply_async(topic_sim_matrix, args=(l[0],l[1],user_topic_map[l[0]],user_topic_map[l[1]])) for l in user_list_list]
  dest = dict(results[0].get())
  for r in range(1,len(results)):
    dest.update(results[r].get())
  return dest

def calulate_user_similarity(lda_path,sim_path,processes):
  lda_loaded_model = lda.load_lda(lda_path)
  user_list = db_info.user_list
  user_list_list = db.split_item(user_list)
  user_topic_map = get_user_topic_map(lda_loaded_model)
  results = multiprocess(processes,lda_loaded_model,user_list_list,user_topic_map)
  json.dump(results,open(path,'w'))

def main():
  lda_path = 'lda_model/50_topics.txt'
  sim_path = 'sim_matrix/topic_sim(50).txt'
  calulate_user_similarity(lda_path,sim_path,4)