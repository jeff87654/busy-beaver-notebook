"""Repair literal newlines that a shell heredoc put inside C string/char literals of stage35g.cpp."""
s = open('stage35g.cpp').read()
NL = chr(10)
BS = chr(92)
s = s.replace('printf(" | U=%x' + NL + '", used);', 'printf(" | U=%x' + BS + 'n", used);')
s = s.replace("ch != '" + NL + "')", "ch != '" + BS + "n')")
open('stage35g.cpp', 'w').write(s)
print('ok')
