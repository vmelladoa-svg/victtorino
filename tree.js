const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  const p = await b.newPage();
  await p.setUserAgent('Mozilla/5.0 (Linux; Android 14; SM-S911B) Mobile Safari/537.36');
  await p.setViewport({width:412,height:1200,isMobile:true,deviceScaleFactor:3});
  await p.goto('https://victtorino.cl/categoria-producto/griferia/?tree='+Date.now(),{waitUntil:'networkidle0',timeout:60000});
  await new Promise(r=>setTimeout(r,3500));
  const tree = await p.evaluate(()=>{
    const w=document.querySelector('.e-loop-item .elementor-widget-theme-post-featured-image');
    if(!w) return 'no widget';
    function walk(el,d){
      if(d>6||!el) return '';
      const r=el.getBoundingClientRect(); const cs=getComputedStyle(el);
      let s='  '.repeat(d)+el.tagName.toLowerCase()+'.'+(el.className||'').toString().trim().replace(/\s+/g,'.').slice(0,40)
        +` [${Math.round(r.width)}x${Math.round(r.height)} pos:${cs.position} ar:${cs.aspectRatio} pb:${cs.paddingBottom} of:${cs.objectFit}]`;
      for(const c of el.children) s+='\n'+walk(c,d+1);
      return s;
    }
    return walk(w,0);
  });
  console.log(tree);
  await b.close();
})();
