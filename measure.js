const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']});
  for (const W of [390, 414]) {
    const p = await b.newPage();
    await p.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile/15E148 Safari/604.1');
    await p.setViewport({width:W,height:900,isMobile:true});
    await p.goto('https://victtorino.cl/categoria-producto/griferia/?m='+Date.now(),{waitUntil:'networkidle2',timeout:60000});
    await new Promise(r=>setTimeout(r,3000));
    const d = await p.evaluate(()=>{
      const card = document.querySelector('.e-loop-item');
      const link = document.querySelector('.e-loop-item .elementor-widget-theme-post-featured-image a') || document.querySelector('.e-loop-item .vtr-hover-wrap');
      const img = document.querySelector('.vtr-img-primary');
      const r=e=>e?{w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height),left:Math.round(e.getBoundingClientRect().left),right:Math.round(e.getBoundingClientRect().right)}:null;
      // cuantas columnas
      const grid = document.querySelector('.elementor-grid, ul.products, .e-loop-item')?.parentElement;
      return {card:r(card), link:r(link), img:r(img), viewport:window.innerWidth, scrollW:document.body.scrollWidth};
    });
    console.log(`\n=== viewport ${W}px ===`);
    console.log('  tarjeta(card):', JSON.stringify(d.card));
    console.log('  cuadro imagen(link):', JSON.stringify(d.link));
    console.log('  imagen:', JSON.stringify(d.img));
    console.log('  ancho página(scrollW):', d.scrollW, '(si > viewport => hay overflow horizontal)');
    if(d.img && d.card) console.log('  >>> imagen', d.img.w>d.card.w+5?'MÁS ANCHA que la tarjeta ❌ (se sale)':'cabe en la tarjeta ✅');
    await p.close();
  }
  await b.close();
})();
