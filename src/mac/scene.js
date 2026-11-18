import {setup} from './look.js';
/* The laptop on a slide. Khalid, 2026-11-17: "where the laptop is closed and animates and opens in the scene in 3d flipping or rotating way, smooth, cinematic";
   "the video does not match the ratio of the macbook"; "they [the graphics] can stay but repositioned to breathing room space".
   - a perspective camera on the display's normal: at rest the display is an undistorted rectangle, the deck recedes in perspective
   - entrance: the closed laptop arrives turned and tipped toward the viewer, from further away, and swings round to face the viewer while the lid opens
   - the film covers the whole display (the model's panel is 1.549:1, the film 1.6:1: 1.6 % is cropped on each side, nothing is letterboxed)
   - the slide's sources and cards move into the title column (sources above the text, cards under it); connectors and their nodes are hidden */
export async function create({THREE,GLTFLoader,MeshoptDecoder,slide,state,reduced,CONFIG,url,fail,isStale}) {
  const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});
  renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NeutralToneMapping;
  const FOV=20, TAN=Math.tan(THREE.MathUtils.degToRad(FOV)/2), scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(FOV,1,.1,4000);
  const canvas=renderer.domElement;canvas.className='mac-canvas';canvas.setAttribute('aria-label','Laptop showing a fictional Cortex demonstration');
  Object.assign(canvas.style,{position:'absolute',pointerEvents:'none'});
  const slot=slide.querySelector('.slot'), deck=document.getElementById('deck');
  const video=document.createElement('video');Object.assign(video,{muted:true,loop:true,playsInline:true,preload:'metadata',poster:url(CONFIG.poster)});
  let frame=0,active=false,start=0,last=0,pivot,panel,poster,texture,dead=false,playRequested=false,rig,pose=null,cw=912,ch=760,needLayout=true;
  const closed=THREE.MathUtils.degToRad(110.08), openAngle=THREE.MathUtils.degToRad(20), textures=new Set();
  const kids=[...slot.children], moved=[];
  /* slot children by role, in the order build_site writes them (src/data/<key>.json) */
  const chips=CONFIG.chips.map(i=>kids[i]), cards=CONFIG.cards.map(i=>kids[i]);
  kids.forEach(k=>{if(!chips.includes(k)&&!cards.includes(k))k.classList.add('mac-hide');});

  /* design-pixel box relative to the slot: the slot and the title column travel together during a slide transition, so this stays true mid-transition */
  function rel(el){const r=el.getBoundingClientRect(),s=slot.getBoundingClientRect(),k=deck.getBoundingClientRect().height/900;return {x:(r.left-s.left)/k,y:(r.top-s.top)/k,w:r.width/k,h:r.height/k};}
  function moveTo(el,x,y){el.style.translate='';const a=rel(el);el.style.translate=(x-a.x)+'px '+(y-a.y)+'px';if(!moved.includes(el))moved.push(el);}
  /* sources in rows above the title block (wrapping inside the column), cards stacked under the lede; y is measured from the slot's top (72 on the artboard) */
  function layoutGraphics(){
    const block=slide.querySelector('.tblock');if(!block||!slot.getBoundingClientRect().width)return false;
    const tb=rel(block), X=tb.x, W=Math.max(tb.w,444), GAP=16, ROW=12, TOP=-8, BOTTOM=724;
    const sizes=chips.map(c=>{c.style.translate='';return rel(c);});
    const rows=[[]];let x=0;
    sizes.forEach((s,i)=>{if(x>0&&x+s.w>W){rows.push([]);x=0;}rows[rows.length-1].push(i);x+=s.w+GAP;});
    const rowH=Math.max(...sizes.map(s=>s.h)), total=rows.length*rowH+(rows.length-1)*ROW;
    let y=Math.max(TOP,tb.y-40-total);
    rows.forEach(r=>{let cx=X;r.forEach(i=>{moveTo(chips[i],cx,y);cx+=sizes[i].w+GAP;});y+=rowH+ROW;});
    const hs=cards.map(c=>{c.style.translate='';return rel(c).h;}), need=hs.reduce((a,b)=>a+b,0)+ROW*(cards.length-1);
    let cy=tb.y+tb.h+40;if(cy+need>BOTTOM)cy=Math.max(tb.y+tb.h+16,BOTTOM-need);
    cards.forEach((c,i)=>{moveTo(c,X,cy);cy+=hs[i]+ROW;});
    return true;
  }
  /* the canvas covers the whole free area: from the title column to the right margin, from the chapter bar to the footer rule */
  function place(){
    const ex=parseFloat(getComputedStyle(deck).getPropertyValue('--ex'))||0;
    const x0=504,x1=1440+ex-12,y0=52,y1=812,sx=504+ex,sy=72;
    cw=x1-x0;ch=y1-y0;
    Object.assign(canvas.style,{left:(x0-sx)+'px',top:(y0-sy)+'px',width:cw+'px',height:ch+'px'});
    needLayout=!layoutGraphics();
  }
  const langWatch=new MutationObserver(()=>{if(!dead)requestAnimationFrame(()=>{if(!dead)needLayout=!layoutGraphics();});});
  function dispose(){
    if(dead)return;dead=true;cancelAnimationFrame(frame);video.pause();video.removeAttribute('src');video.load();
    removeEventListener('resize',resize);removeEventListener('orientationchange',resize);langWatch.disconnect();
    kids.forEach(k=>k.classList.remove('mac-hide'));moved.forEach(el=>{el.style.translate='';});
    scene.traverse(o=>{o.geometry?.dispose();for(const m of o.material?(Array.isArray(o.material)?o.material:[o.material]):[]){for(const t of Object.values(m))if(t?.isTexture)textures.add(t);m.dispose();}});
    textures.forEach(t=>{t.dispose();t.image?.close?.();});scene.environment?.dispose();renderer.dispose();renderer.forceContextLoss();canvas.remove();video.remove();
  }
  function resize(){
    if(dead)return;const scale=deck.getBoundingClientRect().height/900;place();
    renderer.setPixelRatio(Math.min(2,devicePixelRatio*scale));renderer.setSize(Math.round(cw),Math.round(ch),false);
    if(pose){frameCamera();if(!active){applyPose(reduced||state.open>=1?1:0);renderer.render(scene,camera);}}
  }
  /* the camera sits on the display's normal; distance and aim are solved so the open laptop fills the canvas with a 6 % margin */
  const v=new THREE.Vector3();
  function frameCamera(){
    const {n,up,right,pts}=pose, aspect=cw/ch, target=pose.home.clone();let d=pose.d;
    for(let pass=0;pass<6;pass++){
      camera.aspect=aspect;camera.up.copy(up);camera.position.copy(target).addScaledVector(n,d);camera.lookAt(target);camera.updateProjectionMatrix();camera.updateMatrixWorld(true);
      if(pass===5)break;
      let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
      for(const p of pts){v.copy(p).project(camera);x0=Math.min(x0,v.x);x1=Math.max(x1,v.x);y0=Math.min(y0,v.y);y1=Math.max(y1,v.y);}
      target.addScaledVector(right,(x0+x1)/2*d*TAN*aspect).addScaledVector(up,(y0+y1)/2*d*TAN);
      d*=Math.max((x1-x0)/2,(y1-y0)/2)*1.06;
    }
    pose.d=d;state.screen={width:cw*pose.screenW/(2*d*TAN*aspect),scale:1};
  }
  const io=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2, out=x=>1-Math.pow(1-x,4), c01=x=>Math.max(0,Math.min(1,x));
  const qa=new THREE.Quaternion(),qb=new THREE.Quaternion();
  /* p 0..1. 0: closed, turned and tipped toward the viewer, further away and lower. 1: open, facing the viewer. */
  function applyPose(p){
    const {n,up,right,home,d}=pose, turn=1-io(c01(p/.94)), far=1-io(c01(p/.85)), lid=io(c01((p-.16)/.84));   /* the turn and the lid overlap: the laptop is still swinging round while it opens */
    qa.setFromAxisAngle(up,THREE.MathUtils.degToRad(CONFIG.yaw)*turn);qb.setFromAxisAngle(right,THREE.MathUtils.degToRad(CONFIG.pitch)*turn);
    rig.quaternion.copy(qb).multiply(qa);
    rig.position.copy(home).addScaledVector(n,-d*.5*far).addScaledVector(up,-pose.h*.06*far);
    pivot.rotation.x=THREE.MathUtils.lerp(closed,openAngle,lid);state.open=p>=1?1:lid*.999;state.pose=p;
  }
  try {
    const lookDev=setup(THREE,renderer,scene);
    const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync(url(CONFIG.model));scene.add(gltf.scene);scene.updateMatrixWorld(true);
    if(isStale()){dispose();return {dispose};}
    scene.traverse(o=>{for(const m of o.material?(Array.isArray(o.material)?o.material:[o.material]):[])for(const t of Object.values(m))if(t?.isTexture)textures.add(t);});
    const lid=gltf.scene.getObjectByName('GyAtsALzJhKEkPM');panel=gltf.scene.getObjectByName('SadnAkehSlxIwKv');
    gltf.scene.getObjectByName('OrhpMXCxeprcNok').visible=false;
    pivot=new THREE.Group();pivot.position.set(0,-.265,-11.7145);lid.parent.add(pivot);pivot.updateMatrixWorld(true);pivot.attach(lid);
    const sourceUV=panel.geometry.attributes.uv;
    const uv=new THREE.Float32BufferAttribute(Array.from({length:sourceUV.count},(_,i)=>[sourceUV.getX(i),sourceUV.getY(i)]).flat(),2);
    panel.geometry.setAttribute('uv',uv);
    /* cover: the film's full height on the display's full height, its width cropped to the display's ratio */
    const keep=(32.69446/21.11002)/1.6;
    for(let i=0;i<uv.count;i++)uv.setXY(i,.5+((uv.getX(i)-.012675)/.973315-.5)*keep,1-(uv.getY(i)-.013103)/.972620);uv.needsUpdate=true;
    const old=panel.material;for(const t of Object.values(old))if(t?.isTexture)textures.add(t);old.dispose();
    poster=await new THREE.TextureLoader().loadAsync(url(CONFIG.poster));poster.flipY=false;poster.colorSpace=THREE.SRGBColorSpace;textures.add(poster);
    if(isStale()){dispose();return {dispose};}
    texture=new THREE.VideoTexture(video);texture.flipY=false;texture.colorSpace=THREE.SRGBColorSpace;textures.add(texture);
    panel.material=new THREE.MeshBasicMaterial({map:poster,toneMapped:false});
    panel.material.onBeforeCompile=s=>{s.fragmentShader=s.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
      if(vMapUv.x<0.0||vMapUv.x>1.0||vMapUv.y<0.0||vMapUv.y>1.0)diffuseColor.rgb=vec3(0.0);`);};
    lookDev(gltf.scene,panel);
    /* measure the open laptop along the display's own axes */
    pivot.rotation.x=openAngle;scene.updateMatrixWorld(true);
    const normal=panel.geometry.attributes.normal;
    const n=new THREE.Vector3().fromBufferAttribute(normal,0).applyMatrix3(new THREE.Matrix3().getNormalMatrix(panel.matrixWorld)).normalize();
    if(n.z<0)n.negate();
    const up=new THREE.Vector3(0,1,0).addScaledVector(n,-n.y).normalize(), right=new THREE.Vector3().crossVectors(up,n).normalize();
    const pts=[], box=new THREE.Box3();
    gltf.scene.traverse(o=>{if(!o.isMesh||!o.visible)return;const a=o.geometry.attributes.position;for(let i=0;i<a.count;i+=2){const p=new THREE.Vector3().fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld);pts.push(p);box.expandByPoint(p);}});
    const pbox=new THREE.Box3().setFromObject(panel), size=box.getSize(new THREE.Vector3());
    pose={n,up,right,pts,home:box.getCenter(new THREE.Vector3()),h:size.y,screenW:pbox.max.x-pbox.min.x,d:size.x/(2*TAN)};
    /* the rig turns the laptop about its own centre */
    rig=new THREE.Group();rig.position.copy(pose.home);scene.add(rig);rig.updateMatrixWorld(true);rig.attach(gltf.scene);
    video.addEventListener('error',()=>{if(!dead)fail('Video load failed');});
    video.addEventListener('playing',()=>{panel.material.map=texture;panel.material.needsUpdate=true;});
    video.src=url(CONFIG.video);video.load();
    canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();if(!dead)fail('WebGL context lost');});
    video.hidden=true;slot.append(canvas);slot.append(video);addEventListener('resize',resize);addEventListener('orientationchange',resize);
    langWatch.observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-lang']});
    place();frameCamera();applyPose(reduced?1:0);resize();renderer.render(scene,camera);
    function tick(now){
      frame=0;if(!active||dead)return;
      if(needLayout)needLayout=!layoutGraphics();
      const p=reduced?1:c01((now-start-CONFIG.delay)/CONFIG.duration);applyPose(p);
      if(last&&p>0){const a=state.frames[p<1?'opening':'playing'];a.push(now-last);if(a.length>600)a.shift();}last=now;
      if(!reduced&&state.open>.6&&!playRequested){playRequested=true;video.play().catch(e=>{if(active&&!dead)fail(e);});}
      renderer.render(scene,camera);if(!reduced||needLayout)frame=requestAnimationFrame(tick);
    }
    function hide(){video.pause();applyPose(reduced?1:0);}
    return {dispose,hide,setActive(value,entered){
      if(active===value)return;active=value;state.active=value;cancelAnimationFrame(frame);frame=0;last=0;
      if(value){start=Math.max(entered,performance.now()-CONFIG.delay);playRequested=false;video.currentTime=0;panel.material.map=poster;panel.material.needsUpdate=true;needLayout=!layoutGraphics();frame=requestAnimationFrame(tick);}
      else {video.pause();if(slide.hidden)hide();}
    }};
  } catch(e){dispose();throw e;}
}
