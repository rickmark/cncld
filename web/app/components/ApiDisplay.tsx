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
        fetch(`/api/list/lgbt/${encodeURIComponent(term)}`)
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
            <div key={doc.page_id || index} className={`border-2 rounded-lg shadow-md ${doc.canceled == true ? 'border-red-500' : 'border-green-600'}`}>
              <div className={`p-4 rounded-t-sm ${doc.canceled == true ? 'bg-red-500 text-white' : 'bg-green-600 text-white'}`}>
                <h3 className="text-3xl font-bold">{doc.title || 'Unknown'}</h3>
              </div>
              <div className="bg-black text-white p-4 rounded-b-lg">
                <div className="flex flex-col">
                  <p className="text-2xl font-bold text-center">{doc.canceled ? 'Cancelled' : 'Not Cancelled'}</p>
                  <br />
                  <p className="mb-1 text-left">{doc.rationale || 'N/A'}</p>
                  {doc.revokable && doc.penance && (
                    <div>
                      <hr className="my-2" />
                      <p className="mb-1 text-left"><strong>Path to Redemption:</strong> {doc.penance}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div>
          <p className="text-xl">No results found</p>
          <p className="mx-4">Enter the name of a celebrity to check their cancled status.</p>
        </div>
      )}
    </div>
  )
}