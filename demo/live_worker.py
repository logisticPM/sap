"""One real run on frozen synthetic material. Never mutates prior demo runtimes."""
import importlib.util,json,sys,time,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
job=Path(sys.argv[1]);payload=json.loads(job.read_text())
spec=importlib.util.spec_from_file_location('isolated_followup',ROOT/'followup.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
f.FILE=job.with_suffix('.result.json')
f.DB={'revision':payload['target'],'replies':{},'run':None,'history':[],'published':None,'queued':False,'decision':None,'decisionHistory':[]}
def save_progress():
 r=f.DB.get('run')
 if r:
  for event in r['events']:event.setdefault('recordedAt',time.time())
 temp=f.FILE.with_suffix('.tmp')
 temp.write_text(json.dumps(f.DB,indent=2))
 temp.replace(f.FILE)
f.save=save_progress
if payload['target']>=2:f.DB['replies']=copy.deepcopy(f.FIXTURES)
if payload['target']==4:f.DB['decision']={'id':payload['id'],'choice':'alternative','actor':'Retail planner (local simulated role)','reason':'Investigate an alternative carrier and quote only. Do not book, pay or change the purchase plan.','scope':'Investigation only','baselineRetained':True,'externalSend':False}
docs=payload['sources']
original_validate=f.validate
def validate(a,read,docs):
 result=original_validate(a,read,docs)
 if 'unknown' in a.get('conditions',{}).values() and 'unmet' in a.get('summary','').lower() and sum(v=='not_satisfied' for v in a['conditions'].values())<3:
  raise ValueError('Do not describe unknown conditions as unmet, including aggregate unmet conditions. Keep status in typed conditions; summarize the next action without grouping unknown and not_satisfied.')
 return result
f.validate=validate
d={'workflowId':payload['session'],'disclosure':{'draft':{'version':5}},'case':{'clock':'2026-10-23T14:42:00Z','sourceIds':list(docs)}}
def call(role,path):
 x=docs.get(path.split('/')[-1]);return (200,x) if x else (404,{'error':'Source absent'})
try:
 f.connect()
 original_complete=f.CLIENT.complete
 def tracked_complete(*args,**kwargs):
  f.DB['run']['activity']={'phase':'model_request','startedAt':time.time()}
  f.save()
  return original_complete(*args,**kwargs)
 f.CLIENT.complete=tracked_complete
 f.start(d,call)
 while f.ACTIVE.locked():time.sleep(.25)
except Exception as e:
 f.DB['run']={'id':payload['id'],'status':'failed','error':str(e)[:240],'events':[]};f.save()
