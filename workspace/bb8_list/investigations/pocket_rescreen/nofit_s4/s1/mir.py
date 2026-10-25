import sys
m=sys.argv[1]; print('_'.join(''.join(t[i:i+3].replace('L','x').replace('R','L').replace('x','R') for i in (0,3)) for t in m.split('_')))
