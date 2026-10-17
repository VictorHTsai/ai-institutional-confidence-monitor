"""SEC bulk ingestion; archives are filing windows, never observation quarters.
Standard library only. Preserve source rows and all relationship metadata.
"""
import csv,io,json,zipfile,urllib.request,hashlib,time,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
'NVDA':r'^NVIDIA', 'AMD':r'^ADVANCED MICRO DEVICES', 'AVGO':r'^BROADCOM',
'MRVL':r'^MARVELL', 'TSM':r'^TAIWAN SEMICONDUCTOR', 'ASML':r'^ASML',
'MU':r'^MICRON TECHNOLOGY', 'MSFT':r'^MICROSOFT', 'GOOG_FAMILY':r'^ALPHABET',
'AMZN':r'^AMAZON', 'META':r'^(META PLATFORMS|FACEBOOK)', 'ORCL':r'^ORACLE',
'CRWV':r'^COREWEAVE', 'NBIS':r'^(NEBIUS|YANDEX)', 'IREN':r'^(IREN|IRIS ENERGY)',
'APLD':r'^APPLIED DIGITAL', 'PLTR':r'^PALANTIR', 'NOW':r'^SERVICENOW', 'CRM':r'^SALESFORCE'}
DISCOVERY=re.compile('|'.join('(?:'+v+')' for v in PATTERNS.values()))
def rows(z,name):
    matches=[n for n in z.namelist() if n.rsplit('/',1)[-1].lower()==name.lower()+'.tsv']
    if len(matches)!=1:raise ValueError('Expected exactly one table: '+name)
    return csv.DictReader(io.TextIOWrapper(z.open(matches[0]),encoding='utf-8-sig'),delimiter='\t')
def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true', help='Re-fetch and reprocess all windows, including historical revisions')
    args=parser.parse_args()
    db=sqlite3.connect(ROOT/'research/staging.sqlite');db.execute('PRAGMA journal_mode=WAL')
    db.executescript('''CREATE TABLE IF NOT EXISTS archives(url TEXT PRIMARY KEY,sha256 TEXT,size INTEGER,ingested_at TEXT);
    CREATE TABLE IF NOT EXISTS accession_sources(accession TEXT,url TEXT,PRIMARY KEY(accession,url));
    CREATE TABLE IF NOT EXISTS conflicts(accession TEXT,row_id TEXT,old_json TEXT,new_json TEXT,url TEXT);
    CREATE TABLE IF NOT EXISTS metadata(kind TEXT,accession TEXT,row_json TEXT,PRIMARY KEY(kind,accession,row_json));
    CREATE TABLE IF NOT EXISTS positions(accession TEXT,row_id TEXT,candidate TEXT,row_json TEXT,PRIMARY KEY(accession,row_id));''')
    urls=json.loads((ROOT/'research/archive_urls.json').read_text())
    urls=[u for u in urls if re.search(r'202[2-6]|2021q4',u)]
    for url in reversed(urls):
        if db.execute('SELECT 1 FROM archives WHERE url=?',(url,)).fetchone() and not args.refresh:continue
        f=ROOT/'research'/url.rsplit('/',1)[-1]
        if not f.exists() or args.refresh:
            print('Downloading',url,flush=True)
            req=urllib.request.Request(url,headers={'User-Agent':'VictorInvestmentResearch public reproducible study https://github.com/VictorHTsai'})
            with urllib.request.urlopen(req,timeout=120) as res,open(str(f)+'.part','wb') as out:
                while chunk:=res.read(1024*1024):out.write(chunk)
            Path(str(f)+'.part').replace(f)
        h=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();count=0
        with zipfile.ZipFile(f) as z:
            for kind in ['SUBMISSION','COVERPAGE','OTHERMANAGER','OTHERMANAGER2','SUMMARYPAGE']:
                for r in rows(z,kind):
                    if kind=='SUBMISSION':db.execute('INSERT OR IGNORE INTO accession_sources VALUES(?,?)',(r['ACCESSION_NUMBER'],url))
                    db.execute('INSERT OR IGNORE INTO metadata VALUES(?,?,?)',(kind,r['ACCESSION_NUMBER'],json.dumps(r,sort_keys=True)))
            for r in rows(z,'INFOTABLE'):
                name=r['NAMEOFISSUER'].upper()
                if not DISCOVERY.search(name):continue
                for ticker,pat in PATTERNS.items():
                    if re.search(pat,name):
                        encoded=json.dumps(r,sort_keys=True)
                        old=db.execute('SELECT row_json FROM positions WHERE accession=? AND row_id=?',(r['ACCESSION_NUMBER'],r['INFOTABLE_SK'])).fetchone()
                        if old and old[0]!=encoded:
                            db.execute('INSERT INTO conflicts VALUES(?,?,?,?,?)',(r['ACCESSION_NUMBER'],r['INFOTABLE_SK'],old[0],encoded,url))
                        db.execute('INSERT OR IGNORE INTO positions VALUES(?,?,?,?)',(r['ACCESSION_NUMBER'],r['INFOTABLE_SK'],ticker,encoded));count+=1;break
        from datetime import datetime,timezone
        db.execute('INSERT OR REPLACE INTO archives VALUES(?,?,?,?)',(url,h,f.stat().st_size,datetime.now(timezone.utc).isoformat()));db.commit()
        print('Ingested',f.name,count,'candidate rows',flush=True)
        # ZIP is reproducible from manifest; retain latest sample for audit.
        if '01jun2026' not in f.name:f.unlink()
    print('Completed',db.execute('SELECT count(*) FROM archives').fetchone()[0],'archives',flush=True)
if __name__=='__main__':main()
