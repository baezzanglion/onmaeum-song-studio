# tools/ — 굿모닝라이언 생성기

## 무엇인가
`build_lion.py` 는 **온마음 말씀사진관(`../print.html`)** 을 유일한 소스로 두고,
**굿모닝라이언 행운사진관(`lion.html`)** 을 자동 생성하는 변환기입니다.

두 앱은 **"같은 엔진, 다른 콘텐츠"** 입니다:

| | 온마음 (교회) | 굿모닝라이언 (회사 로비) |
|---|---|---|
| 배포 | 이 저장소 `print.html` (Vercel) | `sponge-intro/lion.html` (GitHub Pages) |
| 랜덤 콘텐츠 | 성경 말씀 100+ | 행운지수 + 응원 문구 |
| 직접 입력 | 🙏 기도제목 | 💌 메시지 |
| 색상 | teal/persimmon | gold/coral |
| 상단/하단 | 평해감리교회 / 온마음 | 라이크라이언 / 🦁 오늘도 굿모닝 |

공통 엔진(카메라·줌·디더링·블루투스 인쇄·컬러 카드·곱게·효과·**기기내 갤러리**·
사진없이 카드)은 완전히 동일하며, `print.html` 한 곳만 고치면 됩니다.

## 사용법
```bash
# 1) 온마음(print.html)을 고친다
# 2) 굿모닝라이언 생성
python3 tools/build_lion.py                 # ./print.html → ./tools/lion.generated.html
python3 tools/build_lion.py <src> <out>     # 경로 직접 지정도 가능

# 3) 생성물을 sponge-intro 로 복사해 배포
cp tools/lion.generated.html /path/to/sponge-intro/lion.html
cd /path/to/sponge-intro && git add lion.html && git commit -m "..." && git push
```

## 안전장치
모든 치환은 `must(찾을문자열, 바꿀문자열, 횟수)` 로 **"정확히 N번 매칭"을 검증**합니다.
`print.html` 이 바뀌어 앵커 문자열이 어긋나면 **조용히 깨지지 않고 즉시 AssertionError** 로
멈춥니다. 그러면 `build_lion.py` 의 해당 `must(...)` 대상 문자열을 새 `print.html` 에
맞게 고쳐주면 됩니다. 마지막에 `VERSES`/`verseIdx` 잔여 참조가 0인지도 검사합니다.

> `lion.generated.html` 은 빌드 산출물이라 커밋하지 않습니다(.gitignore).
