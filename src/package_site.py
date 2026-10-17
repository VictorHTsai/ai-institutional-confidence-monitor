"""Fail closed: no deployment of an empty interface or a partial dataset."""
import json,shutil,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(d):
 if d.get('status')!='validated_restricted_reporting_panel':raise ValueError('Restricted-panel gate required')
 core=[r for r in d['series'] if r['ticker']=='core']
 if len(core)!=19 or core[0]['quarter']!='2021-12-31' or core[-1]['quarter']!='2026-06-30':raise ValueError('Historical coverage gap or new quarter requires explicit eligibility review')
 if d['panel_managers']<30:raise ValueError('Too few managers')
 if len(d['archives'])<20:raise ValueError('Historical archive coverage incomplete')
 required={'NVDA','AMD','AVGO','MRVL','TSM','ASML','MU','MSFT','GOOG','GOOGL','AMZN','META','PLTR','NOW','CRM'}
 if not required.issubset({s['ticker'] for s in d['stocks']}):raise ValueError('Core universe incomplete')
 for s in d['stocks']:
  if s['latest_shares']<=0:raise ValueError('Missing security')
 return True
if __name__=='__main__':
 source=ROOT/'data/panel.json'
 d=json.loads(source.read_text() if source.exists() else gzip.decompress((ROOT/'data/panel.json.gz').read_bytes()).decode());validate(d)
 out=ROOT/'dist';out.mkdir(exist_ok=True)
 shutil.copy(ROOT/'site/index.html',out/'index.html');shutil.copytree(ROOT/'data',out/'data',dirs_exist_ok=True)
 for f in (out/'data').glob('*.gz'):
  f.with_suffix('').write_bytes(gzip.decompress(f.read_bytes()))
 for f in ['METHODOLOGY.md','UNIVERSE.md','AUDIT.md','RELEASE_ASSESSMENT.md']:shutil.copy(ROOT/f,out/f)
 (out/'.nojekyll').write_text('')
 print('Packaged complete restricted-panel dataset; no claim of full institutional coverage')
