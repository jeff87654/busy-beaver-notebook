"""bcfg.py: base machines, K-templates (dl3_hits codings) and the real K-moment b value B0."""
import idle, sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
F1T = 'P=-,u=1,s=0,d=1d+0,b=1b+0'
BASES = {  # tag: (machine, template, B0, family)
 'r': ('1RB0LG_1RC1RB_0RD0RB_0LE1RD_0LD1LF_---1LA_1LC1LG', 'R,E,' + F1T + ',S=-', 6, 'F1'),
 's': ('1RB0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG', 'R,D,' + F1T + ',S=0110', 2, 'F1'),
 'h': ('1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1RA0LG_1LB1LG', 'R,A,' + F1T + ',S=1', 3, 'F1'),
 'u': ('1RB1RE_1RC1RB_0LD0LG_0RA1LD_---1RF_1LG0RB_1LC1LG', 'L,C,' + F1T + ',S=-', 2, 'F1'),
 'i': ('1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE', 'R,C,P=-,u=1,s=0,d=1d+0,b=3b+1,S=0', 0, 'F2'),
 'a': ('1RB1RA_0LC0LF_0RD1LC_1RA1RE_0RF0RG_1LB1LF_---0RA', 'L,C,P=-,u=1,s=0,d=1d+0,b=3b+1,S=0', 0, 'F2'),
 'b': ('1RB1RA_0LC0LF_0RD1LC_1RA1RE_0RF1RG_1LB1LF_---0RA', 'L,B,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', 0, 'F2'),
 'c': ('1RB1RA_0LC0LF_0RD1LC_1RA1RE_1RF1RG_1LB1LF_---0RA', 'L,B,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', 0, 'F2'),
 't': ('1RB1RE_1RC1RB_0LD0LG_0RA1LD_---1RF_0LC0RB_1LC1LG', 'L,C,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', 0, 'F2'),
 'j': ('1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RA1LG_---0LE', 'R,A,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', 1, 'F2'),
 'd': ('1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_---0RA', 'L,E,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', 0, 'F3'),
 'f': ('1RB1RA_0LC0LF_1RD1LC_1LE1RE_1LB0RG_1LE1LF_---0RA', 'L,E,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', 0, 'F3'),
 'o': ('1RB1LA_1LC1RC_1LF0RD_---0RE_1RF1RE_0LA0LG_1LC1LG', 'L,C,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', 0, 'F3'),
 'n': ('1RB1LA_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG', 'L,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', 1, 'F3'),
 'e': ('1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_---0RA', 'L,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 3, 'F3'),
 'g': ('1RB1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_---0RA', 'L,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 3, 'F3'),
 'p': ('1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG', 'L,A,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 3, 'F3'),
 'q': ('1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG', 'L,A,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 3, 'F3'),
}
def T(tag): return kl.tmpl(BASES[tag][0], BASES[tag][1])
def targs(tag):
    t = T(tag); return [t['o'], t['q'], t['P'] or '-', t['u'], t['s'], str(t['al']), str(t['be']), str(t['alB']), str(t['beB']), t['S'] or '-']
def word(tag, ds, a, b): return kl.word(T(tag), ds, a, b)
