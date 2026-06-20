const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  for (const [label,url] of [['CANONICAL (lo que abres tú)','https://victtorino.cl/categoria-producto/griferia/'],['con cache-buster','https://victtorino.cl/categoria-producto/griferia/?cb='+Date.now()]]) {
    const p = await b.newPage();
    await p.setViewport({width:412,height:1000,isMobile:true,deviceScaleFactor:2});
    await p.goto(url,{waitUntil:'networkidle0',timeout:60000});
    await new Promise(r=>setTimeout(r,4000));
    const d = await p.evaluate(()=>{
      const w=document.querySelector('.e-loop-item .elementor-widget-theme-post-featured-image');
      if(!w) return {err:'no widget'};
      const wr=w.getBoundingClientRect();
      const fix = !!document.querySelector('#vtr-img-fix') || [...document.querySelectorAll('script')].some(s=>s.textContent.includes('vtr-hover-wrap')&&s.textContent.includes('setProperty'));
      const img=w.querySelector('img'); const ir=img?img.getBoundingClientRect():null;
      return {widgetH:Math.round(wr.height), widgetW:Math.round(wr.width), imgH:ir?Math.round(ir.height):null, fixPresent:fix, age:'-'};
    });
    // headers
    const resp = await p.goto(url,{waitUntil:'domcontentloaded'});
    console.log(`${label}: widget=${d.widgetW}x${d.widgetH} img.h=${d.imgH} fixPresent=${d.fixPresent} | Age=${resp.headers()['age']||'-'}`);
    await p.close();
  }
  await b.close();
})();
