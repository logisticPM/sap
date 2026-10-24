import os,uuid,unittest
from pathlib import Path
from unittest.mock import patch
import engine,server

class PortableChecks(unittest.TestCase):
 def test_live_disabled_before_any_job(self):
  with patch.dict(os.environ,{'ENABLE_LIVE_MODEL':'0'}):
   with self.assertRaisesRegex(ValueError,'Live calls disabled'):server.start_live({},1,'review','supplier')
 def test_default_zero_budget(self):
  with patch.dict(os.environ,{'DEMO_BUDGET_USD':'0'}):
   b=engine.Budget(engine.RUNTIME/('test-budget-'+uuid.uuid4().hex+'.sqlite'))
   with self.assertRaises(RuntimeError):b.reserve({'messages':[]})
 def test_excessive_cap_rejected(self):
  with patch.dict(os.environ,{'DEMO_BUDGET_USD':'11'}):
   with self.assertRaises(ValueError):engine.Budget()

if __name__=='__main__':unittest.main()
