import type { NextApiRequest, NextApiResponse } from 'next';
import { calculateWillisRatio, isWillisNormal, ImageSize } from '@facemap/core';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { landmarks, imageSize } = req.body;

  if (!landmarks) {
    return res.status(400).json({ error: 'No landmarks provided' });
  }

  // 필수 랜드마크 검증
  const required = ['pupil', 'subnasale', 'rimaOris', 'chin'];
  for (const key of required) {
    if (!landmarks[key] || !Array.isArray(landmarks[key]) || landmarks[key].length !== 2) {
      return res.status(400).json({ error: `Invalid landmark: ${key}` });
    }
  }

  // imageSize가 없으면 기본값 사용 (aspect ratio 1:1)
  const size: ImageSize | undefined = imageSize?.width && imageSize?.height
    ? { width: imageSize.width, height: imageSize.height }
    : undefined;

  const ratio = calculateWillisRatio(landmarks, size);
  const normal = isWillisNormal(ratio);

  res.status(200).json({
    result: normal ? 'normal' : 'abnormal',
    ratio: Math.round(ratio * 1000) / 1000  // 소수점 3자리
  });
}
