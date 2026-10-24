"""Separate historical replay and real inference sessions; immutable historical archive."""
import json,uuid,threading,time,subprocess,sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
ROOT=Path(__file__).resolve().parent;STORE=ROOT/'runtime';STORE.mkdir(exist_ok=True);LOCK=threading.RLock()
import os
import engine
from activity import describe,changes
LIVE=threading.Lock()
archive=json.loads((ROOT/'fixtures/source_archive.json').read_text())
runs={r['id']:r for r in archive['history']+[archive['run']]}
IDS={1:'followup-8c49f8c1718443158b8a7d15fd64002c',2:'followup-5a99e2d6da154f669ad1e4acd2dfb840',4:'followup-c4a9c7ff723a484392053f73e2b1624b'}
for ident in IDS.values():assert runs[ident]['status']=='completed'
def file(ident):
 if len(ident)!=32 or any(c not in '0123456789abcdef' for c in ident):raise ValueError('Invalid replay ID')
 return STORE/('replay-'+ident+'.json')
def save(d):file(d['id']).write_text(json.dumps(d,indent=2))
def create(mode='historical_replay'):
 if mode not in ['historical_replay','live_model']:raise ValueError('Choose historical replay or live model.')
 d={'id':uuid.uuid4().hex,'stage':0,'revision':0,'events':[],'createdAt':time.time(),'mode':mode,'modelCalls':0,'liveRuns':{},'attempts':[],'job':None};save(d);return d
def start_live(d,target,action,role):
 if os.environ.get("ENABLE_LIVE_MODEL")!="1":raise ValueError("Live calls disabled. Read docs/RUN_LOCAL.md before enabling your own budget.")
 if not LIVE.acquire(False):raise ValueError('Another real model execution is running. Wait before starting another.')
 docs={}
 for e in runs[IDS[target]]['events']:
  if e['type']=='tool' and e['name']=='read_sources':
   for s in e['result'].get('sources',[]):
    if s.get('id') not in ['HUMAN-MANDATE','FOLLOWUP-LOGISTICS','FOLLOWUP-QA']:docs[s['id']]=s
 jobid=uuid.uuid4().hex;path=STORE/('job-'+jobid+'.json')
 path.write_text(json.dumps({'id':jobid,'session':d['id'],'target':target,'sources':docs}))
 d['job']={'id':jobid,'status':'running','target':target};d['revision']+=1;save(d)
 def worker():
  result=None
  try:
   subprocess.run([sys.executable,str(ROOT/'live_worker.py'),str(path)],timeout=360,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   result=json.loads(path.with_suffix('.result.json').read_text())['run']
   if result.get('status')=='completed' and not isinstance(result.get('artifact'),dict):
    result['status']='failed';result['error']='No validated artifact returned. Step retained; no fallback.'
  except Exception:result={'id':jobid,'status':'failed','error':'Execution interrupted or failed. Inspect retained job records; no historical fallback.','events':[]}
  finally:
   with LOCK:
    latest=json.loads(file(d['id']).read_text());latest['attempts'].append(result);latest['modelCalls']+=sum(e['type']=='model' for e in result['events'])
    latest['job']={'id':jobid,'status':result['status'],'target':target,'error':result.get('error')}
    if result['status']=='completed':
     latest['liveRuns'][str(target)]=result;latest['events'].append({'action':action,'role':role,'from':latest['stage'],'to':target,'recordedAt':time.time(),'execution':'new real model run','runId':result['id']});latest['stage']=target
    latest['revision']+=1;save(latest);LIVE.release()
 threading.Thread(target=worker,daemon=True).start()
def public(d,role):
 out={k:v for k,v in d.items() if k not in ['liveRuns','attempts']};out.update({'role':role,'artifact':None,'trace':None,'runId':None,'synthetic':True,'budget':engine.Budget().status()})
 stage=d['stage'];index=4 if stage in [4,6] else 2 if stage>=2 else 1 if stage==1 else None
 if role=='planner':
  released_alt=any(e['action']=='share_alternative' or d['mode']=='historical_replay' and e['action']=='alternative' for e in d['events'])
  index=(4 if released_alt else 2) if stage>=3 else None
  if out.get('job'):out['job']={k:v for k,v in out['job'].items() if k!='error'}
 out['pendingDisclosure']=role=='planner' and stage==4 and d['mode']=='live_model'
 out['activity']=None;out['changes']=[];out['previousSummary']=None
 if role=='supplier' and d['mode']=='live_model' and d.get('job'):
  try:
   current=json.loads((STORE/('job-'+d['job']['id']+'.result.json')).read_text())['run']
   if current:out['activity']=describe(current)
  except (FileNotFoundError,json.JSONDecodeError):pass
 if role=='supplier' and d.get('job') and d['job']['status']=='failed':out['failedTrace']=(d.get('attempts') or [{}])[-1].get('events',[])
 if index and (role=='supplier' or stage>=3):
  r=(d.get('liveRuns',{}).get(str(index)) if d['mode']=='live_model' else runs[IDS[index]])
  if not r:return out
  out['runId']=r['id']
  if role=='supplier':out['artifact']=r['artifact'];out['trace']=r['events']
  else:out['artifact']={k:r['artifact'][k] for k in ['summary','conditions','next_step']}
  if r.get('artifact'):
   prior=1 if index==2 else 2 if index==4 else None
   old=(d.get('liveRuns',{}).get(str(prior)) if d['mode']=='live_model' else runs.get(IDS.get(prior)))
   if old and old.get('artifact') and (role=='supplier' or index==4):
    out['changes']=changes(old['artifact'],r['artifact']);out['previousSummary']=old['artifact']['summary']
   if role=='supplier' and out['activity'] is None and not(d.get('job') and d['job']['status']=='running'):out['activity']=describe(r)
 return out
def advance(d,role,action,revision):
 if revision!=d['revision']:raise ValueError('Replay changed. Reload before advancing.')
 if d.get('job',{} ) and d['job']['status']=='running':raise ValueError('Wait for real model execution to finish.')
 allowed={0:('supplier','review',1),1:('supplier','reply',2),2:('supplier','share',3)}
 if d['stage'] in allowed:
  who,verb,nxt=allowed[d['stage']]
  if (role,action)!=(who,verb):raise ValueError('This step belongs to '+who+'.')
 elif d['stage']==3 and role=='planner' and action in ['alternative','stop']:nxt=4 if action=='alternative' else 5
 elif d['stage']==4 and role=='planner' and action=='stop':nxt=5
 elif d['stage']==4 and role=='supplier' and action=='share_alternative' and d['mode']=='live_model':nxt=6
 elif d['stage']==6 and role=='planner' and action=='stop':nxt=5
 else:raise ValueError('Action unavailable. Start a new replay to explore another branch.')
 if d['mode']=='live_model' and nxt in [1,2,4]:start_live(d,nxt,action,role);return d
 d['events'].append({'action':action,'role':role,'from':d['stage'],'to':nxt,'recordedAt':time.time(),'execution':('historical replay selection' if d['mode']=='historical_replay' else 'local authorization') if action!='stop' else 'local closure rule'})
 d['stage']=nxt;d['revision']+=1;save(d);return d
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def reply(self,status,data,mime='application/json'):
  raw=json.dumps(data).encode() if mime=='application/json' else data
  self.send_response(status);self.send_header('Content-Type',mime+'; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'");self.end_headers();self.wfile.write(raw)
 def valid(self):return self.headers.get('Host') in ['127.0.0.1:8796','localhost:8796']
 def do_GET(self):
  if not self.valid():return self.reply(403,{'error':'Loopback only'})
  u=urlparse(self.path)
  files={'/planner.js':('planner.js','text/javascript'),'/':('index.html','text/html'),'/replay':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}
  if u.path in files:
   name,mime=files[u.path];return self.reply(200,(ROOT/name).read_bytes(),mime)
  try:
   if u.path!='/api/state':raise ValueError('Unknown endpoint')
   q=parse_qs(u.query);role=q.get('role',['planner'])[0]
   if role not in ['supplier','planner']:raise ValueError('Invalid role')
   with LOCK:d=json.loads(file(q.get('id',[''])[0]).read_text());self.reply(200,public(d,role))
  except (ValueError,FileNotFoundError) as e:self.reply(409,{'error':str(e)})
 def do_POST(self):
  if not self.valid() or self.headers.get('X-Demo-Request')!='local' or self.headers.get('Origin') not in [None,'http://127.0.0.1:8796','http://localhost:8796']:return self.reply(403,{'error':'Local same-origin request required'})
  try:
   length=int(self.headers.get('Content-Length',0))
   if length>2000:raise ValueError('Request too large')
   b=json.loads(self.rfile.read(length) or '{}')
   with LOCK:
    if self.path=='/api/new':return self.reply(200,{'id':create(b.get('mode','historical_replay'))['id']})
    if self.path!='/api/advance':raise ValueError('Unknown endpoint')
    role=b.get('role');d=json.loads(file(b.get('id','')).read_text());advance(d,role,b.get('action'),b.get('revision'));self.reply(200,public(d,role))
  except (ValueError,FileNotFoundError) as e:self.reply(409,{'error':str(e)})
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8796),Handler).serve_forever()
