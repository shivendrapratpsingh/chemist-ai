/**
 * Maa Gayatri Pharmacy — "Lotus Aarti" opening.
 *
 * Injects a full-screen overlay, plays for ~4.5s, then dissolves into the page.
 * Plays once per browser tab session (sessionStorage), is skippable on tap/key,
 * and is bypassed entirely for prefers-reduced-motion.
 *
 * Load it as the first thing inside <body> so it covers the page before the
 * rest of the markup paints.
 */
(function () {
  var KEY = 'mg_intro_seen';
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) { /* private mode */ }
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  try { sessionStorage.setItem(KEY, '1'); } catch (e) {}

  var CSS = `
#mg-intro{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;
  overflow:hidden;cursor:pointer;
  background:radial-gradient(ellipse 80% 70% at 50% 55%,#400c1c 0%,#2b0713 42%,#12030a 78%,#080106 100%);
  transition:opacity .95s ease,transform .95s cubic-bezier(.5,0,.3,1);
  font-family:'Segoe UI',system-ui,sans-serif;}
#mg-intro.mg-done{opacity:0;transform:scale(1.2) rotate(1.5deg);pointer-events:none;}
#mg-intro .mg-haze{position:absolute;inset:0;opacity:0;animation:mg-fade 2s ease .5s forwards;
  background:radial-gradient(ellipse 45% 55% at 50% 62%,rgba(255,138,31,.18),transparent 70%),
             radial-gradient(ellipse 30% 30% at 22% 78%,rgba(224,49,107,.12),transparent 70%),
             radial-gradient(ellipse 30% 30% at 78% 78%,rgba(232,185,63,.12),transparent 70%);}
@keyframes mg-fade{to{opacity:1}}

#mg-intro .mg-mandala{position:absolute;left:50%;top:47%;width:min(96vw,560px,88vh);aspect-ratio:1;
  transform:translate(-50%,-50%) scale(.5);opacity:0;
  animation:mg-md 2s cubic-bezier(.2,.9,.3,1) 1.2s forwards;}
#mg-intro .mg-mandala svg{width:100%;height:100%;animation:mg-spin 46s linear infinite;}
#mg-intro .mg-mandala .mg-rev{animation:mg-spinr 34s linear infinite;transform-origin:150px 150px;}
@keyframes mg-md{to{opacity:.85;transform:translate(-50%,-50%) scale(1)}}
@keyframes mg-spin{to{transform:rotate(360deg)}}
@keyframes mg-spinr{to{transform:rotate(-360deg)}}

#mg-intro .mg-lotus{position:absolute;left:50%;top:41%;width:min(74vw,390px,62vh);aspect-ratio:1;
  transform:translate(-50%,-50%);z-index:3;pointer-events:none;opacity:.6;filter:blur(.4px);}
#mg-intro .mg-lotus i{position:absolute;left:50%;top:50%;width:15%;height:40%;margin-left:-7.5%;
  background:linear-gradient(180deg,rgba(255,233,174,.5),rgba(255,138,31,.34) 55%,rgba(224,49,107,.2));
  border-radius:50% 50% 46% 46%/62% 62% 38% 38%;
  transform-origin:50% 100%;transform:translateY(-100%) rotate(var(--a)) scaleY(.05) scaleX(.5);
  opacity:0;filter:drop-shadow(0 0 12px rgba(255,150,60,.5));
  animation:mg-petal 1.5s cubic-bezier(.22,1.2,.36,1) forwards;animation-delay:var(--d);}
@keyframes mg-petal{0%{opacity:0;transform:translateY(-100%) rotate(var(--a)) scaleY(.05) scaleX(.5)}
  45%{opacity:1}100%{opacity:.9;transform:translateY(-100%) rotate(var(--a)) scaleY(1) scaleX(1)}}
#mg-intro.mg-closing .mg-lotus i{animation:mg-close .8s ease forwards;}
@keyframes mg-close{to{opacity:0;transform:translateY(-100%) rotate(var(--a)) scaleY(.1) scaleX(.4)}}

#mg-intro .mg-seed{position:absolute;left:50%;top:50%;width:26px;height:38px;margin:-30px 0 0 -13px;z-index:5;
  background:radial-gradient(ellipse at 50% 70%,#fffbe8 0%,#ffd166 38%,#ff8a1f 62%,rgba(255,90,20,0) 78%);
  border-radius:50% 50% 45% 45%/68% 68% 32% 32%;transform:scale(0);
  animation:mg-seed .85s cubic-bezier(.2,1.4,.4,1) .2s forwards,mg-seedout .7s ease 1.7s forwards,
            mg-flick .18s ease-in-out infinite alternate;}
@keyframes mg-seed{to{transform:scale(1.25)}}
@keyframes mg-seedout{to{opacity:0;transform:scale(.2) translateY(-20px)}}
@keyframes mg-flick{to{filter:brightness(1.25);transform:scale(1.15) translateY(-2px)}}

#mg-intro .mg-stage{position:relative;z-index:4;display:flex;flex-direction:column;align-items:center;}
#mg-intro .mg-devi{width:min(52vw,215px,32vh);height:auto;overflow:visible;position:relative;z-index:6;
  opacity:0;transform:translateY(26px) scale(.85);
  animation:mg-devi 1.5s cubic-bezier(.2,.9,.3,1) 1.5s forwards;
  filter:drop-shadow(0 0 8px rgba(255,170,60,.9)) drop-shadow(0 0 26px rgba(255,110,30,.5));}
@keyframes mg-devi{to{opacity:1;transform:none}}
#mg-intro .mg-devi .ln{stroke:#ffe9ae;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;fill:none;}
#mg-intro .mg-devi .ln.f{fill:rgba(255,180,80,.14);}
#mg-intro .mg-devi .halo{stroke:rgba(255,225,170,.5);fill:none;stroke-width:1;}

#mg-intro .mg-diya{position:absolute;bottom:16%;width:66px;opacity:0;
  animation:mg-diya 1s ease 2.3s forwards;z-index:6;}
#mg-intro .mg-diya.l{left:9%}#mg-intro .mg-diya.r{right:9%}
@keyframes mg-diya{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
#mg-intro .mg-flame{transform-box:fill-box;transform-origin:50% 100%;
  animation:mg-fl 1.1s ease-in-out infinite alternate;}
#mg-intro .mg-flame.b{animation-duration:.85s;animation-delay:-.3s;}
@keyframes mg-fl{from{transform:scale(1) rotate(-3deg)}to{transform:scale(1.16) rotate(4deg)}}

#mg-intro .mg-fall{position:absolute;inset:0;z-index:5;pointer-events:none;overflow:hidden;}
#mg-intro .mg-fall i{position:absolute;top:-24px;width:11px;height:7px;border-radius:60% 40% 55% 45%;
  background:linear-gradient(120deg,#ffd166,#ff8a1f 60%,#e0316b);opacity:0;
  box-shadow:0 0 7px rgba(255,140,50,.55);animation:mg-drop linear infinite;}
@keyframes mg-drop{0%{opacity:0;transform:translateY(0) rotate(0) translateX(0)}
  10%{opacity:.95}100%{opacity:0;transform:translateY(106vh) rotate(560deg) translateX(50px)}}

#mg-intro .mg-wm{text-align:center;margin-top:30px;position:relative;z-index:6;opacity:0;
  animation:mg-wm 1.1s cubic-bezier(.2,.9,.3,1) 2.75s forwards;}
@keyframes mg-wm{from{opacity:0;transform:translateY(18px) scale(.96)}to{opacity:1;transform:none}}
#mg-intro .mg-dev{font-family:'Noto Sans Devanagari','Nirmala UI','Mangal',sans-serif;
  font-size:clamp(19px,5vw,28px);color:#ffe9ae;text-shadow:0 0 26px rgba(255,160,60,.65);}
#mg-intro .mg-en{font-size:clamp(15px,3.9vw,22px);font-weight:900;letter-spacing:clamp(3px,1.4vw,7px);
  margin-top:8px;background:linear-gradient(180deg,#fff4dc,#e8b93f 58%,#b07a17);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
#mg-intro .mg-rule{width:0;height:1px;margin:12px auto 9px;
  background:linear-gradient(90deg,transparent,#ff8a1f,transparent);animation:mg-rule 1s ease 3.05s forwards;}
@keyframes mg-rule{to{width:min(76vw,290px)}}
#mg-intro .mg-sub{font-size:11px;letter-spacing:3.4px;text-transform:uppercase;color:rgba(255,220,180,.6);}
#mg-intro .mg-skip{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);z-index:9;
  font-size:10.5px;letter-spacing:2.6px;text-transform:uppercase;color:rgba(255,220,180,.4);
  opacity:0;animation:mg-fade .8s ease 3.3s forwards;}
@media(max-width:600px){#mg-intro .mg-diya{width:52px}}
@media(max-height:620px){#mg-intro .mg-wm{margin-top:14px}#mg-intro .mg-diya{width:46px;bottom:9%}
  #mg-intro .mg-sub{display:none}}
`;

  var DEVI = '<svg class="mg-devi" viewBox="0 0 240 300" fill="none" aria-label="Maa Gayatri in namaste">'
    + '<circle class="halo" cx="120" cy="92" r="56"/>'
    + '<circle class="halo" cx="120" cy="92" r="63" stroke-dasharray="1.5 6"/><g>'
    + '<path class="ln f" d="M96 76 L104 48 L112 68 L120 38 L128 68 L136 48 L144 76 Q120 68 96 76 Z"/>'
    + '<circle class="ln f" cx="120" cy="46" r="3.4"/>'
    + '<path class="ln" d="M97 92 Q90 54 120 50 Q150 54 143 92"/>'
    + '<path class="ln" d="M97 96 Q88 124 95 146"/><path class="ln" d="M143 96 Q152 124 145 146"/>'
    + '<ellipse class="ln" cx="120" cy="94" rx="21" ry="25"/>'
    + '<circle class="ln f" cx="120" cy="80" r="2.6"/>'
    + '<path class="ln" d="M105 86 Q110 82.5 115.5 85"/><path class="ln" d="M135 86 Q130 82.5 124.5 85"/>'
    + '<path class="ln" d="M106 92 Q110.5 96 115.5 92.5"/><path class="ln" d="M134 92 Q129.5 96 124.5 92.5"/>'
    + '<path class="ln" d="M120 90 L119 102 Q119.5 104.5 122.5 104"/>'
    + '<path class="ln" d="M114 110 Q120 106.5 126 110 Q120 114.5 114 110 Z"/>'
    + '<path class="ln" d="M99 96 Q95 100 99 105"/><path class="ln" d="M141 96 Q145 100 141 105"/>'
    + '<circle class="ln f" cx="98" cy="110" r="3"/><circle class="ln f" cx="142" cy="110" r="3"/>'
    + '<path class="ln" d="M111 116 L110 128"/><path class="ln" d="M129 116 L130 128"/>'
    + '<path class="ln" d="M104 130 Q120 143 136 130"/><path class="ln" d="M100 136 Q120 155 140 136"/>'
    + '<path class="ln" d="M104 129 C82 140 68 178 63 218"/><path class="ln" d="M136 129 C158 140 172 178 177 218"/>'
    + '<path class="ln" d="M63 218 Q120 236 177 218"/>'
    + '<path class="ln" d="M96 150 Q104 190 96 218"/><path class="ln" d="M144 150 Q136 190 144 218"/>'
    + '<path class="ln" d="M105 134 C86 148 79 178 96 186 C105 190 111 185 113 179"/>'
    + '<path class="ln" d="M135 134 C154 148 161 178 144 186 C135 190 129 185 127 179"/>'
    + '<path class="ln" d="M89 176 Q96 180 101 176"/><path class="ln" d="M151 176 Q144 180 139 176"/>'
    + '<path class="ln f" d="M120 130 C113 139 109 152 109 164 C109 173 113 180 120 181 Z"/>'
    + '<path class="ln f" d="M120 130 C127 139 131 152 131 164 C131 173 127 180 120 181 Z"/>'
    + '<path class="ln" d="M120 130 L120 181"/>'
    + '<path class="ln" d="M117 136 C113 145 111 155 111.5 166"/>'
    + '<path class="ln" d="M123 136 C127 145 129 155 128.5 166"/>'
    + '<path class="ln f" d="M120 216 C108 224 106 238 120 245 C134 238 132 224 120 216 Z"/>'
    + '<path class="ln f" d="M96 220 C82 224 78 238 94 243 C107 240 108 226 96 220 Z"/>'
    + '<path class="ln f" d="M144 220 C158 224 162 238 146 243 C133 240 132 226 144 220 Z"/>'
    + '<path class="ln" d="M62 246 Q120 260 178 246"/></g></svg>';

  function diya(cls) {
    return '<svg class="mg-diya ' + cls + '" viewBox="0 0 80 70" fill="none">'
      + '<g class="mg-flame' + (cls === 'r' ? ' b' : '') + '">'
      + '<path d="M40 6 C48 20 52 26 52 33 C52 42 46 47 40 47 C34 47 28 42 28 33 C28 26 32 20 40 6 Z" fill="url(#mg-fg)"/></g>'
      + '<path d="M16 50 Q40 46 64 50 Q58 66 40 66 Q22 66 16 50 Z" fill="rgba(232,185,63,.22)" stroke="#e8b93f" stroke-width="1.6"/>'
      + '<path d="M16 50 Q40 56 64 50" stroke="#e8b93f" stroke-width="1.2"/>'
      + '<defs><linearGradient id="mg-fg" x1="0" y1="0" x2="0" y2="1">'
      + '<stop offset="0%" stop-color="#fff8dd"/><stop offset="45%" stop-color="#ffce5a"/>'
      + '<stop offset="100%" stop-color="#ff6a12"/></linearGradient></defs></svg>';
  }

  var style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  var el = document.createElement('div');
  el.id = 'mg-intro';
  el.innerHTML =
      '<div class="mg-haze"></div>'
    + '<div class="mg-mandala"><svg viewBox="0 0 300 300" fill="none" stroke="rgba(232,185,63,.42)" stroke-width="1">'
    + '<circle cx="150" cy="150" r="146" stroke-dasharray="2 6"/><circle cx="150" cy="150" r="134"/>'
    + '<circle cx="150" cy="150" r="120" stroke-dasharray="10 5"/>'
    + '<circle cx="150" cy="150" r="96" stroke="rgba(255,138,31,.35)"/>'
    + '<g class="mg-rev" id="mg-md-petals"></g><g id="mg-md-ticks"></g></svg></div>'
    + '<div class="mg-lotus" id="mg-lotus"></div><div class="mg-seed"></div>'
    + '<div class="mg-fall" id="mg-fall"></div>'
    + '<div class="mg-stage">' + DEVI
    + '<div class="mg-wm"><div class="mg-dev">॥ माँ गायत्री फार्मेसी ॥</div>'
    + '<div class="mg-en">MAA GAYATRI PHARMACY</div><div class="mg-rule"></div>'
    + '<div class="mg-sub">Aapke swasthya ki sewa mein</div></div></div>'
    + diya('l') + diya('r')
    + '<div class="mg-skip">Tap anywhere to skip</div>';
  document.body.appendChild(el);

  var NS = 'http://www.w3.org/2000/svg';
  var petals = el.querySelector('#mg-md-petals');
  for (var i = 0; i < 16; i++) {
    var p = document.createElementNS(NS, 'path');
    p.setAttribute('d', 'M150 60 C132 84 132 108 150 122 C168 108 168 84 150 60 Z');
    p.setAttribute('transform', 'rotate(' + (i * 22.5) + ' 150 150)');
    p.setAttribute('stroke', 'rgba(255,138,31,.34)');
    petals.appendChild(p);
  }
  var ticks = el.querySelector('#mg-md-ticks');
  for (var j = 0; j < 48; j++) {
    var a = (j / 48) * Math.PI * 2, r2 = j % 4 ? 140 : 146;
    var l = document.createElementNS(NS, 'line');
    l.setAttribute('x1', 150 + Math.cos(a) * 134); l.setAttribute('y1', 150 + Math.sin(a) * 134);
    l.setAttribute('x2', 150 + Math.cos(a) * r2);  l.setAttribute('y2', 150 + Math.sin(a) * r2);
    l.setAttribute('stroke', 'rgba(232,185,63,.4)');
    ticks.appendChild(l);
  }
  var lotus = el.querySelector('#mg-lotus');
  [[10, 0.5, 1, 1], [10, 0.9, 0.72, 0.85]].forEach(function (ring) {
    for (var k = 0; k < ring[0]; k++) {
      var s = document.createElement('i');
      s.style.setProperty('--a', (k * (360 / ring[0])) + 'deg');
      s.style.setProperty('--d', (ring[1] + k * 0.055) + 's');
      s.style.height = (40 * ring[2]) + '%';
      s.style.opacity = ring[3];
      lotus.appendChild(s);
    }
  });
  var fall = el.querySelector('#mg-fall');
  for (var m = 0; m < 22; m++) {
    var f = document.createElement('i');
    f.style.left = Math.random() * 100 + '%';
    f.style.animationDuration = (7 + Math.random() * 6) + 's';
    f.style.animationDelay = (Math.random() * 10 - 6) + 's';
    fall.appendChild(f);
  }

  var ended = false;
  function end() {
    if (ended) return;
    ended = true;
    el.classList.add('mg-closing');
    setTimeout(function () { el.classList.add('mg-done'); }, 260);
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 1350);
  }
  var timer = setTimeout(end, 4500);
  el.addEventListener('click', function () { clearTimeout(timer); end(); });
  window.addEventListener('keydown', function () { clearTimeout(timer); end(); });
})();
