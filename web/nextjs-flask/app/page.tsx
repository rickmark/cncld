import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">Hello from Next.js</h1>
        <p className="mb-2">This is the Next root page.</p>
        <p>
          <Link href="/api/python" className="text-blue-600 underline">
            Call the Flask API
          </Link>
        </p>
      </div>
    </main>
  )
}
