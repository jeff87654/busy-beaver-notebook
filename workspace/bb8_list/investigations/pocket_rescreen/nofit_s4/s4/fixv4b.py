L=open('v4.cpp',newline='').read()
old='     if(regex_match(w,re)){'
new='''     bool hit=false; if(rx.rfind("C1:",0)==0){ long long k=atoll(rx.c_str()+3); string pre="0"+string(k,'1')+"0"; hit=w.compare(0,pre.size(),pre)==0; } else hit=regex_match(w,re);
     if(hit){'''
assert old in L
L=L.replace(old,new)
L=L.replace('regex re(rx=="ALL"?string("x"):rx);','regex re((rx=="ALL"||rx.rfind("C1:",0)==0)?string("x"):rx);')
open('v4.cpp','w',newline='').write(L)
