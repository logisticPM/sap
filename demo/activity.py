"""Presentation of observable tool events, not model chain of thought."""
def describe(run):
 events=run.get('events',[]);items=[];sources={}
 for e in events:
  if e['type']!='tool':continue
  name=e['name'];result=e.get('result',{});stamp=e.get('recordedAt')
  if name=='list_sources':
   items.append({'kind':'discovery','label':'Source index checked','detail':str(len(result.get('sources',[])))+' available records','at':stamp})
  elif name=='read_sources':
   for src in result.get('sources',[]):
    if 'id' not in src:continue
    sources[src['id']]=src
    items.append({'kind':'read','label':'Read '+src['id'],'detail':src.get('title',src.get('subject','Source record retrieved')),'at':stamp})
  elif name=='submit_followup':
   items.append({'kind':'accepted' if result.get('accepted') else 'rejected','label':'Review accepted by rule checks' if result.get('accepted') else 'Rule check requested a correction','detail':result.get('error','Citations and typed conditions passed; business truth is not independently verified.'),'at':stamp})
 status=run.get('status','running')
 phase=('Review complete' if status=='completed' else 'Execution stopped' if status=='failed' else 'Revising output after a rule check' if items and items[-1]['kind']=='rejected' else 'Assessing retrieved records' if sources else 'Selecting sources to read')
 return {'runId':run.get('id'),'status':status,'phase':phase,'items':items,'sources':list(sources.values()),'modelResponses':sum(e['type']=='model' for e in events),'startedAt':run.get('activity',{}).get('startedAt')}

def changes(before,after):
 if not before or not after:return []
 rows=[]
 for key,value in after['conditions'].items():
  old=before['conditions'].get(key)
  if old!=value:rows.append({'field':key,'before':old,'after':value})
 if before['next_step']!=after['next_step']:rows.append({'field':'next_action','before':before['next_step'],'after':after['next_step']})
 return rows
