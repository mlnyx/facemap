import { useRef, useState } from 'react';
import { FaceMesh } from '@mediapipe/face_mesh';
import { LANDMARK_INDICES, getMidpoint } from '@facemap/core';

export default function Analyze() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [ratio, setRatio] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Mediapipe 얼굴 분석 및 API 호출
  const analyzeImage = async (img: HTMLImageElement) => {
    setLoading(true);
    setResult(null);
    setRatio(null);
    setError(null);
    try {
      const faceMesh = new FaceMesh({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
      });
      await faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7,
      });
      const results = await new Promise<any>((resolve, reject) => {
        faceMesh.onResults(resolve);
        faceMesh.send({ image: img });
      });
      if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
        setError('얼굴을 인식하지 못했습니다. 정면 사진을 올려주세요.');
        setLoading(false);
        return;
      }

      const lm = results.multiFaceLandmarks[0];

      // 양쪽 동공의 중간점 계산 (기울어진 얼굴 보정)
      const pupil = getMidpoint(
        lm[LANDMARK_INDICES.LEFT_IRIS],
        lm[LANDMARK_INDICES.RIGHT_IRIS]
      );

      // 비저부 (코 밑 중앙) - 정확한 인덱스 사용
      const subnasale: [number, number] = [
        lm[LANDMARK_INDICES.SUBNASALE].x,
        lm[LANDMARK_INDICES.SUBNASALE].y
      ];

      // 구열 (상순과 하순의 중간점)
      const rimaOris = getMidpoint(
        lm[LANDMARK_INDICES.UPPER_LIP],
        lm[LANDMARK_INDICES.LOWER_LIP]
      );

      // 턱끝
      const chin: [number, number] = [
        lm[LANDMARK_INDICES.CHIN].x,
        lm[LANDMARK_INDICES.CHIN].y
      ];

      const landmarks = { pupil, subnasale, rimaOris, chin };

      // 이미지 크기 정보 (aspect ratio 보정용)
      const imageSize = { width: img.naturalWidth, height: img.naturalHeight };

      // API 호출
      const apiRes = await fetch('/api/analyze-willis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ landmarks, imageSize }),
      });
      const apiJson = await apiRes.json();
      if (apiJson.error) {
        setError(apiJson.error);
      } else {
        setRatio(apiJson.ratio);
        setResult(apiJson.result === 'normal' ? '정상 얼굴 비율입니다.' : '비정상 얼굴 비율입니다.');
      }
    } catch (e) {
      setError('분석 중 오류가 발생했습니다.');
    }
    setLoading(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('이미지 파일만 업로드 가능합니다.');
      return;
    }
    setError(null);
    const url = URL.createObjectURL(file);
    setImageUrl(url);
    setResult(null);
    setTimeout(() => {
      const img = new window.Image();
      img.src = url;
      img.onload = () => analyzeImage(img);
    }, 100);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#e0e6ef] to-[#f8fafc]">
      <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-xl px-8 py-12 flex flex-col items-center w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-900">사진 분석</h2>
        <input
          type="file"
          accept="image/png, image/jpeg"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="mb-4"
        />
        {error && <div className="text-red-500 mb-2">{error}</div>}
        {imageUrl && (
          <img src={imageUrl} alt="업로드 이미지" className="rounded-xl mb-4 max-h-64 object-contain" />
        )}
        {loading && <div className="text-blue-500 mb-2">분석 중...</div>}
        {result && (
          <div className="mt-4 text-center">
            <div className="text-lg font-semibold">{result}</div>
            {ratio !== null && (
              <div className="text-sm text-gray-600 mt-1">
                Willis 비율: {ratio.toFixed(3)} (정상 범위: 0.85 ~ 1.15)
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
