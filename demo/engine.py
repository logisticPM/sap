from pathlib import Path
import json,os,sqlite3,threading,time,uuid,requests
ROOT=Path(__file__).resolve().parent
RUNTIME=ROOT/'runtime';RUNTIME.mkdir(exist_ok=True)
MODEL='anthropic/claude-sonnet-4.6'
PRICE_IN=3.;PRICE_OUT=15.;MAX_OUTPUT=1400
TOOLS=[]
def tool(name,description,properties=None,required=None):
    return {'type':'function','function':{'name':name,'strict':True,'description':description,'parameters':{'type':'object','properties':properties or {},'required':required or [],'additionalProperties':False}}}

class Budget:
    def __init__(self,path=None,cap=None):
        cap=float(os.environ.get("DEMO_BUDGET_USD","0")) if cap is None else cap
        if not 0<=cap<=9:raise ValueError("Budget must be between 0 and 9 USD")
        self.path=Path(path or RUNTIME/'budget.sqlite');self.cap=cap;self.lock=threading.Lock()
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS calls(id TEXT PRIMARY KEY, reserve REAL, charged REAL, status TEXT, generation TEXT, input_tokens INTEGER, output_tokens INTEGER, created REAL)')
    def status(self):
        with sqlite3.connect(self.path) as db:
            row=db.execute('SELECT COALESCE(SUM(charged),0),COUNT(*),SUM(CASE WHEN status="settled" THEN charged ELSE 0 END),SUM(CASE WHEN status!="settled" THEN 1 ELSE 0 END) FROM calls').fetchone()
        return {'accounted_usd':round(row[0],6),'confirmed_usd':round(row[2] or 0,6),'calls':row[1],'unsettled_calls':row[3] or 0,'stop_limit_usd':self.cap,'authorized_limit_usd':10.,'remaining_usd':round(max(0,self.cap-row[0]),6)}
    def reserve(self,body):
        # UTF-8 bytes conservatively upper-bound ordinary BPE input tokens, plus protocol overhead.
        bound=(len(json.dumps(body,ensure_ascii=False).encode('utf-8'))+4096)*PRICE_IN/1e6+MAX_OUTPUT*PRICE_OUT/1e6
        with self.lock,sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            used=db.execute('SELECT COALESCE(SUM(charged),0) FROM calls').fetchone()[0]
            if used+bound>self.cap:raise RuntimeError('Budget guard: no new request; conservative reserve would exceed the configured local cap.')
            cid=uuid.uuid4().hex
            db.execute('INSERT INTO calls VALUES(?,?,?,?,?,?,?,?)',(cid,bound,bound,'reserved',None,None,None,time.time()))
        return cid,bound
    def settle(self,cid,data):
        usage=data.get('usage',{});cost=usage.get('cost')
        with self.lock,sqlite3.connect(self.path) as db:
            reserve=db.execute('SELECT reserve FROM calls WHERE id=?',(cid,)).fetchone()[0]
            if isinstance(cost,(int,float)) and 0<=cost<=reserve:
                db.execute('UPDATE calls SET charged=?,status="settled",generation=?,input_tokens=?,output_tokens=? WHERE id=?',(cost,data.get('id'),usage.get('prompt_tokens'),usage.get('completion_tokens'),cid))
            else:
                db.execute('UPDATE calls SET status="uncertain",generation=? WHERE id=?',(data.get('id'),cid))
                if isinstance(cost,(int,float)) and cost>reserve:
                    db.execute('UPDATE calls SET charged=? WHERE id=?',(cost,cid))
                    raise RuntimeError('Actual cost exceeded conservative reserve; stop and reconcile.')
    def uncertain(self,cid):
        with sqlite3.connect(self.path) as db:db.execute('UPDATE calls SET status="uncertain" WHERE id=?',(cid,))

class ModelClient:
    def __init__(self,key,budget=None):self.key=key;self.budget=budget or Budget();self.lock=threading.Lock()
    def account(self):
        r=requests.get('https://openrouter.ai/api/v1/key',headers={'Authorization':'Bearer '+self.key},timeout=20)
        if r.status_code!=200:raise RuntimeError('OpenRouter credential check failed: HTTP '+str(r.status_code))
        d=r.json()['data']
        return {k:d.get(k) for k in ['usage','limit','limit_remaining','is_free_tier']}
    def complete(self,messages,role):
        denied='read_frn_snapshot' if role=='supplier' else 'calculate_supply'
        offered_tools=[t for t in TOOLS if t['function']['name']!=denied]
        body=dict(model=MODEL,messages=messages,tools=offered_tools,tool_choice='auto',max_tokens=MAX_OUTPUT,temperature=0,provider={'require_parameters':True,'max_price':{'prompt':PRICE_IN,'completion':PRICE_OUT}},stream=False)
        cid,bound=self.budget.reserve(body)
        start=time.monotonic()
        try:
            r=requests.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json','X-Title':'Demand Pulse local v17'},json=body,timeout=(10,55))
            if r.status_code!=200:
                self.budget.uncertain(cid)
                raise RuntimeError('OpenRouter HTTP '+str(r.status_code)+'; no retry, reserve retained')
            d=r.json();self.budget.settle(cid,d)
            if not d.get('choices'):raise RuntimeError('No model choices')
            return d,round(time.monotonic()-start,3)
        except requests.RequestException:
            self.budget.uncertain(cid);raise RuntimeError('Model network failure; cost reserve retained, no fabricated result') from None