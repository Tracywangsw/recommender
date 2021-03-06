import csv
import psycopg2

def read_file(path):
  data_list = []
  if path.endswith('.csv'):
    with open(path,'rb') as f:
      has_header = csv.Sniffer().has_header(f.read(1024))
      f.seek(0)
      reader = csv.reader(f)
      if has_header: next(reader)
      for row in reader: data_list.append(row)
    return data_list
  elif path.endswith('.dat'):
    with open(path,'rb') as f:
      # next(f)
      for row in f:
        row = row.strip()
        row = row.split("@")
        data_list.append(row)
    return data_list

class SplitSet:

  def __init__(self):
    self.whole_data = read_file(path='dataset/ratings.dat')
    self.set = self.set_whole_dataset(self.whole_data)

  # return hashmap {userid:[record]}
  def set_whole_dataset(self,data):
    fullset = {}
    for row in data:
      (userid,movieid,rating,ts) = (int(row[0]),int(row[1]),float(row[2]),int(row[3]))
      if userid in fullset: fullset[userid].append([ts,userid,movieid,rating])
      else: fullset.setdefault(userid,[[ts,userid,movieid,rating]])
    return fullset

  # return data of single user
  def user_data(self,user):
    userset = self.set[user]
    userset.sort()
    return userset

  def split(self):
    (trainset,testset,fullset) = ([],[],self.set)
    for u in fullset:
      userdata = self.user_data(u)
      addedsum = 0
      for ru in userdata:
        if float(addedsum)/len(userdata) <= 0.8:
          trainset.append(ru)
          addedsum += 1
        else: testset.append(ru)
    return [trainset,testset]


def main():
  s = SplitSet()
  (trainset,testset) = s.split()[:]
  print 'begin to write trainset\n'
  write_file(trainset,'dataset/rating_train.csv')
  print 'trainset writing end\n'
  print 'begin to write testset\n'
  write_file(testset,'dataset/rating_test.csv')
  print 'testset writing end'

def write_file(recordlist,path):
  with open(path,'w') as f:
    a = csv.writer(f,delimiter=',')
    a.writerows(recordlist)
