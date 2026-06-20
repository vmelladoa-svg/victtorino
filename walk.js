const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  const p = await b.newPage();
  await p.setUserAgent('Mozilla/5.0 (Linux; Android 14; SM-S911B) Mobile Safari/537.36');
  await p.setViewport({width:360,height:1200,isMobile:true});
  await p.goto('https://victtorino.cl/categoria-producto/griferia/?w='+Date.now(),{waitUntil:'networkidle0',timeout:60000});
  await new Promise(r=>setTimeout(r,3500));
  const data = await p.evaluate(()=>{
    const img=document.querySelector('.vtr-img-primary');
    if(!img) return {err:'no vtr-img-primary'};
    const chain=[]; let el=img; let n=0;
    while(el && n++<7){
      const r=el.getBoundingClientRect(); const cs=getComputedStyle(el);
      chain.push({tag:el.tagName, cls:(el.className||'').toString().slice(0,45),
        w:Math.round(r.width), h:Math.round(r.height),
        pos:cs.position, padTop:cs.paddingTop, ar:cs.aspectRatio, objFit:cs.objectFit, disp:cs.display});
      el=el.parentElement;
    }
    return {chain};
  });
  console.log(JSON.stringify(data,null,1));
  await b.close();
})();
