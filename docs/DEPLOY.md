# Vercel/Netlify 배포 가이드

1. 루트(이 폴더)에서 `yarn install`로 의존성 설치
2. `apps/web` 폴더를 배포 대상(root)으로 지정
3. 빌드 명령: `yarn build`
4. 시작 명령: `yarn start`

- Vercel: 프로젝트 import → root를 `apps/web`으로 지정
- Netlify: base directory를 `apps/web`, build command `yarn build`, publish directory `.next`

환경 변수, SSR, API 라우트 모두 지원

---

## 모바일/반응형 최적화
- Tailwind 기반, 모든 주요 뷰포트에서 자연스럽게 동작
- 버튼/입력/이미지/카메라 UI 모두 모바일 터치 대응

## 유지보수/확장성
- 모노레포 구조, core/ui/web 분리
- mediapipe, API, 핵심 로직 모두 별도 관리
- 타입스크립트 기반, 타입 안전성 보장

---

## 문의/피드백
- GitHub 이슈 또는 직접 연락
