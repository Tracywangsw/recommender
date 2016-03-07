def extract_id(filename):
  path = 'file:/C:/mallet-2.0.8RC3/movie-plots/'
  start = len(path)
  end = -4
  return filename[start:end]

def load_plot_composition(path):
  plot_composition = {}
  with open(path) as f:
    for line in f:
      records = line.rstrip().split('\t')
      docname = records[1]
      values = [float(r) for r in records[2:]]
      movieid = int(extract_id(docname))
      plot_composition[movieid] = values
  return plot_composition

def main(topics):
  path = 'model_data/movie_'+str(topics)+'/plot_composition.txt'
  return load_plot_composition(path)
