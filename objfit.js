const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  const p = await b.newPage();
  await p.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile/15E148 Safari/604.1');
  await p.setViewport({width:414,height:900,isMobile:true});
  await p.goto('https://victtorino.cl/categoria-producto/griferia/?of='+Date.now(),{waitUntil:'networkidle2',timeout:60000});
  await new Promise(r=>setTimeout(r,3000));
  const d = await p.evaluate(()=>{const i=document.querySelector('.vtr-img-primary');const cs=getComputedStyle(i);const r=i.getBoundingClientRect();return {objectFit:cs.objectFit, h:Math.round(r.height), w:Math.round(r.width)};});
  console.log('  object-fit COMPUTADO:', d.objectFit, '| tamaño:', d.w+'x'+d.h);
  await b.close();
})();
