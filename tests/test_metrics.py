import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from metrics import endpoint_decomposition,accumulation,resolve_chain
class Metrics(unittest.TestCase):
 def test_appreciation_is_not_buying(self):
  r=endpoint_decomposition([10],[10],[100],[150]);self.assertEqual(r['estimated_position_change_dollars'],0);self.assertEqual(r['price_effect_dollars'],500)
 def test_split_invariance(self):
  a=endpoint_decomposition([10],[12],[100],[110]);b=endpoint_decomposition([100],[120],[10],[11]);self.assertEqual(a,b)
 def test_endpoint_identity(self):
  r=endpoint_decomposition([10,20],[12,15],[100,50],[110,40]);self.assertAlmostEqual(r['valuation_change_dollars'],r['estimated_position_change_dollars']+r['price_effect_dollars'])
 def test_missing_is_not_zero(self):
  with self.assertRaises(ValueError):endpoint_decomposition([None],[0],[100],[100])
 def test_invalid_universe(self):
  with self.assertRaises(ValueError):endpoint_decomposition([1],[1,2],[10],[10])
 def test_no_accumulation(self):self.assertIsNone(accumulation([100,90],1)['remaining_accumulation_pct'])
 def test_negligible_peak(self):self.assertIsNone(accumulation([100,100.1],1)['remaining_accumulation_pct'])
 def test_remaining_can_be_negative(self):self.assertEqual(accumulation([100,120,90],1)['remaining_accumulation_pct'],-50)
 def test_stock_drawdown_is_distinct(self):self.assertAlmostEqual(accumulation([100,120,110],1)['position_stock_drawdown_pct'],-100/12)
 def test_restatement_and_additions(self):
  fs=[dict(form='13F-HR',amended=False,type='',rows=[1,2]),dict(form='13F-HR/A',amended=True,type='NEW HOLDINGS',rows=[3]),dict(form='13F-HR/A',amended=True,type='RESTATEMENT',rows=[4]),dict(form='13F-HR/A',amended=True,type='NEW HOLDINGS',rows=[5])]
  self.assertEqual(resolve_chain(fs),[4,5])
 def test_unanchored_addition_rejected(self):
  with self.assertRaises(ValueError):resolve_chain([dict(form='13F-HR/A',amended=True,type='NEW HOLDINGS',rows=[3])])

class ArchiveLayout(unittest.TestCase):
 def test_top_level_and_nested_tables(self):
  import io,zipfile
  from ingest import rows
  for name in ['SUBMISSION.tsv','01JUN2025-31AUG2025_form13f/SUBMISSION.tsv']:
   buf=io.BytesIO()
   with zipfile.ZipFile(buf,'w') as z:z.writestr(name,'ACCESSION_NUMBER\tCIK\nabc\t123\n')
   buf.seek(0)
   with zipfile.ZipFile(buf) as z:self.assertEqual(list(rows(z,'SUBMISSION')),[{'ACCESSION_NUMBER':'abc','CIK':'123'}])
 def test_ambiguous_table_rejected(self):
  import io,zipfile
  from ingest import rows
  buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w') as z:
   z.writestr('a/SUBMISSION.tsv','CIK\n1');z.writestr('b/SUBMISSION.tsv','CIK\n2')
  buf.seek(0)
  with zipfile.ZipFile(buf) as z:
   with self.assertRaises(ValueError):rows(z,'SUBMISSION')

if __name__=='__main__':unittest.main()
