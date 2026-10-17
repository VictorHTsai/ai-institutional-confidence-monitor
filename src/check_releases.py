"""Discover official bulk releases and recent filing-index arrivals.
Daily filing arrivals are monitored as a queue, not represented as verified holdings.
"""
import urllib.request,urllib.error,re,json,time,gzip
from datetime import datetime,timedelta,timezone
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets'
def fetch(u):
 req=urllib.request.Request(u,headers={'User-Agent':'VictorInvestmentResearch https://github.com/VictorHTsai/ai-institutional-confidence-monitor'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read().decode('utf-8','replace')
def main():
 body=fetch(URL);urls=re.findall(r'href="([^"]+\.zip)"',body)
 urls=['https://www.sec.gov'+u if u.startswith('/') else u for u in urls]
 if len(urls)<20:raise RuntimeError('Missing SEC archive inventory; retain previous verified data')
 (ROOT/'research').mkdir(exist_ok=True)
 (ROOT/'research/archive_urls.json').write_text(json.dumps(urls,indent=2)+'\n')
 now=datetime.now(timezone.utc);arrivals=[];failures=[]
 for n in range(1,8):
  d=now-timedelta(days=n)
  if d.weekday()>4:continue
  u=f'https://www.sec.gov/Archives/edgar/daily-index/{d.year}/QTR{(d.month-1)//3+1}/master.{d:%Y%m%d}.idx'
  time.sleep(.2)
  try:
   for line in fetch(u).splitlines():
    parts=line.split('|')
    if len(parts)==5 and parts[2] in ('13F-HR','13F-HR/A','13F-NT','13F-NT/A'):
     arrivals.append({'cik':parts[0],'form':parts[2],'filed':parts[3],'source':'https://www.sec.gov/Archives/'+parts[4]})
  except urllib.error.HTTPError as e:
   if e.code!=404:failures.append({'url':u,'error':str(e)[:200]})
  except Exception as e:failures.append({'url':u,'error':str(e)[:200]})
 payload={'checked_at':now.isoformat(),'status':'ok' if not failures else 'partial','bulk_archives':len(urls),'recent_filing_arrivals':len(arrivals),'filing_arrivals':arrivals,'index_failures':failures,'limitation':'Individual arrivals are queued for audit. Verified panel refresh currently follows bulk publication; daily arrivals are not yet integrated.'}
 (ROOT/'data/release_check.json').write_text(json.dumps(payload,indent=2)+'\n')
 (ROOT/'data/release_check.json.gz').write_bytes(gzip.compress((ROOT/'data/release_check.json').read_bytes(),mtime=0))
 if failures:raise RuntimeError('Some SEC daily indexes failed; see release_check.json')
if __name__=='__main__':main()
