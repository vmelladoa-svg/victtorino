const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  const p = await b.newPage();
  await p.setViewport({width:1366,height:900});
  await p.goto('https://victtorino.cl/categoria-producto/griferia/?d='+Date.now(),{waitUntil:'networkidle0',timeout:60000});
  await new Promise(r=>setTimeout(r,4000));
  await p.screenshot({path:'C:/Users/dell/victtorino/shot_desktop.png', fullPage:false});
  const d = await p.evaluate(()=>{
    const cards=[...document.querySelectorAll('.e-loop-item')];
    const c0=cards[0]?cards[0].getBoundingClientRect():null;
    const cols=c0?cards.filter(c=>Math.abs(c.getBoundingClientRect().top-c0.top)<5).length:0;
    const w=document.querySelector('.e-loop-item .elementor-widget-theme-post-featured-image');
    const wr=w?w.getBoundingClientRect():null;
    const img=w?w.querySelector('img'):null; const ir=img?img.getBoundingClientRect():null;
    return {cols, cardH:c0?Math.round(c0.height):null, widgetW:wr?Math.round(wr.width):null, widgetH:wr?Math.round(wr.height):null, imgH:ir?Math.round(ir.height):null};
  });
  console.log('DESKTOP 1366px:', JSON.stringify(d));
  await b.close();
})();
