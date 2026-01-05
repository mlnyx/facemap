// 얼굴 계측 관련 핵심 로직 (Willis 비율 계산 등)

// MediaPipe Face Mesh 랜드마크 인덱스 (정확한 해부학적 위치)
export const LANDMARK_INDICES = {
  // 홍채 중심 (refineLandmarks: true 필요)
  LEFT_IRIS: 468,
  RIGHT_IRIS: 473,
  // 비저부 (subnasale) - 코 밑 중앙
  SUBNASALE: 94,
  // 구열 (rima oris) - 상순/하순 중앙
  UPPER_LIP: 13,
  LOWER_LIP: 14,
  // 턱끝 (gnathion)
  CHIN: 152,
} as const;

// 이미지 크기 정보 (aspect ratio 보정용)
export interface ImageSize {
  width: number;
  height: number;
}

export function calculateWillisRatio(
  landmarks: {
    pupil: [number, number],
    subnasale: [number, number],
    rimaOris: [number, number],
    chin: [number, number],
  },
  imageSize?: ImageSize
): number {
  // aspect ratio 보정을 위한 스케일 팩터
  // MediaPipe 정규화 좌표(0~1)를 실제 픽셀 비율로 변환
  const scaleX = imageSize?.width ?? 1;
  const scaleY = imageSize?.height ?? 1;

  // 실제 픽셀 거리 계산 (aspect ratio 반영)
  const dist = (a: [number, number], b: [number, number]) => {
    const dx = (a[0] - b[0]) * scaleX;
    const dy = (a[1] - b[1]) * scaleY;
    return Math.hypot(dx, dy);
  };

  // 동공~구열 거리, 비저부~턱끝 거리 계산
  const pupilToRima = dist(landmarks.pupil, landmarks.rimaOris);
  const subnasaleToChin = dist(landmarks.subnasale, landmarks.chin);

  // 0으로 나누기 방지
  if (pupilToRima === 0) return 0;

  return subnasaleToChin / pupilToRima;
}

// Willis 비율 정상 범위 상수
export const WILLIS_NORMAL_MIN = 0.85;  // 하한선 (여유있게 조정)
export const WILLIS_NORMAL_MAX = 1.15;  // 상한선

export function isWillisNormal(ratio: number): boolean {
  // 논문 기준 정상 범위: 0.85 ~ 1.15 (약 1:1 비율 기준 ±15%)
  return ratio >= WILLIS_NORMAL_MIN && ratio <= WILLIS_NORMAL_MAX;
}

// 랜드마크에서 중간점 계산 유틸리티
export function getMidpoint(
  p1: { x: number; y: number },
  p2: { x: number; y: number }
): [number, number] {
  return [(p1.x + p2.x) / 2, (p1.y + p2.y) / 2];
}
