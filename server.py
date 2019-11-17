import spacy
import numpy as np
import asyncio
import websockets
import json
import time
from thinc.neural.util import get_array_module

nlp = spacy.load('en_core_web_md')

print('Spacy Loaded')

# from sklearn.decomposition import PCA
# pca = PCA(n_components=10)
# pca.fit(difference_matrix)

def n_most_similar(nlp, queries, *, n_closest=1, batch_size=1024):
    xp = get_array_module(nlp.data)

    unit_vectors = nlp.data / xp.linalg.norm(
        nlp.data, axis=1, keepdims=True
    )  # unit normalize all vectors

    similars = xp.dot(
        queries, unit_vectors.T
    ).flatten()  # cos_sim = dot(a, b)/(norm(a)*norm(b))
    #         similars.shape (200000,)
    n_closest_idx = np.argpartition(similars, -n_closest)[-n_closest:]  # [n,..., N]
    scores = similars[n_closest_idx]

    xp = get_array_module(nlp.data)

    row2key = {row: key for key, row in nlp.key2row.items()}

    keys = xp.asarray([row2key[row] for row in n_closest_idx], dtype="uint64")

    scores, keys = zip(*sorted(zip(scores, keys), reverse=True))
    return scores, keys


async def operation(websocket, path):
    """Opens a Web Socket on the specified port and listens for operations.
    Operation must contain one or two words (a and b) to perform on:

    a && b
        - Multiply numpy.mulitply(a, b)
        - Divide np.divide(a, b)
        - Add np.add(a, b)
        - Subtract np.sub(a, b)
        - Cross np.cross(a, b) -- Perpendicular to both

    a
        - scale numpy.multiply(a, scalar)

    TODO:
        - Bisection (a, b) --> np.add(a, b).normalize * scalar 
        - Lerp (a, b, alpha) --> alpha * a + (1 - alpha) * b
        - Rotate (a, angle) --> will involve quaternions
    
    Arguments:
        websocket {type} -- The websocket instance
        path {type} -- The path to serve the websocket
    """
    async for message in websocket:
        request = json.loads(message)

        if "sentence" in request:
            try:
                doc = nlp(request["sentence"])
                # FIXME: will this break because misspelled word?
                # FIXME: send time stamp so I can diff off that rather than large dictionary
                data = [ { "word": token.text, "data": { "pos": token.pos_, "dep": token.dep_ } } for token in doc ]

                response = json.dumps({
                    "op": "sentence",
                    "data": data,
                })

            except Exception as inst:
                response = json.dumps({
                        "message": inst.args[0],
                        "op": "sentence"
                    })

        elif "b" not in request and "a" in request:
            try:
                word_a = nlp(request["a"])[0]
                if not word_a.has_vector:
                    raise Exception('No corresponding vector') # FIXME:

                vector_a = word_a.vector # might fail
                vector_a_norm = word_a.vector_norm
                vector_a_pos = word_a.pos_

                if request["type"] == 'scale':
                    data = vector_a * 0.3
                    # data = vector_a * scalar # Scalar undefined

                response = json.dumps({
                    "op": "scale",
                    "data": data,
                    "a": request["a"],
                    "vectorA": vector_a,
                    "vectorANorm": vector_a_norm,
                    "vectorAPos": vector_a_pos
                })

            except:
                response = json.dumps({
                    "op": request["type"],
                    "message": f"{request['a']} has no corresponding vector.",
                    "argument": "B",
                })

        elif "a" in request and "b" in request:
            try:
                word_a = nlp(request["a"])[0]
                word_b = nlp(request["b"])[0]

                if not word_a.has_vector:
                    raise Exception("A", request["a"])
                if not word_b.has_vector:
                    raise Exception("B", request["b"])

                vector_a = word_a.vector # might fail
                vector_b = word_b.vector # might fail
                vector_a_norm = word_a.vector_norm # might fail
                vector_b_norm = word_b.vector_norm # might fail
                vector_a_pos = word_a.pos_
                vector_b_pos = word_b.pos_

                if request["type"] == 'add':
                    data = np.add(vector_a, vector_b)
                if request["type"] == 'subtract':
                    data = np.subtract(vector_a, vector_b)
                if request["type"] == 'multiply':
                    data = np.multiply(vector_a, vector_b)
                if request["type"] == 'divide':
                    data = np.divide(vector_a, vector_b)
                if request["type"] == 'cross':
                    data = np.cross(vector_a, vector_b)

                scores, keys = n_most_similar(nlp.vocab.vectors, np.array([data]), n_closest=50)
                data = [nlp.vocab[key].text for key in keys]

                response = json.dumps({
                    "op": request["type"],
                    "data": data,
                    "a": request["a"],
                    "b": request["b"],
                    "vectorA": vector_a,
                    "vectorB": vector_b,
                    "vectorANorm": vector_a_norm,
                    "vectorBNorm": vector_b_norm,
                    "vectorAPos": vector_a_pos,
                    "vectorBPos": vector_b_pos
                })

            except Exception as inst:
                if inst.args[0] == "A":
                    response = json.dumps({
                        "op": request["type"],
                        "message": f"{request['a']} has no corresponding vector.",
                        "argument": "A"
                    })
                elif inst.args[0] == "B":
                    response = json.dumps({
                        "op": request["type"],
                        "message": f"{request['a']} has no corresponding vector.",
                        "argument": "B"
                    })
                else:
                    response = json.dumps({
                        "op": request["type"],
                        "message": inst.args[0],
                        "argument": None
                    })

        else:
            response = json.dumps({
                "op": request["type"],
                "message": "Neither A or B was provided.",
                "argument": "A,B"
            })
        
        await websocket.send(response)


if __name__ == '__main__':
    start_server = websockets.serve(operation, '127.0.0.1', 5678)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()