import Head from 'next/head';
import Link from 'next/link';

export default function Home() {
  return (
    <>
      <Head>
        <title>Willis 안면 계측</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#e0e6ef] to-[#f8fafc]">
        <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-xl px-8 py-12 flex flex-col items-center">
          <h1 className="text-4xl font-bold mb-8 text-center text-gray-900 drop-shadow-lg">
            Willis 안면 계측
          </h1>
          <div className="flex flex-col gap-4 w-full max-w-xs">
            <Link href="/analyze" legacyBehavior>
              <a className="rounded-xl bg-black/80 text-white py-4 text-lg font-semibold hover:bg-black/90 transition text-center">사진 분석</a>
            </Link>
            <Link href="/camera" legacyBehavior>
              <a className="rounded-xl bg-white/80 text-black py-4 text-lg font-semibold border border-gray-300 hover:bg-gray-100 transition text-center">실시간 카메라</a>
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
