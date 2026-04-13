import { useParams, useNavigate } from 'react-router-dom'
import ProblemDetail from '../components/problem/ProblemDetail'
import { ArrowLeft } from 'lucide-react'

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Back button */}
      <div className="border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <button
            onClick={() => navigate('/')}
            className="btn-ghost flex items-center gap-2 hover:scale-105 active:scale-95"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Назад к списку</span>
          </button>
        </div>
      </div>

      {/* Problem Detail */}
      <ProblemDetail problemId={Number(id)} />
    </div>
  )
}
