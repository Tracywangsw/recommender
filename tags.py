import db
from math import sqrt
import multiprocessing as mp
import json
import csv
import pickle
import util

db_info = db.info()

class generate_tag():
  def __init__(self,userid):
    self.mv_list = db_info.user_train_movies(userid)

  def mv_top_tags(self,mvid,top=30):
    tags = db_info.movie_tag_relevance(mvid)
    genres = db_info.movie_genres(mvid)
    if genres:
      for g in genres:
        tags[g] = 1
    if tags: return util.hash2list(tags)[:top]
    else: return None

  def user_tags(self,top=30):
    tag_count = {}
    for m in self.mv_list:
      top_tags = self.mv_top_tags(m)
      if not top_tags: continue
      for t in top_tags:
        (relevance,tagid) = t[:]
        if tagid not in tag_count: tag_count.setdefault(tagid,relevance)
        else: tag_count[tagid] += relevance
    return util.hash2list(tag_count)[:top]

def get_common_items(set1,set2):
  common = {}
  for item in set1: 
    if item in set2: 
      common[item] = 1
  return common

def cosine_sim(set1,set2):
  common = get_common_items(set1,set2)
  if len(common) == 0: return 0

  sum1 = sum([set1[item] for item in common])
  sum2 = sum([set2[item] for item in common])

  sum1_sq = sum([pow(set1[item],2) for item in common])
  sum2_sq = sum([pow(set2[item],2) for item in common])
  set_sum = sum([set1[item]*set2[item] for item in common])

  rate = float(len(common))/(len(set1)+len(set2)-len(common))
  return float(set_sum*rate)/sqrt(sum1_sq*sum2_sq)

def tag_sim_matrix(person,other):
  sim_matrix = {}
  person_tags = tag_map[person]
  other_tags = tag_map[other]
  sim_matrix[(person,other)] = cosine_sim(util.list2hash(person_tags),util.list2hash(other_tags))
  print sim_matrix
  return sim_matrix

def multiprocess(processes, user_list_list):
  pool = mp.Pool(processes=processes)
  results = [pool.apply_async(tag_sim_matrix, args=(l[0],l[1])) for l in user_list_list]
  dest = dict(results[0].get())
  for r in range(1,len(results)):
    dest.update(results[r].get())
  pool.close()
  pool.join()
  return dest



def main(processes=4):
  global tag_map
  tag_map = util.read_file('user_profile/preference_tag/user_tags_50.pickle')
  user_list = db_info.user_list
  user_list_list = util.split_item(user_list)
  node = len(user_list_list)/60
  for i in range(60):
    exe_list = user_list_list[i*node:(i+1)*node]
    results = multiprocess(processes,exe_list)
    path = 'user_similarity/user_tag_sim/genres/' + str(i) + '.pickle'
    util.write_file(results,path)