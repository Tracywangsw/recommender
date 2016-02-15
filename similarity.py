import lda
import db
import datetime
import numpy as np
import scipy.stats as stats
import multiprocessing as mp
import math
import pdb
import json

db_info = db.info()

class user_topics(object):
  """find user concerning topics with the plots of movies the user likes"""
  def __init__(self,userid):
    super(user_topics, self).__init__()
    self.userid = userid

  def get_user_topics(self,model):
    movie_list = db_info.user_train_movies(self.userid)
    plot_map = db.movieid_plot_map(db_info.mv_plots_set)
    plot_list = []
    for m in movie_list:
      if m in plot_map: plot_list.append(plot_map[m])
    user_doc = self.get_plot_doc(plot_list)
    topic_dis = lda.doc_topic_distribution(model,user_doc)
    return topic_dis

  def get_plot_doc(self,return_list):
    str_list = []
    for r in return_list:
      if type(r) is tuple:
        plot_str = ''
        for p in r:
          if p: plot_str += p
        str_list.append(plot_str)
      else: str_list.append(r)
    return str_list

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