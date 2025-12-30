'use client'

import { useState, useEffect, useRef } from 'react'
import CancelCard from "@/app/components/CancelCard";

interface ApiDisplayProps {
  term: string
}

export default function ApiDisplay({ term }: ApiDisplayProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    if (term) {
      debounceRef.current = setTimeout(() => {
        setLoading(true)
        setError('')
        fetch(`/api/lgbt/list/${encodeURIComponent(term)}`)
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}, message: ${response.statusText}`)
            }
            return response.json()
          })
          .then(data => {
            if (data.docs) {
              setData(data.docs)
            } else if (data.results) {
              setData(data.results)
            } else if (data.message) {
              setData([data.message])
            } else {
              setData([])
            }
            setLoading(false)
          })
          .catch(err => {
            setError(err.message)
            setLoading(false)
          })
      }, 500) // 500ms debounce
    } else {
      setData([])
      setLoading(false)
      setError('')
    }

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [term])

  if (!term) return null
  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      {data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mx-4">
          {data.map((doc, index) => (
            <CancelCard key={index} title={doc.title} canceled={doc.canceled} rationale={doc.rationale} penance={doc.penance} />
          ))}
        </div>
      ) : (
        <div>
          <p className="text-xl">No results found</p>
          <p className="mx-4">Enter the name of a celebrity to check their canceled status.</p>
        </div>
      )}
    </div>
  )
}