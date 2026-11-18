// All URLs, including the swappable film, are local to this module.
export const CONFIG = {key:'s15', model:'model/laptop.glb', video:'media/cortex-b214-v2.mp4', poster:'media/poster.png', delay:450, duration:2600,
  /* entrance: degrees the closed laptop starts turned (about the display's up) and tipped toward the viewer */
  yaw:-62, pitch:34,
  /* slot children kept beside the laptop, by index in src/data/s15.json: the four sources left to right, then the actor and result cards */
  chips:[1,10,4,7], cards:[13,14]};
const url = p => new URL(p, import.meta.url).href;
export function mount() {
  const slides=[...document.querySelectorAll('.slide')], slide=slides.find(s=>s.dataset.key===CONFIG.key);
  const device=slide?.querySelector('[data-name="Device · Desktop · Contract file"]');
  if(!device)return;
  const state={status:'idle',open:0,active:false,disposed:true,errors:[],frames:{opening:[],playing:[]}};
  window.BNG_MAC={state};
  /* with the laptop loaded it replaces the flat device; the sources and cards stay and move into the title column (scene.js), connectors are hidden; all of it comes back on dispose or failure */
  const css=document.createElement('style');css.textContent='.slide .slot>.mac-hide{visibility:hidden}';document.head.append(css);
  let instance=null, pending=null, generation=0, entered=0, prior=-1;
  const index=slides.indexOf(slide), reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  function fail(e){state.errors.push(String(e));dispose();state.status='fallback';}
  function dispose(){generation++;instance?.dispose();instance=null;slide.classList.remove('mac-on');state.disposed=true;state.active=false;state.status='disposed';}
  async function load(){
    if(instance||pending)return;
    const token=generation;state.status='loading';
    pending=(async()=>{
      const [THREE,{GLTFLoader},{MeshoptDecoder}]=await Promise.all([import('./vendor/three.module.js'),import('./vendor/loaders/GLTFLoader.js'),import('./vendor/meshopt_decoder.module.js')]);
      if(token!==generation)return;
      const {create}=await import('./scene.js');
      const obj=await create({THREE,GLTFLoader,MeshoptDecoder,device,slide,state,reduced,CONFIG,url,fail,isStale:()=>token!==generation});
      if(token!==generation){obj.dispose();return;}
      instance=obj;state.disposed=false;state.status='ready';slide.classList.add('mac-on');sync();
    })().catch(e=>{if(token===generation)fail(e);}).finally(()=>{pending=null; if((prior===index||prior===index-1)&&!instance&&state.status!=='fallback')sync();});
  }
  function sync(){
    const cur=window.BNG_DECK?.index??-1;
    if(cur!==prior){if(cur===index)entered=performance.now();prior=cur;}
    const active=cur===index;
    if(cur===index||cur===index-1)load();
    if(Math.abs(cur-index)>=2){if(instance||state.status==='loading')dispose();return;}
    state.active=active;
    if(instance){instance.setActive(active,entered);}
  }
  new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:['data-slide']});
  // The outgoing slide remains visible through the deck's sliding transition.
  new MutationObserver(()=>{if(slide.hidden)instance?.hide();}).observe(slide,{attributes:true,attributeFilter:['hidden']});
  sync();
}
