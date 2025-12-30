import {useState} from "react";
import CancelCard from "@/app/components/CancelCard";

interface CancelResult {
    title: string,
    canceled: boolean,
    rationale: string,
    penance: string | null
}

export default function RandomCancel() {
    const [data, setData] = useState<CancelResult | null>(null);
    if (!data) {
        fetch(`/api/lgbt/random/cancel`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}, message: ${response.statusText}`)
                }
                return response.json()
            })
            .then(data =>
                setData(data.result)
            )
    }

    return data ? <div>
        <CancelCard title={data.title} canceled={data.canceled} rationale={data.rationale} penance={data.penance} />
    </div> : null;
}