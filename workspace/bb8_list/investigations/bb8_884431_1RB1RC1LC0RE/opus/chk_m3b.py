from pieces import *
for b in range(0, 4):
    print(b, [(k, validate.reaches(start3, M3, {'k':k,'b':b,'y':1}), validate.reaches(M3, G3, {'k':k,'b':b,'y':1}), validate.reaches(start3, G3, {'k':k,'b':b,'y':1})) for k in range(0, 5)])
