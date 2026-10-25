from pieces import *
for vals in ({'k':0,'b':0,'y':1},{'k':1,'b':0,'y':0},{'k':0,'b':1,'y':1},{'k':2,'b':3,'y':2}):
    print(vals, 'start3->M3', validate.reaches(start3, M3, vals), 'M3->G3', validate.reaches(M3, G3, vals),
          'start3->G3', validate.reaches(start3, G3, vals), 'start3->tgt3', validate.reaches(start3, tgt3, vals))
