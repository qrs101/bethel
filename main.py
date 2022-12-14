
import json
import os
path = 'data/a.json'

with open(path) as fo:
    s = fo.read()
    s = s.replace('=', ':').replace('null', 'None')
    j = json.dumps(s)
    print(j)
