"""Summarize observed SEC ingestion; explicitly not a validated holdings series."""
import json,sqlite3,collections
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def audit():
 db=sqlite3.connect(ROOT/'research/staging.sqlite')
 submissions={};conflicting_metadata=collections.Counter();kinds=collections.Counter()
 periods=collections.defaultdict(lambda:{'accessions':0,'holdings_reports':0,'amendments':0,'notices':0,'managers':set()})
 relations=collections.Counter();amendment_types=collections.Counter();cusips=collections.defaultdict(collections.Counter)
 for kind,acc,encoded in db.execute('SELECT kind,accession,row_json FROM metadata'):
  r=json.loads(encoded);kinds[kind]+=1
  if kind=='SUBMISSION':
   if acc in submissions and submissions[acc]!=r:conflicting_metadata[kind]+=1
   submissions[acc]=r
  elif kind=='COVERPAGE' and r.get('ISAMENDMENT','').lower() in ('y','true','1'):
   amendment_types[r.get('AMENDMENTTYPE','')]+=1
  elif kind in ('OTHERMANAGER','OTHERMANAGER2'):
   relations[kind]+=1
 for acc,r in submissions.items():
  q=r['PERIODOFREPORT'];a=periods[q];a['accessions']+=1;a['managers'].add(r['CIK']);f=r['SUBMISSIONTYPE']
  if f=='13F-HR':a['holdings_reports']+=1
  if f.endswith('/A'):a['amendments']+=1
  if 'NT' in f:a['notices']+=1
 candidate=collections.Counter();options=collections.Counter();shared=collections.Counter();missing=collections.Counter()
 for acc,t,encoded in db.execute('SELECT accession,candidate,row_json FROM positions'):
  r=json.loads(encoded);candidate[t]+=1
  cusips[t][(r['CUSIP'].upper(),r['TITLEOFCLASS'])]+=1
  if r.get('PUTCALL','').strip():options[t]+=1
  if r.get('OTHERMANAGER','').strip() or r.get('INVESTMENTDISCRETION','').upper()!='SOLE':shared[t]+=1
  if acc not in submissions:missing[t]+=1
 for a in periods.values():a['distinct_managers']=len(a.pop('managers'))
 output={'generated_at':datetime.now(timezone.utc).isoformat(),'status':'staging_only_not_validated',
 'publication_gate':'FAIL_PENDING_SECURITY_ACTION_PRICE_AMENDMENT_AND_OVERLAP_VALIDATION',
 'archives':[dict(zip(['url','sha256','size_bytes','ingested_at'],r)) for r in db.execute('SELECT * FROM archives ORDER BY url')],
 'observed_filing_periods':dict(periods),'metadata_counts':dict(kinds),'conflicting_metadata':dict(conflicting_metadata),
 'amendment_types':dict(amendment_types),'relationship_rows':dict(relations),
 'candidate_rows':dict(candidate),'candidate_option_rows':dict(options),'candidate_shared_discretion_or_other_manager_rows':dict(shared),
 'candidate_rows_without_submission':dict(missing),
 'candidate_identifiers':{t:[{'cusip':k[0],'class':k[1],'rows':n} for k,n in v.most_common(12)] for t,v in cusips.items()},
 'warning':'Counts include amendments, old report periods, options and overlap. Not positions, ownership, capital flows or institutional confidence. Zero candidate rows is not proof of zero holdings.'}
 (ROOT/'data/staging_audit.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'archives':len(output['archives']),'candidate_rows':sum(candidate.values()),'periods':len(periods),'gate':output['publication_gate']}))
 return output
if __name__=='__main__':audit()
