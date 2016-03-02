import db
import recommend
import json
import csv

db_info = db.info()

def common_list_len(list1,list2):
  common = {}
  for i in list1:
    if i in list2: common[i] = 0
  return len(common)

def cal_precise(recm,testm):
  if len(recm) == 0:
    print 'recommend list is null'
    return 0
  return float(common_list_len(recm,testm))/len(recm)

def cal_recall(recm,testm):
  if len(testm) == 0:
    print 'test list is null'
    return 0
  return float(common_list_len(recm,testm))/len(testm)

def cal_f1(recm,testm):
  precise = cal_precise(recm,testm)
  recall = cal_recall(recm,testm)
  average = (precise+recall)/2
  if average == 0: return 0
  return precise*recall/average

def write_file(recordlist,path):
  with open(path,'w') as f:
    a = csv.writer(f,delimiter=',')
    a.writerows(recordlist)

def estimate_recommender(path,top_neighbor=50,top_movie=20):
  estimate_json = {}
  user_info = []
  user_list = db_info.user_list
  # user_list = []
  # for u in db_info.user_list:
  #   if len(db_info.user_train_movies(u)) > 20 and len(db_info.user_test_movies(u)) > 5:
  #     user_list.append(u)

  (total_pre,total_recall,total_f1) = (0,0,0)
  for u in user_list:
    recommend_list = recommend.recommend_for_user(u,top_neighbor,top_movie)
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
    user_info.append([u,precision,recall,f1,user_train_count,len(test_list)])

  print 'average precision : ' + str(total_pre/len(user_list))
  print 'average recall : ' + str(total_recall/len(user_list))
  print 'average f1 : ' + str(total_f1/len(user_list))
  write_file(user_info,path)

def main():
  args = [[50,5],[50,10],[50,20],[50,30],[20,20],[40,20],[60,20]]
  for arg in args:
    path = 'results/user_info_'+str(arg[0])+'_'+str(arg[1])+'.csv'
    estimate_recommender(path,arg[0],arg[1])