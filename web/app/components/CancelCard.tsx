

interface CancelCardProps {
    title: string,
    canceled: boolean,
    rationale: string,
    penance: string | null
}

export default function CancelCard({ title, canceled, rationale, penance }: CancelCardProps) {
    return (
        <div className={`border-2 m-6 rounded-lg shadow-md ${canceled ? 'border-red-500' :  (penance != null ? 'border-yellow-400' :'border-green-600')}`}>
            <div className={`p-4 rounded-t-sm text-white ${canceled ? 'bg-red-500' : (penance != null ?  'bg-yellow-400': 'bg-green-600')}`}>
                <h3 className="text-3xl font-bold">{title || 'Unknown'}</h3>
            </div>
            <div className="bg-black text-white p-4 rounded-b-lg">
                <div className="flex flex-col">
                    <p className="text-2xl font-bold text-center">{canceled ? 'Cancelled' :  (penance != null ? 'Do Better...' : 'Slay Queen!')}</p>
                    <br />
                    <p className="mb-1 text-left">{rationale || 'N/A'}</p>
                    {penance && (
                        <div>
                            <hr className="my-2" />
                            <p className="mb-1 text-left"><strong>Path to Redemption:</strong> {penance}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}