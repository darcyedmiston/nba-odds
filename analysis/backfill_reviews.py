import csv,re,sys,unicodedata
P='/home/claude/nba-odds/'
def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r"[.'’]",'',s); s=re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s); return re.sub(r'\s+',' ',s).strip()
box={}
def load_box(day):
    if day in box: return box[day]
    m={}
    try:
        for r in csv.DictReader(open(f'{P}boxscores/{day}.csv',newline='')): m[norm(r['player'])]=r
    except FileNotFoundError: pass
    box[day]=m; return m
def margin_game(fs):
    n=[int(x) for x in re.findall(r'(\d+)(?:\s*-|\s*$)',fs)]
    return abs(n[0]-n[1]) if len(n)==2 else None
def review(r):
    if r['result']=='Void': return 'Void: inactive/DNP per box score. [Unforeseeable] [auto-backfill]'
    if r['result'] not in('Win','Loss'): return None
    b=load_box(r['date_melb']).get(norm(r['player']))
    kf=r['key_factors'] or ''
    pm=re.search(r'proj ([\d.]+) in ([\d.]+) min',kf)
    hit=re.search(r'hit (\d+)%',kf); l10=re.search(r'\((\d+)/10\)',kf)
    parts=[];short=False;mins=None
    if b and b.get('minutes') not in (None,''): mins=float(b['minutes'])
    head=f"{r['result']}: {r['actual']}"
    if mins is not None: head+=f" in {mins:.0f} min"
    if pm: head+=f" vs proj {pm.group(1)} in {pm.group(2)} min"
    parts.append(head)
    if mins is not None and pm:
        d=mins-float(pm.group(2))
        if abs(d)<4: parts.append('minutes on projection')
        else: parts.append(f"minutes {abs(d):.1f} {'over' if d>0 else 'short'}"); short=d<0
    g=margin_game(b['final_score']) if b else None
    if g is not None: parts.append(f"{g}-point game"+(' (blowout)' if g>=20 else ''))
    mm=r.get('market_move','')
    try:
        v=float(mm); parts.append('market flat' if v==0 else f"market moved {abs(v):g} {'our way' if v>0 else 'against'}")
    except ValueError: parts.append('market move n/a')
    cls='Variance'
    if r['result']=='Loss':
        if short: parts.append('minutes shortfall drove the miss')
        elif hit and l10 and (int(hit.group(1))<=60 or int(l10.group(1))<=6):
            parts.append(f"thin support (hit {hit.group(1)}%, L10 {l10.group(1)}/10) - D2/D3 overstated"); cls='Model error'
        try:
            if float(r['margin'])==-0.5: parts.append('missed by 0.5')
        except ValueError: pass
    if r['override']=='Yes':
        if r['tier'] in('Watchlist','Pass') or r['placed']!='Paper' or r['tier']=='Diff 3' and 'Diff 4' in (r['risk_flagged'] or ''):
            parts.append('override helped (loss avoided at paper stake)' if r['result']=='Loss' else 'override cost value (win at reduced/no stake)')
    src='repo box score (ESPN)' if b else 'repo result (box row not found)'
    return '; '.join(parts)+f". Source: {src}. [{cls}] [auto-backfill]"
if __name__=='__main__':
    mode=sys.argv[1]
    rows=list(csv.DictReader(open(P+'model/picks_log.csv',newline='')));f=list(rows[0].keys())
    if mode=='check':
        n=agree=0
        for r in rows:
            if r['date_melb'] in('2026-11-17',) and r['post_game_review']:
                g=review(r); n+=1
                a=re.search(r'\[(Variance|Model error|Unforeseeable)\]',r['post_game_review']).group(1)
                b=re.search(r'\[(Variance|Model error|Unforeseeable)\]',g).group(1)
                agree+=a==b
                if a!=b or n<=3: print('ORIG',r['post_game_review'][:170]); print('GEN ',g[:170]); print()
        print('class agreement',agree,'/',n)
    else:
        c=0
        for r in rows:
            if '2026-11-07'<=r['date_melb']<='2026-11-16' and not r['post_game_review']:
                g=review(r)
                if g: r['post_game_review']=g; c+=1
        w=csv.DictWriter(open(P+'model/picks_log.csv','w',newline=''),fieldnames=f);w.writeheader();w.writerows(rows);print('filled',c)
