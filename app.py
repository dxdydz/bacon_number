from flask import Flask, jsonify, request, abort
import redis
from util import keystr, Actor

app = Flask(__name__)
app.config["TESTING"] = True

db = redis.Redis(host='localhost', decode_responses=True)


def search_bacon(id_a, id_b='4724'):
    '''
    Performs breadth-first searches from both actor A and B, stops when they "touch"

    Args:
        id_a: Actor A ID
        id_b: Actor B ID (Kevin Bacon)

    returns:
        Dictionary with bacon number and the chain of actor-actor pairs and movie they co-starred in form:
        {"bacon_number": [bacon_number], "chain":{"actor_1":[actor_name], "actor_two":[actor_name], "movie":[movie_title]}}

        If no chain is found, returns {"bacon_number":1000}
    '''
    def costars(x):
        '''
        Returns list of Actor objects for all costars of Actor x
        '''
        return [Actor(k, x.id, v) for k,v in db.hgetall(keystr('actor', x.id, 'costars')).items()]

    a = Actor(id_a, None, None)
    b = Actor(id_b, None, None)
    a_set = {a.id: a}
    b_set = {b.id: b}
    a_list = [a]
    b_list = [b]

    #Double ended breadth-first search
    it = 0
    while len(a_set.keys() & b_set.keys()) == 0:
        if (len(a_list) == 0) or (len(b_list) == 0):    #No path found
            return {'bacon_number': 1000}
        if it%2 == 0:
            next_actor = a_list.pop(0)
            next_costars = [star for star in costars(next_actor) if star not in a_set]
            #Skip to b if is a costar
            if b not in next_costars:
                a_list.extend(next_costars)
            else:
                b_as_costar = [star for star in next_costars if star==b][0]
                a_set[b_as_costar.id] = b_as_costar
            a_set[next_actor.id] = next_actor
        else:
            next_actor = b_list.pop(0)
            next_costars = [star for star in costars(next_actor) if star not in b_set]
            if a not in next_costars:
                b_list.extend(next_costars)
            else:
                a_as_costar = [star for star in next_costars if star==a][0]
                b_set[a_as_costar.id] = a_as_costar
            b_set[next_actor.id] = next_actor
        it += 1

    meeting_point = (a_set.keys() & b_set.keys()).pop()

    #Trace back up search tree to roots
    a_chain = [a_set[meeting_point]]
    b_chain = [b_set[meeting_point]]
    p = a_set[meeting_point].parent
    while p != None and p != a:
        a_chain.append(a_set[p])
        p = a_set[p].parent
    p = b_set[meeting_point].parent
    while p != None and p != b:
        b_chain.append(b_set[p])
        p = b_set[p].parent
    a_chain = a_chain[::-1]

    #Format chain with names rather than IDs
    out_chain = []
    for i in range(len(a_chain)):
        if a_chain[i].film != None:
            actor_2 = db[keystr('actor', a_chain[i].id, 'name')]
            actor_1 = db[keystr('actor', a_chain[i].parent, 'name')]
            movie = db[keystr('movie', a_chain[i].film, 'title')]
            out_chain.append({'movie':movie, 'actor_1':actor_1, 'actor_2':actor_2})
    for i in range(len(b_chain)):
        if b_chain[i].film != None:
            actor_1 = db[keystr('actor', b_chain[i].id, 'name')]
            actor_2 = db[keystr('actor', b_chain[i].parent, 'name')]
            movie = db[keystr('movie', b_chain[i].film, 'title')]
            out_chain.append({'movie':movie, 'actor_1':actor_1, 'actor_2':actor_2})
    
    return {'bacon_number': len(out_chain), 'chain': out_chain}



@app.route('/bacon', methods=['GET'])
def get_bacon():
    '''
    GET:
        Expects "name" parameter with actor name
        Returns JSON object with bacon degrees of separation and chain, if present
    '''

    bacon_id = '4724' #Kevin's ID number
    cache_time = 60*60*24*7 #one week

    params = request.args

    actor_name = params.get('name')
    if not actor_name:
        abort(400)
    
    #Find actor id
    ks = keystr('actor', actor_name, 'index')
    if ks in db:
        actor_id = db.zrange(ks, -1, -1)[0] #Assume most common actor
    else:
        abort(400)
    
    #Check cache for previous search
    cache_str = keystr('cache', actor_id, bacon_id)
    if cache_str in db:
        db.expire(cache_str, cache_time) #Re-up timeout
        return db[cache_str], 200

    #find bacon number
    oot = jsonify(search_bacon(actor_id))

    #add to cache
    db.setex(cache_str, cache_time, oot.get_data(as_text=True))

    return oot, 200


if __name__ == '__main__':
    app.run(debug=True)