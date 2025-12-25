'use client'

import { useState, useEffect, useRef } from 'react'

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
        fetch(`/api/list/${encodeURIComponent(term)}`)
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`)
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
      <h2>Search Results:</h2>
      {data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mx-4">
          {data.map((doc, index) => (
            <div key={doc.page_id || index} className="border border-gray-300 rounded-lg p-4 shadow-md">
              <h3 className="text-lg font-bold mb-2">{doc.title || 'Unknown'}</h3>
              <p className="mb-1"><strong>Cancelled:</strong> {doc.cancled ? 'Yes' : 'No'}</p>
              <p className="mb-1"><strong>Rationale:</strong> {doc.rationale || 'N/A'}</p>
              <p className="mb-1"><strong>Revokable:</strong> {doc.revokable ? 'Yes' : 'No'}</p>
              {doc.revokable && doc.penance && (
                <p className="mb-1"><strong>Penance:</strong> {doc.penance}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p>No results found.</p>
      )}
    </div>
  )
}