// api/generate.js — Vercel 서버리스 함수
// API 키는 Vercel 환경변수(ANTHROPIC_API_KEY)에만 존재하고,
// 팀원들의 브라우저에는 절대 노출되지 않습니다.

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST만 허용됩니다.' });
  }

  // (선택) 팀 코드 검증 — Vercel에 TEAM_CODE 환경변수를 설정한 경우에만 작동
  const teamCode = process.env.TEAM_CODE;
  if (teamCode && req.headers['x-team-code'] !== teamCode) {
    return res.status(401).json({ error: '팀 코드가 올바르지 않아요. ⚙ 설정에서 팀 코드를 확인해 주세요.' });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: '서버에 API 키가 설정되지 않았어요. Vercel 환경변수 ANTHROPIC_API_KEY를 확인해 주세요.' });
  }

  try {
    const { messages } = req.body || {};
    if (!Array.isArray(messages)) {
      return res.status(400).json({ error: '잘못된 요청 형식입니다.' });
    }

    // 모델과 토큰 한도는 서버에서 강제 — 외부인이 남용해도 비용 폭탄 방지
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-opus-4-8',
        max_tokens: 1200,
        messages,
      }),
    });

    const data = await r.json();
    return res.status(r.status).json(data);
  } catch (e) {
    return res.status(500).json({ error: '생성 중 오류: ' + String(e) });
  }
}
