const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  for (const W of [412, 384, 360, 320]) {
    const p = await b.newPage();
    await p.setUserAgent('Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 Mobile Safari/537.36');
    await p.setViewport({width:W,height:1200,isMobile:true,deviceScaleFactor:3});
    await p.goto('https://victtorino.cl/categoria-producto/griferia/?ww='+W+Date.now(),{waitUntil:'networkidle0',timeout:60000});
    await new Promise(r=>setTimeout(r,3500));
    const d = await p.evaluate(()=>{
      const cards=[...document.querySelectorAll('.e-loop-item')];
      if(!cards.length) return {err:'no cards'};
      // columnas: contar cuantas cards tienen el mismo top que la primera de la grilla
      const c0=cards[0].getBoundingClientRect();
      const cols=cards.filter(c=>Math.abs(c.getBoundingClientRect().top-c0.top)<5).length;
      const img=cards[0].querySelector('.vtr-img-primary, .elementor-widget-theme-post-featured-image img');
      const ir=img?img.getBoundingClientRect():null;
      const wrap=cards[0].querySelector('.vtr-hover-wrap');
      return {cols, cardW:Math.round(c0.width), cardH:Math.round(c0.height),
        imgW:ir?Math.round(ir.width):null, imgH:ir?Math.round(ir.height):null,
        wrapH: wrap?Math.round(wrap.getBoundingClientRect().height):'no-wrap',
        imgsPerCard: cards[0].querySelectorAll('img').length};
    });
    console.log(`W=${W}: cols=${d.cols} | card=${d.cardW}x${d.cardH} | img=${d.imgW}x${d.imgH} | wrapH=${d.wrapH} | imgs/card=${d.imgsPerCard}`);
    await p.close();
  }
  await b.close();
})();
