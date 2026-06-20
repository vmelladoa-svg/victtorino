const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  const p = await b.newPage();
  await p.setUserAgent('Mozilla/5.0 (Linux; Android 14; SM-S911B) Mobile Safari/537.36');
  await p.setViewport({width:360,height:1200,isMobile:true});
  await p.goto('https://victtorino.cl/categoria-producto/griferia/?w2='+Date.now(),{waitUntil:'networkidle0',timeout:60000});
  await new Promise(r=>setTimeout(r,3500));
  const data = await p.evaluate(()=>{
    const w=document.querySelector('.e-loop-item .elementor-widget-theme-post-featured-image');
    if(!w) return {err:'no featured-image widget'};
    const img=w.querySelector('img');
    const out=[]; let el=img||w; let n=0;
    while(el && n++<6){
      const r=el.getBoundingClientRect(); const cs=getComputedStyle(el);
      out.push({tag:el.tagName, cls:(el.className||'').toString().slice(0,40),
        w:Math.round(r.width), h:Math.round(r.height), pos:cs.position,
        padTop:cs.paddingTop, ar:cs.aspectRatio, objFit:cs.objectFit, minH:cs.minHeight});
      el=el.parentElement;
    }
    // tambien: cuantos vtr-img y cuantas imgs por tarjeta
    const card=w.closest('.e-loop-item');
    return {chain:out, vtrCount:document.querySelectorAll('.vtr-img-primary').length, imgsInCard:card?card.querySelectorAll('img').length:0};
  });
  console.log(JSON.stringify(data,null,1));
  await b.close();
})();
