import tags
import db
import csv
import db
import similarity
import pickle
import util

def save_user_tags(path,top_tag=50):
  output = {}
  for u in db.get_user_list():
    person_tags = tags.generate_tag(u).user_tags(50)
    output[u] = person_tags
    print u
  util.write_file(output,path)

def save_user_topics(path):
  output = []
  for u in db.get_user_list():
    person_topics = similarity.get_user_topics(u)
    output.append(person_topics)
    print u
  util.write_file(output,path)

class profile():
  """docstring for profile"""
  def __init__(self,path):
    self.user_tag_set = util.read_file(path)

  def get_user_tags(self,userid):
    # user_tags = {}
    # for t in user_tag_list:
    #   (rate,tagid) = t[:]
    #   tag_name = tags_info.get_name_by_id(tagid)
    #   user_tags[tag_name] = rate
    # return user_tags
    info = db.tags_info()
    for t in self.user_tag_set:
      key = info.get_name_by_id(t[1])
      user_tags[key] = t[0] 
    return user_tags

def main():
  path = 'user_profile/preference_tag/user_tags_50.pickle'
  save_user_tags(path,50)