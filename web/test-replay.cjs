// Offline contract check; no browser or network and no model calls.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const store=new Map();global.window=global;global.location={origin:'https://example.test'};
global.localStorage={getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v)};
vm.runInThisContext(fs.readFileSync(__dirname+'/fixtures.js','utf8'));
vm.runInThisContext(fs.readFileSync(__dirname+'/demand-records.js','utf8'));
vm.runInThisContext(fs.readFileSync(__dirname+'/replay-api.js','utf8'));
(async()=>{
 for(const alt of [false,true]){
  const {id}=await replayApi('/api/new',{mode:'historical_replay'});
  let revision=0;
  const step=async(role,action)=>{const d=await replayApi('/api/advance',{id,role,action,revision});revision=d.revision;return d;};
  await assert.rejects(()=>step('planner','review'));
  await step('supplier','review');await step('supplier','reply');
  const privateView=await replayApi('/api/state?id='+id+'&role=planner');
  assert.equal(privateView.artifact,null);assert.equal(privateView.trace,null);
  await step('supplier','share');
  const shared=await replayApi('/api/state?id='+id+'&role=planner');
  assert.equal(shared.artifact.conditions.qa_release,'unknown');assert.equal(shared.activity,null);
  await assert.rejects(()=>step('planner','alternative'));
  await assert.rejects(()=>step('supplier','demand_review'));
  const checked=await step('planner','demand_review');assert.equal(checked.demand.review,null);assert.equal(checked.demand.checked,true);assert.equal(checked.demand.purchaseAllowed,false);
  if(alt)await step('planner','alternative');
  const closed=await step('planner','stop');assert.equal(closed.stage,5);
  assert.equal(closed.artifact.next_step,alt?'investigate_alternative':'human_tradeoff');
  await assert.rejects(()=>step('planner','alternative'));
 }
 await assert.rejects(()=>replayApi('/api/new',{mode:'live_model'}));
 console.log('PASS: both replay branches, role gates, pre-disclosure projection, retained closed version, live-mode rejection.');
})();
