import type { NextApiRequest, NextApiResponse } from 'next';

// 얼굴 분석 API (예시)
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  // TODO: 이미지 데이터 받아서 분석 (mediapipe, core 로직 활용)
  // 임시 응답
  res.status(200).json({ result: 'normal', ratio: 0.95 });
}
