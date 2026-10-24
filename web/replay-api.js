/* Local browser replay, NOT a security boundary. All fixtures are public and synthetic. */
window.replayApi=async function(path,body){
 const prefix='demand-pulse-team-v31:';
 const load=id=>{const d=JSON.parse(localStorage.getItem(prefix+id)||'null');if(!d)throw Error('Session not found in this browser. Start a new replay.');return d;};
 const save=d=>localStorage.setItem(prefix+d.id,JSON.stringify(d));
 const project=(d,role)=>{
  if(!['supplier','planner'].includes(role))throw Error('Invalid demo role');
  const snapshotStage=d.stage===5?(d.alternative?4:3):d.stage;
  const out=structuredClone(window.REPLAY_SNAPSHOTS[snapshotStage][role]);
  Object.assign(out,{id:d.id,stage:d.stage,revision:d.revision,events:d.events});return out;
 };
 if(path==='/api/new'){
  if(body.mode!=='historical_replay')throw Error('Public website supports replay only. Use the local version for real inference.');
  const d={id:crypto.randomUUID().replaceAll('-',''),stage:0,revision:0,events:[],alternative:false};save(d);return {id:d.id};
 }
 if(path.startsWith('/api/state')){const q=new URL(path,location.origin).searchParams;return project(load(q.get('id')),q.get('role'));}
 if(path==='/api/advance'){
  const d=load(body.id);if(d.revision!==body.revision)throw Error('Session changed. Refresh before continuing.');
  const allowed={0:{supplier:{review:1}},1:{supplier:{reply:2}},2:{supplier:{share:3}},3:{planner:{alternative:4,stop:5}},4:{planner:{stop:5}}};
  const next=allowed[d.stage]?.[body.role]?.[body.action];if(next===undefined)throw Error('Action is not available for this demo role and stage.');
  d.events.push({action:body.action,role:body.role,from:d.stage,to:next,recordedAt:Date.now()/1000,execution:body.action==='stop'?'local closure rule':'historical replay selection'});
  if(body.action==='alternative')d.alternative=true;d.stage=next;d.revision++;save(d);return project(d,body.role);
 }
 throw Error('Unknown replay action');
};
