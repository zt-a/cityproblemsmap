import { useParams } from 'react-router-dom'
import ProblemDetail from '../components/problem/ProblemDetail'

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Problem Detail */}
      <ProblemDetail problemId={Number(id)} />
    </div>
  )
}
