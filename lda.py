from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim
import datetime
import pdb
import db

class corpora_build():
  def __init__(self,doc_set):
    doc = self.clean_doc(doc_set)
    self.dictionary = corpora.Dictionary(doc)
    self.corpora = [self.dictionary.doc2bow(text) for text in doc]

  def clean_doc(self,doc_set):
    tokenizer = RegexpTokenizer(r'\w+')
    en_stop = get_stop_words('en')
    en_stop += ['t','s','u','can','d','ve','isn','didn','wouldn','don','shouldn','haven','hadn','doesn','couldn']
    p_stemmer = PorterStemmer()
    texts = []
    for i in doc_set:
      raw = i.lower()
      tokens = tokenizer.tokenize(raw)
      stopped_tokens = [i for i in tokens if not i in en_stop]
      stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
      texts.append(stemmed_tokens)
    return texts

def lda_model_build(doc_set,num_topics):
  print 'lda_model_build start,datetime:'+ str(datetime.datetime.now())
  util = corpora_build(doc_set)
  ldamodel = gensim.models.ldamodel.LdaModel(util.corpora, num_topics, id2word = util.dictionary, passes=20, minimum_probability=0)
  print 'lda_model_build end,datetime:'+ str(datetime.datetime.now())
  return ldamodel


def doc_topic_distribution(lda,doc):
  texts = corpora_build(doc)
  test = lda[texts.corpora][0]
  # a = list(sorted(test, key=lambda x: x[1], reverse=True)) #rank distribution
  # print lda.print_topic(a[-1][0]) # the least relative
  # print lda.print_topic(a[0][0]) # the most relative
  return test

def load_lda(path):
  return gensim.models.ldamodel.LdaModel.load(path,mmap='r')

def get_mv_plots():
  cursor = db.get_cursor()
  cursor.execute("select movieid,plot from plots")
  return_list = cursor.fetchall()
  mv_plots = {r[0]:r[1] for r in return_list}
  return mv_plots

def movieid_plot_map(return_list):
  mv_plot = {}
  for r in return_list:
    (mvid,plot) = (r,return_list[r])
    if plot:
      if type(plot) is tuple:
        plot_str = ''
        for p in plot:
          if p: plot_str += p
        mv_plot[mvid] = plot_str
      else: mv_plot[mvid] = plot
    else: print str(mvid)+": has no plots"
  return mv_plot

def build_model(num_topics,path):
  plots = get_mv_plots()
  plot_doc = movieid_plot_map(plots).values()
  lda_model = lda_model_build(plot_doc,num_topics)
  lda_model.save(path)
  return lda_model

def main():
  build_model(50,path="lda_model/50_topics.txt")

def test():
  doc_a = "Brocolli is good to eat. My brother likes to eat good brocolli, but not my mother."
  doc_b = "My mother spends a lot of time driving my brother around to baseball practice."
  doc_c = "Some health experts suggest that driving may cause increased tension and blood pressure."
  doc_d = "I often feel pressure to perform well at school, but my mother never seems to drive my brother to do better."
  doc_e = "Health professionals say that brocolli is good for your health." 
  doc_set = [doc_a, doc_b, doc_c, doc_d, doc_e]
  lda = lda_model_build(doc_set,num_topics=20)
  # lda.save('../lda.txt')
  # lda = load_lda()
  test_doc = ["My mother likes to eat good brocolli. "]
  print doc_topic_distribution(lda,test_doc)
  print lda.show_topics()
