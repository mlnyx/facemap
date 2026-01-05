import { useRef, useEffect, useState } from 'react';
import { FaceMesh } from '@mediapipe/face_mesh';
import {
  LANDMARK_INDICES,
  getMidpoint,
  calculateWillisRatio,
  isWillisNormal,
  WILLIS_NORMAL_MIN,
  WILLIS_NORMAL_MAX
} from '@facemap/core';

export default function Camera() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [ratio, setRatio] = useState<number | null>(null);
  const [guide, setGuide] = useState<string>('얼굴을 정면에 맞춰주세요');

  useEffect(() => {
    let animationId: number;
    let faceMesh: FaceMesh | null = null;
    let stream: MediaStream | null = null;

    async function setupCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        await setupFaceMesh();
      } catch (err) {
        setError('카메라 접근에 실패했습니다.');
      }
    }

    async function setupFaceMesh() {
      faceMesh = new FaceMesh({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
      });
      await faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7,
      });
      faceMesh.onResults(onResults);
      requestAnimationFrame(processFrame);
    }

    async function processFrame() {
      if (!videoRef.current || !faceMesh) return;
      await faceMesh.send({ image: videoRef.current });
      animationId = requestAnimationFrame(processFrame);
    }

    function onResults(results: any) {
      const ctx = canvasRef.current?.getContext('2d');
      const video = videoRef.current;
      if (!ctx || !video) return;

      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

      if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        const lm = results.multiFaceLandmarks[0];

        // 얼굴 위치 가이드
        const faceCenterY = lm[168].y;
        if (faceCenterY < 0.3) setGuide('얼굴을 아래로 내리세요');
        else if (faceCenterY > 0.7) setGuide('얼굴을 위로 올리세요');
        else setGuide('정상 위치입니다');

        // 양쪽 동공의 중간점
        const pupil = getMidpoint(
          lm[LANDMARK_INDICES.LEFT_IRIS],
          lm[LANDMARK_INDICES.RIGHT_IRIS]
        );

        // 비저부 (코 밑 중앙)
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

        // 랜드마크 시각화 (양쪽 동공 + 주요 포인트)
        const pointsToDraw = [
          { pt: lm[LANDMARK_INDICES.LEFT_IRIS], color: '#10b981' },
          { pt: lm[LANDMARK_INDICES.RIGHT_IRIS], color: '#10b981' },
          { pt: { x: pupil[0], y: pupil[1] }, color: '#2563eb' },
          { pt: lm[LANDMARK_INDICES.SUBNASALE], color: '#f59e0b' },
          { pt: { x: rimaOris[0], y: rimaOris[1] }, color: '#ef4444' },
          { pt: lm[LANDMARK_INDICES.CHIN], color: '#8b5cf6' },
        ];

        pointsToDraw.forEach(({ pt, color }) => {
          ctx.beginPath();
          ctx.arc(pt.x * ctx.canvas.width, pt.y * ctx.canvas.height, 5, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();
        });

        // 실시간 Willis 비율 계산
        const landmarks = { pupil, subnasale, rimaOris, chin };
        const imageSize = { width: video.videoWidth, height: video.videoHeight };
        const willisRatio = calculateWillisRatio(landmarks, imageSize);
        const isNormal = isWillisNormal(willisRatio);

        setRatio(willisRatio);
        setResult(isNormal ? '정상 비율' : '비정상 비율');
      } else {
        setGuide('얼굴을 정면에 맞춰주세요');
        setResult(null);
        setRatio(null);
      }
    }

    setupCamera();
    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (stream) stream.getTracks().forEach(track => track.stop());
    };
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#e0e6ef] to-[#f8fafc] p-4">
      <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-xl p-4 sm:p-6 flex flex-col items-center w-full max-w-sm">
        <h2 className="text-xl sm:text-2xl font-bold mb-4 text-center text-gray-900">실시간 카메라</h2>
        {error && <div className="text-red-500 mb-2 text-sm">{error}</div>}

        {/* 비디오 컨테이너 - 4:3 비율 유지 */}
        <div className="relative w-full aspect-[4/3] mb-3 rounded-xl overflow-hidden bg-black">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="absolute inset-0 w-full h-full object-cover"
          />
          <canvas
            ref={canvasRef}
            width={320}
            height={240}
            className="absolute inset-0 w-full h-full pointer-events-none"
          />

          {/* 결과 오버레이 - 비디오 하단에 표시 */}
          <div className="absolute bottom-0 left-0 right-0 bg-black/50 backdrop-blur-sm p-2 text-center">
            <div className="text-white text-sm font-medium">{guide}</div>
            {result && (
              <div className="flex items-center justify-center gap-2 mt-1">
                <span className={`text-sm font-bold ${result === '정상 비율' ? 'text-green-400' : 'text-red-400'}`}>
                  {result}
                </span>
                {ratio !== null && (
                  <span className="text-white/80 text-xs">
                    ({ratio.toFixed(2)})
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 범례 */}
        <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-600">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500"></span> 동공
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span> 비저부
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500"></span> 구열
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-violet-500"></span> 턱끝
          </span>
        </div>
      </div>
    </main>
  );
}
