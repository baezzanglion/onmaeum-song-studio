# -*- coding: utf-8 -*-
# 온마음 말씀사진관(print.html) → 굿모닝라이언 행운사진관(lion.html) 변환기
#
# 배경: 굿모닝라이언(회사 로비)은 온마음(교회)과 "같은 엔진, 다른 콘텐츠"다.
#   온마음 print.html 을 유일한 소스로 두고, 이 스크립트가 말씀→행운/응원,
#   교회명→회사명, 색상(teal→gold/coral) 등을 치환해 lion.html 을 생성한다.
#   각 치환은 must()로 "정확히 N번 매칭"을 검증하므로, print.html이 바뀌어
#   앵커가 어긋나면 조용히 깨지지 않고 즉시 실패한다(의도된 안전장치).
#
# 사용법:
#   python3 tools/build_lion.py                 # ./print.html 읽어 ./tools/lion.generated.html 생성
#   python3 tools/build_lion.py <src> <out>     # 경로 직접 지정
# 생성 후: lion.generated.html 을 sponge-intro/lion.html 로 복사해 배포.
import re, sys, os

_here = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_here, "..", "print.html")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_here, "lion.generated.html")
g = open(SRC, encoding="utf-8").read()

def must(a, b, n=1, label=""):
    global g
    cnt = g.count(a)
    assert cnt == n, f"[{label}] expected {n} got {cnt}\n---\n{a[:120]}"
    g = g.replace(a, b, n)

# ---- FORTUNE 엔진 (원본 굿모닝라이언 문구를 날씨별 풀로 분리 + 실시간 날씨 연동) ----
FORTUNE = r'''/* 응원 문구를 날씨별 풀로 분리 — 실제 날씨에 맞는 문구만 나오게 */
const ONE_POOLS = {
  clear: [
    "맑은 날이 너무 또랑또랑해서 살짝 부담스럽기도 하네요","햇살이 먼저 출근해 있는 아침이네요",
    "하늘이 오늘 제일 부지런했네요, 우리는 이제 시작이에요","이런 하늘 아래면 무슨 일이든 절반은 된 기분이죠",
    "창가 자리가 복권 당첨인 날이에요","파란 하늘 한 번 올려다보고 시작해요, 공짜니까요",
    "오늘 하늘은 저장해두고 싶은 색이네요","맑은 아침엔 걸음도 살짝 가벼워지죠",
  ],
  cloudy: [
    "흐린 하늘은 결정장애가 좀 있는 것 같아요","흐린 하늘 아래선 모두가 조금씩 느려져요","흐려도 꽃은 피는 계절의 한복판",
    "흐린 아침은 어쩐지 마음도 늘어지죠","흐린 하늘 아래에서도 시간은 잘 흐르네요","흐림은 어쩌면 비를 안고 있는 마음",
    "구름이 해를 잠깐 맡아두고 있는 아침이에요","흐린 날은 하늘도 재택 중인가 봐요",
  ],
  fog: [
    "안개 낀 아침은 세상이 슬쩍 흐림 모드를 켠 느낌","답답한 안개도 곧 걷힐 거예요","거리를 살짝 흐려놓은 안개의 아침",
    "안개 속에서도 길은 늘 그 자리에 있어요","오늘 아침 세상은 반쯤 필터를 씌웠네요",
  ],
  rain: [
    "빗소리만으로도 BGM이 되는 아침이네요","우산 챙겨 나온 것만으로 오늘 준비성 만점이에요","비 오는 날의 사무실은 어쩐지 아늑하죠",
    "비가 세상 소음을 한 겹 줄여주는 날이에요","젖은 길을 무사히 건너온 당신, 이미 대단해요",
    "비 오는 날 커피 향은 두 배로 진하죠","창밖 비는 회사에서 볼 때 제일 낭만적이에요","빗길 출근은 그 자체로 오늘의 미션 클리어예요",
  ],
  hot: [
    "이 더위를 뚫고 도착한 것만으로 오늘 절반은 성공이에요","에어컨 바람이 세상에서 제일 반가운 아침이네요",
    "아이스 아메리카노가 생명수가 되는 계절이죠","해가 아침부터 의욕이 넘치네요, 우리는 천천히 가요","그늘만 골라 걸어도 칭찬받아 마땅한 날씨예요",
    "오늘 해는 야근까지 할 기세네요, 우리는 정시퇴근해요","시원한 물 한 잔이 보약이 되는 날이에요",
    "더위도 성실한 사람은 못 이겨요, 오늘의 당신처럼","엘리베이터 에어컨 바람에 감사하게 되는 아침이죠","한여름 출근은 그 자체로 체력장 만점이에요",
  ],
  cold: [
    "쌀쌀함은 시간이 흐르면 풀려요. 마음도 그렇겠지요","따뜻한 한 모금이면 충분한 아침이에요","쌀쌀한 아침, 따뜻한 커피 한 잔의 시간",
    "찬 공기에 정신이 번쩍, 오늘 집중력은 보장이에요","웅크린 채로도 어김없이 도착했네요, 멋져요","추운 날엔 실내의 온기가 두 배로 고맙죠",
  ],
  neutral: [
    "출근길 졸음과 커피가 줄다리기하는 아침","어제도 오늘도, 무사히 시작되는 아침","평범하게 출근한다는 것의 든든함",
    "작은 빛 하나가 반가운 아침이에요","마음이 한 박자 늦는 날도 있죠","천천히 출발해도 되는 아침이네요",
    "출근길의 그 묘한 적막함, 이해합니다","오늘은 조금 느긋해도 괜찮아요","오늘은 한 걸음만 천천히 가도 충분해요",
    "잘 시작된 아침이면 그것으로 충분해요","묵묵히 가는 사람의 등을 응원하는 마음","무사히 책상 앞에 앉은 모두에게 작은 박수",
    "사람들의 걸음이 조금 무거워 보이는 날","가로수가 계절의 초록을 머금은 아침","차분한 아침, 조용히 열리는 하루",
    "오늘 아침엔 계절의 잔향이 흐르네요","오늘은 어떤 하루가 될지 궁금해지네요","이 아침이 어디서 왔는지 모를 일이에요",
    "오늘 하루엔 무엇이 남을지 두고 보기로 해요","슬쩍 궁금해지는 아침이네요",
    "오늘도 문을 열고 들어온 당신이 이 아침의 주인공이에요","시작이 반이면, 출근은 이미 절반의 성공이죠",
    "어제의 나보다 한 뼘만 가벼운 마음으로 가요","좋은 일은 예고 없이 오니까, 일단 웃고 시작해요",
    "책상에 앉기 전 심호흡 한 번, 그거면 준비 끝이에요","오늘의 첫 커피가 유난히 맛있을 예감이에요",
    "월급날이 하루 더 가까워진 아침입니다","당신의 걸음마다 하루가 조용히 응원하고 있어요",
    "완벽하지 않아도 돼요, 출발한 것만으로 충분해요","오늘 하루의 제목은 아직 당신이 정할 수 있어요",
  ],
};

/* 서울 현재 날씨 (Open-Meteo · 무료·키 불필요) — 실패해도 날씨 무관 문구로 정상 동작 */
let wx = null; // {temp, code}
async function fetchWeather(){
  try{
    const r = await fetch('https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.978&current=temperature_2m,weather_code&timezone=Asia%2FSeoul');
    const j = await r.json();
    wx = { temp: +j.current.temperature_2m, code: +j.current.weather_code };
  }catch(e){ wx = null; }
}
fetchWeather();
setInterval(fetchWeather, 30*60*1000);   // 로비 상시 거치 → 30분마다 갱신

function wxPool(){
  let pool = ONE_POOLS.neutral.slice();
  if(wx){
    const c = wx.code, t = wx.temp;
    if((c>=51&&c<=67) || (c>=80&&c<=82) || c>=95) pool = pool.concat(ONE_POOLS.rain);
    else if(c===45 || c===48) pool = pool.concat(ONE_POOLS.fog);
    else if(c>=2 && c<=3) pool = pool.concat(ONE_POOLS.cloudy);
    else if(c<=1) pool = pool.concat(ONE_POOLS.clear);
    if(t>=28) pool = pool.concat(ONE_POOLS.hot, ONE_POOLS.hot);        // 더운 날엔 더위 문구 가중
    else if(t<=8) pool = pool.concat(ONE_POOLS.cold, ONE_POOLS.cold);  // 추운 날 동일
  }
  if(new Date().getDay()===4) pool.push("목요일은 늘 금요일을 살짝 시기하죠");
  return pool;
}
const LUCK_COMMENTS = {
  100: ["본부장이 커피 한 잔 쏩니다","오늘은 본부장 커피 찬스","본부장에게 커피 한 잔 청구 가능한 날","오늘 커피는 본부장이 쏘는 걸로","본부장 커피 쿠폰 발동"],
  90: ["오늘은 흐름이 정말 좋아요","산뜻한 일 하나쯤 생길 것 같은 날","괜히 기분 좋은 일이 있을 듯한 날","손에 잡히는 것마다 매끄러운 하루","의외의 좋은 소식이 도착할 수 있어요","일이 술술 풀려갈 가능성이 높은 날","작은 행운들이 곳곳에 숨어있는 하루","마음 가는 대로 가도 잘 풀릴 듯한 날","평소보다 일이 가볍게 느껴질 듯한 날","무엇을 해도 결이 잘 맞을 하루","운이 살짝 어깨에 앉은 듯한 날","일정이 자연스레 연결되는 하루","별일 없이 잘 굴러갈 듯한 평온","일도 마음도 가벼운 흐름의 하루"],
  70: ["전반적으로 무난히 흘러갈 하루","기복 없이 잘 굴러갈 하루","큰 어려움 없이 지나갈 듯한 날","잔잔하지만 안정적인 흐름의 하루","적당히 무던하게 지나갈 하루","평소 페이스대로 가면 좋은 날","일상의 리듬이 잘 맞는 하루","큰 변수 없이 굴러갈 듯한 날","흔들림 없이 지나갈 안정적인 하루","무리 없이 흘러갈 듯한 평온함","평탄하지만 만족스러울 하루","정신없지 않은 차분한 흐름의 날","큰 사건 없이 흘러갈 평일","그럭저럭 잘 흘러갈 하루","안정적으로 흘러갈 듯한 날"],
  50: ["특별할 것 없이 잔잔할 하루","담담하게 지나갈 하루","평소처럼 흘러갈 하루","딱 평균치의 무난한 날","보통의 흐름을 따라가는 하루","특이사항 없이 굴러갈 평일","조용히 지나갈 하루","무던하게 흘려보내기 좋은 날","평범한 일상의 결을 따라가는 하루","큰 기복 없는 평소 같은 하루","어제와 비슷한 흐름의 오늘","특별한 사건 없이 흘러갈 듯한 날","잔잔한 호수처럼 흘러갈 하루","무난한 일과가 펼쳐질 날","늘 그렇듯 흘러갈 평일"],
  30: ["조금 느슨하게 가도 괜찮은 하루","오늘은 천천히 가도 충분해요","서두르지 않아도 되는 하루","쉬엄쉬엄 가도 되는 날","욕심내지 말고 가도 좋을 하루","차분히 보내는 게 좋을 날","마음을 살짝 비우고 가도 되는 하루","오늘은 가볍게 흘려보내도 괜찮아요","한 박자 늦춰도 되는 날","무리하지 않고 가는 게 좋을 하루","작은 일 하나만 잘해도 충분한 날","잠시 쉬어 가도 되는 하루","호흡을 가다듬어도 좋은 날","천천히 흘려보내고 싶은 하루","가볍게 가도 누구도 뭐라 안 할 하루"]
};
function rollLuck(fl=30){ const r=Math.max(Math.random(),Math.random()); return Math.floor(r*(101-fl))+fl; }
function tierOf(s){ return [100,90,70,50,30].find(t=>s>=t); }
function fpick(a){ return a[Math.floor(Math.random()*a.length)]; }
/* 행운 사진관 = 매번이 '행운 요청' → 봇의 행운 모드(floor 70) 적용.
   70~100, 평균 ~90, 90+ 확률 ~50%, 100점(본부장 커피 잭팟) ~3% */
function rollFortune(){ const s=rollLuck(70); return {score:s, oneLiner:fpick(wxPool()), comment:fpick(LUCK_COMMENTS[tierOf(s)])}; }
let fortune = rollFortune();'''

# 1) VERSES 배열 + verseIdx 통째로 → FORTUNE 엔진
m = re.search(r"const VERSES = \[.*?\];\nlet verseIdx = Math\.floor\(Math\.random\(\)\*VERSES\.length\);", g, re.S)
assert m, "VERSES block not found"
g = g[:m.start()] + FORTUNE + g[m.end():]

# 2) balancedWrap 함수 추가 (wrapText 정의 뒤, buildCard 앞)
must(
"function buildCard(mode){",
'''function balancedWrap(ctx, text, maxW){
  const greedy = wrapText(ctx, text, maxW);
  if(greedy.length <= 1) return greedy;
  const target = greedy.length;
  let lo = 0, hi = maxW, best = maxW;
  for(let i=0;i<20;i++){
    const mid = (lo+hi)/2;
    if(wrapText(ctx, text, mid).length <= target){ best = mid; hi = mid; }
    else lo = mid;
  }
  return wrapText(ctx, text, best);
}
function buildCard(mode){''',
1, "balancedWrap+buildCard")

# 3) buildCard: verse/기도제목 추출 → fortune/메시지
must(
'''  const [verse, ref] = VERSES[verseIdx];
  const manual = manualMode && manualText.trim();          // 직접 적기(기도제목) 모드
  const bodyText = manual ? manualText.trim() : verse;
  const bodyRef  = manual ? '🙏 기도제목' : ('— ' + ref + ' —');''',
'''  const f = fortune;
  const manual = manualMode && manualText.trim();          // 직접 적기(메시지) 모드
  const msg = manual ? manualText.trim() : ('"'+f.oneLiner+'"');''',
1, "buildCard f")

# 4) buildCard: 높이 계산 (verseLines → oneLines/cmtLines)
must(
'''  ctx.font = `700 ${30*S}px "Gowun Batang", serif`;
  const verseLines = wrapText(ctx, bodyText, CW-56*S);
  const nameBlock = name ? 74*S : 0;
  const H = (8+34+18)*S + photoH + 14*S + nameBlock + 20*S + verseLines.length*44*S + (34+22+40+44)*S;''',
'''  ctx.font = `700 ${32*S}px "Gowun Batang", serif`;
  const oneLines = balancedWrap(ctx, msg, CW-56*S);
  ctx.font = `${24*S}px "Gowun Batang", serif`;
  const cmtLines = manual ? [] : balancedWrap(ctx, f.comment, CW-56*S);
  const nameBlock = name ? 74*S : 0;
  const H = (8+34+18)*S + photoH + 14*S + nameBlock + 20*S + oneLines.length*46*S + 20*S + cmtLines.length*34*S + (22 + (manual?0:30) + 44)*S;''',
1, "height calc")

# 5) 컬러 카드 교회명/성함 강조색 teal → gold-deep
must("  ctx.font = `700 ${26*S}px \"Gaegu\", cursive`;\n  if(isColor) ctx.fillStyle = '#0F4844';",
     "  ctx.font = `700 ${26*S}px \"Gaegu\", cursive`;\n  if(isColor) ctx.fillStyle = '#9A5E10';",
     1, "church color")
must("    ctx.font = `700 ${44*S}px \"Gaegu\", cursive`;\n    if(isColor) ctx.fillStyle = '#0F4844';",
     "    ctx.font = `700 ${44*S}px \"Gaegu\", cursive`;\n    if(isColor) ctx.fillStyle = '#9A5E10';",
     1, "name color")

# 6) 구분선 색 coral 계열로
must("  ctx.strokeStyle = isColor ? '#C96A3B' : '#000';",
     "  ctx.strokeStyle = isColor ? '#E4643A' : '#000';",
     1, "divider color")

# 7) buildCard 본문: 말씀 블록 → 행운(응원 크게 + 코멘트 + 행운지수 작게)
must(
'''  // 말씀
  ctx.font = `700 ${30*S}px "Gowun Batang", serif`;
  for(const line of verseLines){ y += 44*S; ctx.fillText(line, CW/2, y); }
  y += 34*S;
  ctx.font = `${20*S}px "Gowun Batang", serif`;
  ctx.fillStyle = isColor ? '#6B6152' : '#000';
  ctx.fillText(bodyRef, CW/2, y); y += 22*S;

  // 하단 문구
  ctx.font = `${22*S}px "Gaegu", cursive`;
  ctx.fillStyle = isColor ? '#A84F26' : '#000';
  ctx.fillText(cfg.footer, CW/2, y+26*S);''',
'''  // 응원·메시지 (최상단, 크게)
  ctx.font = `700 ${32*S}px "Gowun Batang", serif`;
  ctx.fillStyle = isColor ? '#2B2620' : '#000';
  for(const line of oneLines){ y += 46*S; ctx.fillText(line, CW/2, y); }
  y += 20*S;
  // 보조 멘트 (코멘트) — 메시지 모드에선 생략
  ctx.font = `${24*S}px "Gowun Batang", serif`;
  ctx.fillStyle = isColor ? '#6B6152' : '#000';
  for(const line of cmtLines){ y += 34*S; ctx.fillText(line, CW/2, y); }
  y += 22*S;
  // 행운지수 (랜덤 모드에서만)
  if(!manual){
    ctx.font = `700 ${22*S}px "Gaegu", cursive`;
    ctx.fillStyle = isColor ? '#B8461F' : '#000';
    ctx.fillText('오늘의 행운지수 ' + f.score, CW/2, y+22*S); y += 30*S;
  }

  // 하단 문구
  ctx.font = `${22*S}px "Gaegu", cursive`;
  ctx.fillStyle = isColor ? '#9A5E10' : '#000';
  ctx.fillText(cfg.footer, CW/2, y+26*S);''',
1, "content block")

# 8) loadCardFonts: verse → fortune 텍스트
must(
'''  const [v, r] = VERSES[verseIdx];
  const d = new Date();
  const batangText = (manualText||'') + ' ' + v + ' — ' + r + ' — ' + `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 0123456789`;
  const gaeguText = cfg.church + ' ' + cfg.footer + ' ' + ($('elderName').value.trim()||'') + ' 온마음 테스트 인쇄 진하기';''',
'''  const f = fortune;
  const d = new Date();
  const batangText = (manualText||'') + ' "'+f.oneLiner+'" ' + f.comment + ' ' + `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 0123456789`;
  const gaeguText = cfg.church + ' ' + cfg.footer + ' ' + ($('elderName').value.trim()||'') + ' 오늘의 행운지수 굿모닝라이언 테스트 인쇄 진하기';''',
1, "loadCardFonts")

# batangText 폰트 로드 크기(30px)도 실제 사용(32px)과 맞게 유지 — 로드는 서브셋 목적이라 무방
# 9) renderPreview verseTag
must(
"  const [v,r] = VERSES[verseIdx];\n  $('verseTag').textContent = (manualMode && manualText.trim()) ? '🙏 기도제목 카드' : ('🍀 오늘의 말씀: ' + r);",
"  $('verseTag').textContent = (manualMode && manualText.trim()) ? '💌 메시지 카드' : ('🍀 오늘의 행운지수 ' + fortune.score + '점');",
1, "verseTag")

# 10) captureFrame / camInput: verseIdx roll → fortune roll
must("  effectSeed = (Math.random()*1e9)|0;   // 새 사진 → 새 효과 배치 (탭 간에는 동일)\n  verseIdx = Math.floor(Math.random()*VERSES.length);",
     "  effectSeed = (Math.random()*1e9)|0;   // 새 사진 → 새 효과 배치 (탭 간에는 동일)\n  fortune = rollFortune();",
     1, "captureFrame roll")
must("  effectSeed = (Math.random()*1e9)|0;\n  verseIdx = Math.floor(Math.random()*VERSES.length);",
     "  effectSeed = (Math.random()*1e9)|0;\n  fortune = rollFortune();",
     1, "camInput roll")

# 11) rerollVerse
must("  verseIdx = (verseIdx + 1 + Math.floor(Math.random()*(VERSES.length-1))) % VERSES.length;",
     "  fortune = rollFortune();",
     1, "reroll")

# 11b) noPhotoBtn: 사진 없이 카드 — verseIdx roll → fortune roll
must("  photoBitmap = null;\n  verseIdx = Math.floor(Math.random()*VERSES.length);",
     "  photoBitmap = null;\n  fortune = rollFortune();",
     1, "noPhoto roll")
# 11c) noPhotoBtn 라벨
must("✍️ 사진 없이 말씀 카드만 만들기", "✍️ 사진 없이 응원 카드만 만들기", 1, "noPhoto label")

# 12) saveToGallery ref
must(
'''    const [v, ref] = VERSES[verseIdx];
    const d = new Date();
    await galAdd({
      site: cfg.church,
      name: $('elderName').value.trim(),
      ref, verse: v,''',
'''    const f = fortune;
    const d = new Date();
    await galAdd({
      site: cfg.church,
      name: $('elderName').value.trim(),
      ref: '행운 '+f.score, verse: f.oneLiner,''',
1, "saveToGallery")

# 13) testPrint 텍스트
must("  x.fillText('온마음 테스트 인쇄 ✓', W/2, 55);",
     "  x.fillText('굿모닝라이언 테스트 ✓', W/2, 55);",
     1, "testPrint text")

# ---- 브랜딩 ----
must("<title>온마음 · 말씀 사진관</title>",
     "<title>굿모닝라이언 · 행운 사진관 🦁</title>", 1, "title")
must("    --sea:#1E6E68; --sea-deep:#0F4844;",
     "    --sea:#D08A1E; --sea-deep:#9A5E10;", 1, "sea")
must("    --persimmon:#C96A3B; --persimmon-deep:#A84F26;",
     "    --persimmon:#E4643A; --persimmon-deep:#B8461F;", 1, "persimmon")
must("background:radial-gradient(circle at 35% 25%, #2A8F88, var(--sea-deep));color:#fff;",
     "background:radial-gradient(circle at 35% 25%, #E7A63A, var(--sea-deep));color:#fff;", 1, "big-shoot")
must('    <div class="brand">온마음 <small>말씀 사진관</small></div>',
     '    <div class="brand">🦁 굿모닝라이언 <small>행운 사진관</small></div>', 1, "brand")
must('교회에 오신 날, 사진과 말씀을 한 장에 — 평해감리교회 <span',
     '출근길, 사진 한 장에 오늘의 행운과 응원을 담아 — 즉석 인쇄 <span', 1, "sub")
must('placeholder="예) 박종배 형제님, 박하늘 자매님"',
     'placeholder="예) 배짱"', 1, "placeholder")
must("🍀 다른 말씀 뽑기", "🍀 다른 행운 뽑기", 1, "reroll label")

# 내용 모드 UI 라벨/플레이스홀더 + 내부 주석
must('data-mode="random">🍀 말씀 (랜덤)', 'data-mode="random">🍀 행운 (랜덤)', 1, "mode chip random")
must('data-mode="manual">🙏 기도제목 직접', 'data-mode="manual">💌 메시지 직접', 1, "mode chip manual")
must('placeholder="함께 기도할 제목을 적어주세요 (예: 건강, 가정의 평화)"',
     'placeholder="적고 싶은 메시지를 적어주세요 (나에게, 또는 누군가에게)"', 1, "manual placeholder")
must("let manualMode = false;      // 내용: false=랜덤 말씀 / true=직접 기도제목",
     "let manualMode = false;      // 내용: false=랜덤 행운 / true=직접 메시지", 1, "manualMode comment")
must("let manualText = '';         // 직접 적은 기도제목",
     "let manualText = '';         // 직접 적은 메시지", 1, "manualText comment")
must("/* 내용 모드: 랜덤 말씀 ↔ 직접 기도제목 */",
     "/* 내용 모드: 랜덤 행운 ↔ 직접 메시지 */", 1, "content mode comment")

# 폴란: lion 사용자 노출 문자열/주석 정리
must("/* ================= 축복 말씀 풀 ================= */",
     "/* ================= 응원·행운 문구 풀 ================= */", 1, "verse pool comment")
must("/* ✍️ 사진 없이 카드만: 촬영이 부담스러운 어르신용 — 말씀+이름만 */",
     "/* ✍️ 사진 없이 카드만: 촬영이 부담스러운 분용 — 응원+이름만 */", 1, "noPhoto comment")
must("/* 테스트 인쇄: 성함 없이 말씀만 있는 작은 카드 */",
     "/* 테스트 인쇄: 성함 없이 문구만 있는 작은 카드 */", 1, "testPrint comment")
g = g.replace("'말씀사진'", "'행운사진'")   # 다운로드 파일명 fallback (2곳)

# church/footer 기본값 + onchange fallback (여러 곳)
g = g.replace("'평해감리교회'", "'라이크라이언'")
g = g.replace("'온마음 · 예수님이 사랑하십니다'", "'🦁 오늘도 굿모닝, 좋은 하루'")

# 잔여 VERSES 참조 없어야 함
leftover = g.count("VERSES") + g.count("verseIdx")
assert leftover == 0, f"leftover VERSES/verseIdx refs: {leftover}"

open(OUT, "w", encoding="utf-8").write(g)
print("OK ->", OUT, len(g), "bytes")
