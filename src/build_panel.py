"""Conservative balanced standalone-reporting-manager panel, not global ownership.
Excludes amended, confidential, notice/combination and linked/shared manager histories.
Dollars use disclosed SEC as-filed median implied prices, not observed trade prices.
"""
import json,sqlite3,collections,statistics,math,gzip
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
QUARTERS=[f'{y}-{m:02d}-{d}' for y in range(2021,2027) for m,d in [(3,'31'),(6,'30'),(9,'30'),(12,'31')] if '2021-12-31'<=f'{y}-{m:02d}-{d}'<='2026-06-30']
# Security identities observed in SEC issuer/CUSIP/class records; exact class filtering below.
CONFIG=[('NVDA','67066G104','compute','2021-12-31'),('AMD','007903107','compute','2021-12-31'),('AVGO','11135F101','compute','2021-12-31'),('MRVL','573874104','compute','2021-12-31'),('TSM','874039100','compute','2021-12-31'),('ASML','N07059210','compute','2021-12-31'),('MU','595112103','compute','2021-12-31'),('MSFT','594918104','platforms','2021-12-31'),('GOOG','02079K107','platforms','2021-12-31'),('GOOGL','02079K305','platforms','2021-12-31'),('AMZN','023135106','platforms','2021-12-31'),('META','30303M102','platforms','2021-12-31'),('PLTR','69608A108','software','2021-12-31'),('NOW','81762P102','software','2021-12-31'),('CRM','79466L302','software','2021-12-31'),('ORCL','68389X105','incumbent_cloud','2021-12-31'),('CRWV','21873S108','infrastructure','2025-06-30'),('NBIS','N97284108','infrastructure','2024-12-31'),('IREN','Q4982L109','infrastructure','2023-09-30'),('APLD','038169207','infrastructure','2023-09-30')]
SPLITS={'NVDA':[('2024-06-07',10)],'AVGO':[('2024-07-12',10)],'AMZN':[('2022-06-03',20)],'GOOG':[('2022-07-15',20)],'GOOGL':[('2022-07-15',20)],'NOW':[('2025-12-17',5)]}
def iso(s):
 try:return datetime.strptime(s,'%d-%b-%Y').strftime('%Y-%m-%d')
 except ValueError:
  try:return datetime.strptime(s,'%Y-%m-%d').strftime('%Y-%m-%d')
  except ValueError:return None

def factor(t,q):return math.prod(v for d,v in SPLITS.get(t,[]) if q<d)
def true(s):return str(s).strip().upper() in ('Y','TRUE','1')
def select_panel(continuous,excluded):
 return continuous-{c for c,reasons in excluded.items() if reasons}

def finalize_output(result):
 from metrics import endpoint_decomposition
 for stock in result['stocks']:
  stock['remaining_accumulation_pct']=None
  stock['remaining_accumulation_withheld_reason']='cross_sample_robustness_not_validated'
 for stock in result['stocks']:
  rows=sorted((r for r in result['series'] if r['ticker']==stock['ticker']),key=lambda r:r['quarter'])
  for previous,current in zip(rows,rows[1:]):
   decomposition=endpoint_decomposition([previous['shares']],[current['shares']],[previous['reference_price']],[current['reference_price']])
   current['estimated_price_effect_dollars']=decomposition['price_effect_dollars']
   current['proxy_valuation_change_dollars']=decomposition['valuation_change_dollars']
 return result

def main():
 db=sqlite3.connect(ROOT/'research/staging.sqlite');subs={};covers={};summaries={};relations=[];bad=collections.defaultdict(set)
 print('Read metadata',flush=True)
 for kind,acc,j in db.execute('SELECT kind,accession,row_json FROM metadata'):
  r=json.loads(j)
  target={'SUBMISSION':subs,'COVERPAGE':covers,'SUMMARYPAGE':summaries}.get(kind)
  if target is not None:
   if acc in target and target[acc]!=r:bad['conflicting_metadata'].add(acc)
   target[acc]=r
  elif kind in ('OTHERMANAGER','OTHERMANAGER2'):relations.append((acc,r))
 bycusip={c:(t,g,start) for t,c,g,start in CONFIG};filings=collections.defaultdict(list);excluded=collections.defaultdict(set)
 for acc,s in subs.items():
  q=iso(s['PERIODOFREPORT'])
  if q not in QUARTERS:continue
  cik=s['CIK'];filings[cik,q].append(acc);cover=covers.get(acc,{});summary=summaries.get(acc,{})
  if s['SUBMISSIONTYPE']!='13F-HR':excluded[cik].add('amendment_or_notice')
  if cover.get('REPORTTYPE')!='13F HOLDINGS REPORT':excluded[cik].add('non_standalone_report')
  if iso(cover.get('REPORTCALENDARORQUARTER',''))!=q:excluded[cik].add('period_mismatch')
  if true(summary.get('ISCONFIDENTIALOMITTED','')):excluded[cik].add('confidential_omissions')
  if not summary or not cover:excluded[cik].add('missing_metadata')
  if acc in bad['conflicting_metadata']:excluded[cik].add('conflicting_metadata')
 for (cik,q),accs in filings.items():
  if len(accs)!=1:excluded[cik].add('multiple_filings_in_period')
 # Resolve both CIK and 13F file numbers; exclude both sides instead of guessing scope.
 bynumber=collections.defaultdict(set)
 for acc,cover in covers.items():
  if acc in subs and cover.get('FORM13FFILENUMBER'):bynumber[cover['FORM13FFILENUMBER']].add(subs[acc]['CIK'])
 for acc,r in relations:
  if acc not in subs:continue
  source=subs[acc]['CIK'];excluded[source].add('manager_relationship')
  if r.get('CIK'):excluded[r['CIK']].add('manager_relationship')
  for target in bynumber.get(r.get('FORM13FFILENUMBER',''),set()):excluded[target].add('manager_relationship')
 print('Read security positions',flush=True)
 positions=collections.defaultdict(float);prices=collections.defaultdict(list);provenance=collections.defaultdict(set);invalid_rows=collections.Counter();unknown=collections.Counter();raw=collections.Counter()
 for acc,_,j in db.execute('SELECT accession,candidate,row_json FROM positions'):
  r=json.loads(j);s=subs.get(acc)
  if not s:invalid_rows['missing_submission']+=1;continue
  q=iso(s['PERIODOFREPORT'])
  if q not in QUARTERS:continue
  cik=s['CIK'];cusip=r['CUSIP'].upper();cfg=bycusip.get(cusip)
  if not cfg:unknown[cusip]+=1;continue
  t,g,start=cfg
  if q<start:continue
  raw[q]+=1
  if r.get('PUTCALL','').strip() or r['SSHPRNAMTTYPE'].upper()!='SH':invalid_rows['option_or_principal']+=1;continue
  if r.get('OTHERMANAGER','').strip() or r.get('INVESTMENTDISCRETION','').upper()!='SOLE':excluded[cik].add('shared_discretion_or_other_manager')
  try:shares=float(r['SSHPRNAMT']);value=float(r['VALUE'])
  except (ValueError,TypeError):excluded[cik].add('invalid_numbers');continue
  if not math.isfinite(shares+value) or shares<0 or value<0:excluded[cik].add('invalid_numbers');continue
  if shares==0:
   if value>0:excluded[cik].add('zero_shares_positive_value')
   continue
  f=factor(t,q);adjusted=shares*f
  filed=iso(s['FILING_DATE'])
  if not filed:excluded[cik].add('invalid_filing_date');continue
  usd=value*(1000 if filed<'2023-01-03' else 1)
  positions[cik,q,t]+=adjusted;provenance[q,t].add(acc)
  if value>0 and not excluded.get(cik):prices[q,t].append(usd/adjusted)
  # Store ratios to test for unit errors without auto-correcting suspicious values.
  if value>0:prices['manager',cik,q,t].append(usd/adjusted)
 allmanagers={c for c,q in filings};continuous={c for c in allmanagers if all((c,q) in filings for q in QUARTERS)}
 panel=select_panel(continuous,excluded)
 medians={k:statistics.median(v) for k,v in prices.items() if len(k)==2 and len(v)>=20}
 for k,ratios in prices.items():
  if len(k)!=4:continue
  _,c,q,t=k;p=medians.get((q,t))
  if p and any(abs(r/p-1)>.05 for r in ratios):excluded[c].add('implied_price_outlier')
 panel=select_panel(continuous,excluded)
 if len(panel)<30:raise ValueError('Too few independently usable continuous managers')
 print('Balanced panel managers',len(panel),flush=True)
 series=[];stockrows=[];checks=[];quarantined=[];groups=collections.defaultdict(list)
 for t,cusip,g,start in CONFIG:
  qs=[q for q in QUARTERS if q>=start];levels=[sum(positions[c,q,t] for c in panel) for q in qs]
  if not levels or levels[0]<=0 or any(v<=0 for v in levels):raise ValueError('Missing/nonpositive position stock: '+t)
  bad_prices=[{'quarter':q,'reference_count':len(prices.get((q,t),[])),'mad_pct':100*statistics.median([abs(v/medians[q,t]-1) for v in prices.get((q,t),[])]) if (q,t) in medians else None} for q in qs if (q,t) not in medians or statistics.median([abs(v/medians[q,t]-1) for v in prices.get((q,t),[])])>.01]
  if bad_prices:
   if g in ('compute','platforms','software'):raise ValueError('Core security price gate failed: '+t)
   quarantined.append({'ticker':t,'reason':'insufficient_or_inconsistent_SEC_implied_price_reference','failed_quarters':bad_prices});continue
  ref=medians.get((qs[0],t));vals=[v*ref if ref else None for v in levels]
  stock=[]
  for i,(q,qty) in enumerate(zip(qs,levels)):
   p=medians.get((q,t));spread=statistics.median([abs(v/p-1) for v in prices.get((q,t),[])]) if p else None
   if not p or spread>.01:raise ValueError('Inconsistent implied price reference '+t+q)
   previous=levels[i-1] if i else None
   row={'quarter':q,'ticker':t,'group':g,'shares':qty,'index':100*qty/levels[0],'qoq_shares':qty-previous if previous is not None else None,'qoq_pct':100*(qty/previous-1) if previous else None,'reference_price':p,'reference_price_n':len(prices[(q,t)]),'reference_price_mad_pct':100*spread,'estimated_position_change_dollars':(qty-previous)*p if previous is not None else None,'constant_price_position':qty*ref if ref else None,'source_accessions':sorted({filings[c,q][0] for c in panel if positions[c,q,t]>0})}
   stock.append(row);series.append(row)
  peak=max(levels);peakadd=peak-levels[0];remaining=100*(levels[-1]-levels[0])/peakadd if peakadd>.05*levels[0] else None
  stockrows.append({'ticker':t,'cusip':cusip,'group':g,'baseline':qs[0],'latest_shares':levels[-1],'latest_index':stock[-1]['index'],'qoq_pct':stock[-1]['qoq_pct'],'remaining_accumulation_pct':None,'remaining_accumulation_withheld_reason':'cross_sample_robustness_not_validated','stock_drawdown_pct':100*(levels[-1]/peak-1)})
  checks.append({'ticker':t,'quarters':len(qs),'minimum_implied_price_observations':min(x['reference_price_n'] for x in stock),'max_implied_price_mad_pct':max(x['reference_price_mad_pct'] for x in stock)})
  groups[g].append(t)
 # Basket excludes satellites and ORCL overlay. Dollar-weighted position stock uses fixed baseline implied prices.
 for group,tickers in list(groups.items())+[('core',[t for t,_,g,_ in CONFIG if g in ('compute','platforms','software')])]:
  byq=collections.defaultdict(list)
  for r in series:
   if r['ticker'] in tickers:byq[r['quarter']].append(r)
  eligible=[q for q in QUARTERS if len(byq[q])==len(tickers)]
  if not eligible:continue
  # Group-specific start, infrastructure requires ALL satellites to be present.
  first=eligible[0];baseline={r['ticker']:r for r in byq[first]};b0=sum(r['shares']*medians[first,r['ticker']] for r in byq[first]);history=[]
  for q in eligible:
   b=sum(r['shares']*medians[first,r['ticker']] for r in byq[q]);history.append(b)
   series.append({'quarter':q,'ticker':group,'group':group,'index':100*b/b0,'constant_price_position':b,'estimated_position_change_dollars':sum(r['estimated_position_change_dollars'] or 0 for r in byq[q]) if q!=first else None,'baseline':first,'reference_price_convention':'median as-filed SEC implied quarter-end price; not a market close or transaction price'})
 coverage=[]
 for q in QUARTERS:
  managers={c for c,qq in filings if qq==q};coverage.append({'quarter':q,'observed_managers':len(managers),'panel_managers':len(panel),'panel_manager_count_pct':100*len(panel)/len(managers),'raw_candidate_rows':raw[q]})
 result={'status':'validated_restricted_reporting_panel','latest_quarter':QUARTERS[-1],'holdings_as_of':QUARTERS[-1],'publication_cutoff':'2026-08-31','generated_at':datetime.now(timezone.utc).isoformat(),'methodology_version':'restricted-panel-v1','panel_managers':len(panel),'continuous_managers_before_exclusions':len(continuous),'all_observed_managers':len(allmanagers),'manager_exclusion_reasons':dict(collections.Counter(reason for reasons in excluded.values() for reason in reasons)),'panel_ciks':sorted(panel),'coverage':coverage,'series':series,'stocks':stockrows,'security_checks':checks,'archives':[dict(zip(['url','sha256','size_bytes','ingested_at'],r)) for r in db.execute('SELECT * FROM archives')],'invalid_rows':dict(invalid_rows),'quarantined_securities':quarantined,'unknown_cusips':dict(unknown),'limitations':['13F standalone reporting-manager balanced panel, not aggregate institutional ownership or a representative sample.','Amended/linked/shared/confidential manager histories excluded, not economically reconciled.','Price references are robust SEC as-filed implied prices; dollar changes are estimates, not purchases or cash flows.','No independently classified active-only or hedge-fund net-exposure series.','Fixed basket uses hindsight-selected companies; satellite business transitions use separate baselines.','Bulk cutoff is 2026-08-31; later amendments are not yet included.','Coverage counts do not establish market-value coverage or full economic deduplication.','Missing securities in a complete filing are treated as reported zero; de minimis/confidential omissions remain a limitation.','All-file row-count reconciliation and independent shares-outstanding caps remain outstanding.']}
 assert len(QUARTERS)==19
 assert len({r['quarter'] for r in series if r['ticker']=='core'})==19
 if any(not math.isfinite(r['index']) for r in series):raise ValueError('Nonfinite output')
 result=finalize_output(result)
 (ROOT/'data/panel.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
 (ROOT/'data/panel.json.gz').write_bytes(gzip.compress((ROOT/'data/panel.json').read_bytes(),mtime=0))
 print(json.dumps({'panel':len(panel),'continuous':len(continuous),'rows':len(series),'bytes':(ROOT/'data/panel.json').stat().st_size,'checks':checks}),flush=True)
if __name__=='__main__':main()
