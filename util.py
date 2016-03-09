import csv
import json
import pickle

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

def split_item(item):
  l = len(item)
  item_list = []
  for i in range(l):
    for j in range(i+1,l):
      item_list.append([item[i],item[j]])
  return item_list

def write_file(recordlist,path,type='pickle'):
  if type == 'csv':
    with open(path,'w') as f:
      a = csv.writer(f,delimiter=',')
      a.writerows(recordlist)
  elif type == 'pickle':
    with open(path,'w') as f:
      pickle.dump(recordlist,f,pickle.HIGHEST_PROTOCOL)
      f.close()

def read_file(path,type='pickle',has_head=False,delimiter='@'):
  data_list = []
  if type == 'pickle':
    with open(path,'rb') as f:
      return pickle.load(f)
  elif type == 'csv':
    with open(path,'rb') as f:
      if has_head:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        reader = csv.reader(f)
        if has_header: next(reader)
      for row in reader: data_list.append(row)
    return data_list
  elif type == 'dat':
    with open(path,'rb') as f:
      if has_head: next(f)
      for row in f:
        row = row.strip()
        row = row.split(delimiter)
        data_list.append(row)
    return data_list

def read_pickle(path):
  with open(path,'rb') as f:
    obj = pickle.load(f)
    return obj
