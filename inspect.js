const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new', args:['--no-sandbox']
  });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1');
  await page.setViewport({width:414,height:900,isMobile:true});
  const errors=[];
  page.on('console',m=>{ if(m.type()==='error') errors.push(m.text().slice(0,140)); });
  await page.goto('https://victtorino.cl/categoria-producto/griferia/?pp='+Date.now(),{waitUntil:'networkidle2',timeout:60000});
  await new Promise(r=>setTimeout(r,4000));
  const data = await page.evaluate(()=>{
    const out=[];
    const imgs=document.querySelectorAll('.vtr-img-primary, .vtno-img-primary, .e-loop-item .elementor-widget-theme-post-featured-image img');
    let c=0;
    for(const img of imgs){ if(c++>=3) break;
      const cs=getComputedStyle(img); const r=img.getBoundingClientRect();
      const p=img.parentElement, pcs=getComputedStyle(p), pr=p.getBoundingClientRect();
      out.push({cls:img.className.slice(0,35), op:cs.opacity, disp:cs.display, vis:cs.visibility,
        w:Math.round(r.width), h:Math.round(r.height), nat:img.naturalWidth+'x'+img.naturalHeight,
        parent:p.className.slice(0,30), pH:Math.round(pr.height), pPos:pcs.position, pPad:pcs.paddingTop});
    }
    return out;
  });
  console.log(JSON.stringify({images:data, jsErrors:errors.slice(0,6)},null,2));
  await browser.close();
})();
