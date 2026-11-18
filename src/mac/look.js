export function setup(THREE,renderer,scene){
const dark=false;
const LOOK = {
  exposure: 1.0,                  // renderer.toneMappingExposure; ?exposure=1.1 overrides for a trial
  envIntensity: 1.0,              // scene.environmentIntensity (strength of the studio reflections)
  body:    {color:'#3b3c3f', metalness:.9,  roughness:.42},  // top case, lid shell, hinge plates
  tray:    {color:'#2a2b2d', metalness:.9,  roughness:.5},   // keyboard tray around the keys
  pad:     {color:'#232426', metalness:.9,  roughness:.36},  // trackpad glass: darker and smoother than the deck
  keys:    {color:'#232427', metalness:0,   roughness:.5},   // keycaps, lighter than the wells
  well:    {color:'#070708', metalness:0,   roughness:1},    // key wells and gaps
  legend:  {color:'#f2f3f5', metalness:0,   roughness:.45},  // key legends
  bezel:   {color:'#050506', metalness:0,   roughness:.3},   // screen bezel glass
  rubber:  {color:'#101012', metalness:0,   roughness:.85},  // feet and trim
  light:   {key:2.2, fill:.7, rim:.5, rimDark:1.6},          // direct lights on top of the environment
  shade:   {core:.8, soft:.42, glow:.11}                    // contact shade alphas (glow is dark stage only)
};
function studio(){
  const s=new THREE.Scene(),G=v=>new THREE.Color().setScalar(v);
  const room=new THREE.Mesh(new THREE.BoxGeometry(16,9,16),new THREE.MeshBasicMaterial({color:G(dark?.05:.16),side:THREE.BackSide}));room.position.y=3.2;s.add(room);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(16,16),new THREE.MeshBasicMaterial({color:G(dark?.45:1.1)}));floor.rotation.x=-Math.PI/2;floor.position.y=-1.2;s.add(floor);  // the probe sits at the origin, so the floor must be below it
  const box=(w,h,p,i)=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:G(i),side:THREE.DoubleSide}));m.position.set(...p);m.lookAt(0,.3,0);s.add(m);};
  box(7,3.6,[-4.6,3.1,-3.4],dark?4:2.6);    // key: large soft box, upper left and behind (what the deck mirrors)
  box(2.2,5.5,[5.2,2.4,-.5],dark?2.5:.9);   // fill: tall, dim strip on the right
  box(9,1.1,[0,5.6,-1.5],dark?7:2);       // top: long overhead strip, lights the lid shoulder
  box(2.4,.9,[0,1.1,-6.2],dark?9:1.6);      // rim strip behind: separates the silhouette
  box(7,2.2,[1.2,1.3,6.6],dark?2:3);        // front card: lifts the chamfers and the front wall
  box(1.4,6,[-6.4,2.5,2.4],dark?14:4);      // left edge strip: bevel highlight
  box(1.4,6,[6.4,2.5,2.4],dark?14:4);       // right edge strip: bevel highlight
  const pm=new THREE.PMREMGenerator(renderer),t=pm.fromScene(s,.03).texture;pm.dispose();s.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});return t;
}
scene.environment=studio(); scene.environmentIntensity=LOOK.envIntensity;
for(const [p,i] of [[[-.5,.7,.35],2.2],[[.6,.3,.4],.7],[[.1,.35,-.7],.5]]){const l=new THREE.DirectionalLight(0xffffff,i);l.position.set(...p);scene.add(l);}
const ROLE={
  body:['zFJMMvikHFjtmzd','pEUnNAGXCoAFoUk','YjmXmicdBWsFQyD','JKvAHnqjqlqshmY','BfIgIOaUEgyoEft','AqVxlXuHIFahLKs','OFvWomWIIUgmKKA'],
  tray:['hZBlDyddxAQhuPm'],
  pad:['AvocVUvikCzzMtu'],
  keys:['RMDHOHZakhhXXHT'],
  well:['wOIDWopwzKBeTNU','tyKqaDjBmuwfmrZ','dkOmcmuFedorUKC','oINmXIPcNKkHSJV','NzmRSNqyvNKhkmK','EKOOVJzobzfBYEj'],
  legend:['ZrrjpMZNDbttBCc'],
  bezel:['dFfswgailNMtaYj','SsSIPrCyVNTOxvd'],
  rubber:['jIhmcgKbjDOICsY','iFCKstMLETFqCmZ','AZirwHJdxxcChtp','kDpbvvjwMgCSCmF','ASadxrcBIAXFnLn','sRPrqogRtliLLae']
};
function lookDev(root,skip){
  const byName=new Map();for(const [role,names] of Object.entries(ROLE))for(const n of names)byName.set(n,role);
  const done=new Set();
  root.traverse(o=>{
    if(!o.isMesh||o===skip||done.has(o.material))return;done.add(o.material);
    const m=o.material,role=byName.get(m.name);if(!role)return;const v=LOOK[role];
    m.color.set(v.color);m.metalness=v.metalness;m.roughness=v.roughness;
    m.metalnessMap=null;m.roughnessMap=null;m.map=null;m.envMapIntensity=1;
    if(m.isMeshPhysicalMaterial)m.specularIntensity=v.specular??1;
    if(role==='legend'){m.polygonOffset=true;m.polygonOffsetFactor=-2;m.polygonOffsetUnits=-2;}
    m.needsUpdate=true;
  });
}
return lookDev;
}
