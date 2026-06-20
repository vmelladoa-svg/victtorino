import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
html=open(r'C:\Users\dell\victtorino\dom.html',encoding='utf-8',errors='ignore').read()
idx=html.find('theme-post-featured-image')
print(f"DOM: {len(html)} chars | featured-image idx={idx}")
if idx>0:
    blk=html[idx:idx+1400]
    print(re.sub(r'>\s*<','>\n<', blk[:1300]))
