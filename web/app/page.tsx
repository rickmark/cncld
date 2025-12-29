'use client'

import { useState } from 'react'
import ApiDisplay from './components/ApiDisplay'

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('')

  return (
    <main className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">
          Is{' '}
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-transparent border-0 border-b-2 border-white placeholder-white text-3xl font-bold text-center w-48 focus:outline-none"
          />{' '}
          cncld?
        </h1>
        <ApiDisplay term={searchTerm} />
      </div>
    </main>
  )
}
