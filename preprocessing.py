import psycopg2

def get_cursor():
  conn_str = "host='localhost' dbname='movie' user='postgres' password='iswear'"
  # conn_str = "host='localhost' dbname='movielen_1M' user='python' password='python'"
  conn = psycopg2.connect(conn_str)
  cursor = conn.cursor()
  return cursor

# get the map of movie_plots of which the movies are rated by users.
def get_movie_plot():
  cursor = get_cursor()
  cursor.execute("select movieid,plot from plots where movieid in (select distinct movieid from ratings)")
  return_list = cursor.fetchall()
  mv_plots = {r[0]:r[1] for r in return_list}
  return mv_plots

def output_to_file(document_map):
  for d in document_map:
    if document_map[d]:
      # print str(d)
      path = 'plots/'+str(d)+'.txt'
      with open(path,'w') as f:
        f.write(plot2str(document_map[d]))
    else:
      print str(d) + " plots is null"

def plot2str(plot):
  if type(plot) is tuple or type(plot) is list:
    plot_str = ' '.join(plot)
    return plot_str
  else: 
    # print plot
    return plot

def main():
  m = get_movie_plot()
  output_to_file(m)
