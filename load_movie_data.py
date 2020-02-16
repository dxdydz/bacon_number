import ast, csv, redis
from util import keystr

if __name__ == '__main__':
    db = redis.Redis('localhost') #Point at Redis Server

    # database scheme
    #
    # "actor:[actor_id]:name" : "John Doe"
    # "actor:[actor_id]:costars" : {"[costar_id]":"[movie_id]", ...}
    # "movie:[movie_id]:title" : "The Big Movie Title"
    # "actor:[actor_name]:index" : sorted set({index: freq})

    num_movies = 0

    print("Loading costar information...")
    with open('data/credits.csv', 'r', encoding='utf8') as f:
        rdr = csv.reader(f)
        for it, line in enumerate(rdr):
            if it != 0:
                num_movies += 1
                cast = ast.literal_eval(line[0])
                len_cast = len(cast)
                for i in range(len_cast):
                    i_id = cast[i]['id']
                    #check if exists
                    i_key_name = keystr('actor', i_id, 'name')
                    if i_key_name not in db:
                        db.set(i_key_name, cast[i]['name'])
                    #increment frequency of actor_id
                    db.zincrby(keystr('actor', cast[i]['name'], 'index'), 1, i_id)
                    for j in range(i+1, len_cast):
                        j_id = cast[j]['id']
                        j_key_name = keystr('actor', j_id, 'name')
                        if j_key_name not in db:
                            db.set(j_key_name, cast[j]['name'])
                        if i_id != j_id:
                            #Always rewrite with most recent movie
                            db.hmset(keystr('actor', i_id, 'costars'), {j_id: line[-1]})
                            db.hmset(keystr('actor', j_id, 'costars'), {i_id: line[-1]})

    print("Loading film title information...")
    with open('data/movies_metadata.csv','r', encoding='utf8') as f:
        rdr = csv.reader(f)
        for it, line in enumerate(rdr):
            if it == 0:
                col_names = dict(zip(line, range(len(line))))   #Read column headers
            else:
                db.set(keystr('movie', line[col_names['id']], 'title'), line[col_names['original_title']])
    
    print("Done. Data from %d movies entered into database" % num_movies)