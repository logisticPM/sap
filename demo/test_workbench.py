import unittest,tempfile,json,copy
from pathlib import Path
import server as s
from activity import describe,changes

class WorkbenchTests(unittest.TestCase):
 def setUp(self):
  self.old=s.STORE;s.STORE=self.old/('test-'+s.uuid.uuid4().hex);s.STORE.mkdir()
 def tearDown(self):s.STORE=self.old
 def step(self,d,role,action):return s.advance(d,role,action,d['revision'])
 def reviewed(self):
  d=s.create();self.step(d,'supplier','review');self.step(d,'supplier','reply');return d
 def test_mode_validation(self):
  with self.assertRaises(ValueError):s.create('auto')
 def test_independent_sessions(self):
  a=s.create();b=s.create('live_model');self.assertNotEqual(a['id'],b['id']);self.assertEqual(b['stage'],0)
 def test_wrong_role(self):
  with self.assertRaises(ValueError):self.step(s.create(),'planner','review')
 def test_stale_revision(self):
  with self.assertRaises(ValueError):s.advance(s.create(),'supplier','review',99)
 def test_private_before_share(self):
  d=self.reviewed();p=s.public(d,'planner');self.assertIsNone(p['artifact']);self.assertIsNone(p['trace']);self.assertNotIn('attempts',p)
 def test_scoped_after_share(self):
  d=self.reviewed();self.step(d,'supplier','share');p=s.public(d,'planner');self.assertEqual(set(p['artifact']),{'summary','conditions','next_step'});self.assertIsNone(p['trace'])
 def test_both_historical_branches(self):
  for alt in [False,True]:
   d=self.reviewed();self.step(d,'supplier','share')
   if alt:self.step(d,'planner','alternative')
   self.step(d,'planner','stop');self.assertEqual(d['stage'],5);self.assertEqual(d['modelCalls'],0)
 def test_live_no_historical_fallback(self):
  d=s.create('live_model');d['stage']=1;self.assertIsNone(s.public(d,'supplier')['artifact'])
 def test_live_alternative_requires_disclosure(self):
  d=s.create('live_model');d['stage']=4;d['liveRuns']['4']=copy.deepcopy(s.runs[s.IDS[4]])
  self.assertIsNone(s.public(d,'planner')['artifact']);self.step(d,'supplier','share_alternative');self.assertIsNotNone(s.public(d,'planner')['artifact']);self.step(d,'planner','stop');self.assertEqual(d['modelCalls'],0)
 def test_running_prevents_duplicate(self):
  d=s.create('live_model');d['job']={'status':'running'}
  with self.assertRaises(ValueError):self.step(d,'supplier','review')
 def test_no_restart_closed(self):
  d=s.create();d['stage']=5
  with self.assertRaises(ValueError):self.step(d,'supplier','review')
 def test_budget_guard(self):
  b=s.engine.Budget(s.STORE/'test.sqlite',cap=0)
  with self.assertRaises(RuntimeError):b.reserve({'messages':[]})
  self.assertEqual(b.status()['calls'],0)
 def test_progress_is_observed_not_invented(self):
  r={'status':'running','events':[{'type':'tool','name':'read_sources','result':{'sources':[{'id':'ONE','text':'Example'}]}}]}
  p=describe(r);self.assertEqual([x['id'] for x in p['sources']],['ONE']);self.assertEqual(p['phase'],'Assessing retrieved records');self.assertNotIn('findings',p)
 def test_rejected_output_not_findings(self):
  p=describe({'status':'running','events':[{'type':'tool','name':'submit_followup','arguments':{'summary':'UNTRUSTED'},'result':{'error':'Correction required'}}]})
  self.assertEqual(p['phase'],'Revising output after a rule check');self.assertNotIn('UNTRUSTED',json.dumps(p))
 def test_planner_cannot_read_live_progress(self):
  d=s.create('live_model');d['job']={'id':'abc','status':'running'}
  (s.STORE/'job-abc.result.json').write_text(json.dumps({'run':{'status':'running','events':[{'type':'tool','name':'read_sources','result':{'sources':[{'id':'PRIVATE','text':'SECRET'}]}}]}}))
  self.assertIsNotNone(s.public(d,'supplier')['activity']);self.assertNotIn('SECRET',json.dumps(s.public(d,'planner')))
 def test_first_disclosure_does_not_expose_old_private_summary(self):
  d=self.reviewed();self.step(d,'supplier','share');self.assertIsNone(s.public(d,'planner')['previousSummary'])
 def test_diff_reports_only_changed_fields(self):
  a={'conditions':{'carrier':'unknown','qa':'unknown'},'next_step':'collect_facts'};b={'conditions':{'carrier':'not_satisfied','qa':'unknown'},'next_step':'human_tradeoff'}
  self.assertEqual([r['field'] for r in changes(a,b)],['carrier','next_action'])
 def test_new_job_does_not_relabel_old_activity(self):
  d=s.create('live_model');d['stage']=1;d['liveRuns']['1']=copy.deepcopy(s.runs[s.IDS[1]]);d['job']={'id':'not-yet-created','status':'running'}
  self.assertIsNone(s.public(d,'supplier')['activity'])
 def test_pending_disclosure_keeps_last_shared_only(self):
  d=s.create('live_model');d['stage']=4;d['liveRuns']={'2':copy.deepcopy(s.runs[s.IDS[2]]),'4':copy.deepcopy(s.runs[s.IDS[4]])};d['liveRuns']['4']['artifact']['summary']='PRIVATE UNSHARED'
  p=s.public(d,'planner');self.assertEqual(p['artifact']['summary'],d['liveRuns']['2']['artifact']['summary']);self.assertTrue(p['pendingDisclosure']);self.assertNotIn('PRIVATE UNSHARED',json.dumps(p));self.assertIsNone(p['activity'])
 def test_closed_retains_last_authorized_version(self):
  d=self.reviewed();self.step(d,'supplier','share');self.step(d,'planner','alternative');rid=s.public(d,'planner')['runId'];self.step(d,'planner','stop');self.assertEqual(s.public(d,'planner')['runId'],rid)
 def test_planner_error_redaction(self):
  d=s.create('live_model');d['job']={'status':'failed','error':'PRIVATE SOURCE CONTENT','id':'example'};self.assertNotIn('PRIVATE SOURCE CONTENT',json.dumps(s.public(d,'planner')))

if __name__=='__main__':unittest.main(verbosity=2)
