import db
import recommend
import json
import csv
import util
import similarity
import tags

db_info = db.info()

def common_list_len(list1,list2):
  common = {}
  for i in list1:
    if i in list2: common[i] = 0
  return common

def cal_precise(recm,testm):
  if len(recm) == 0:
    print 'recommend list is null'
    return 0
  return float(len(common_list_len(recm,testm)))/len(recm)

def cal_recall(recm,testm):
  if len(testm) == 0:
    print 'test list is null'
    return 0
  return float(len(common_list_len(recm,testm)))/len(testm)

def cal_f1(recm,testm):
  precise = cal_precise(recm,testm)
  recall = cal_recall(recm,testm)
  average = (precise+recall)/2
  if average == 0: return 0
  return precise*recall/average

def estimate_recommender(path,top_neighbor=50,top_movie=20):
  estimate_json = {}
  user_info = []
  user_list = db_info.user_list
  # for u in user_list:
  #   if len(db_info.user_test_movies(u)) < 21:
  #     user_list.remove(u)

  (total_pre,total_recall,total_f1) = (0,0,0)
  for u in user_list:
    recommend_list = recommend.recommend_for_user(u,top_neighbor,top_movie)
    # recommend_list = recommend.item_recommend_for_user(u,top_neighbor,top_movie)
    test_list = db_info.user_test_movies(u)
    precision = cal_precise(recommend_list,test_list)
    recall = cal_recall(recommend_list,test_list)
    f1 = cal_f1(recommend_list,test_list)
    print 'userid : ' + str(u)
    print 'precision : ' + str(precision)
    print 'recall : ' + str(recall)
    print 'f1 : ' + str(f1)
    total_pre += precision
    total_recall += recall
    total_f1 += f1

    user_train_count = len(db_info.user_train_movies(u))
    user_info.append([u,precision,recall,f1,user_train_count,len(test_list),common_list_len(recommend_list,test_list).keys()])

  print 'average precision : ' + str(total_pre/len(user_list))
  print 'average recall : ' + str(total_recall/len(user_list))
  print 'average f1 : ' + str(total_f1/len(user_list))
  # user_info.append([0,total_pre/len(user_list),total_recall/len(user_list),total_f1/len(user_list),0,0])
  util.write_file(user_info,path,type='csv')

def main():
  # topics = 300
  # similarity.main(topics)
  # recommend.save_user_sim_matrix(topics)
  # recommend.main(method='lda',topics=topics)
  # recommend.main(method='hybrid',topics=topics)

  tags.main()
  recommend.main(method='tag')
  # args = [[50,5],[50,10],[50,20],[50,30],[20,20],[40,20],[60,20]]
  args = [[50,10],[50,50]]
  for arg in args:
    path = 'results/tag_based/genres/'+str(arg[0])+'_'+str(arg[1])+'.csv'
    estimate_recommender(path,arg[0],arg[1])