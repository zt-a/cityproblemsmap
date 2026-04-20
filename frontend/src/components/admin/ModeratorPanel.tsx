import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ModeratorService, ReportsService } from '../../api/generated'
import { AlertTriangle, MessageSquare, Eye, EyeOff, CheckCircle, XCircle, Flag } from 'lucide-react'
import { toast } from 'sonner'
import { Link } from 'react-router-dom'

export default function ModeratorPanel() {
  const queryClient = useQueryClient()
  const [activeSection, setActiveSection] = useState<'flagged' | 'suspicious' | 'pending' | 'reports'>('pending')

  const { data: stats } = useQuery({
    queryKey: ['moderator-stats'],
    queryFn: () => ModeratorService.getModeratorStatsApiV1ModeratorStatsGet(),
  })

  const { data: flaggedComments, isLoading: loadingFlagged } = useQuery({
    queryKey: ['flagged-comments'],
    queryFn: () => ModeratorService.getFlaggedCommentsApiV1ModeratorCommentsFlaggedGet(),
    enabled: activeSection === 'flagged',
  })

  const { data: suspiciousProblems, isLoading: loadingSuspicious } = useQuery({
    queryKey: ['suspicious-problems'],
    queryFn: () => ModeratorService.getSuspiciousProblemsApiV1ModeratorProblemsSuspiciousGet(),
    enabled: activeSection === 'suspicious',
  })

  const { data: pendingProblems, isLoading: loadingPending } = useQuery({
    queryKey: ['pending-problems'],
    queryFn: () => ModeratorService.getPendingProblemsApiV1ModeratorProblemsPendingGet(),
    enabled: activeSection === 'pending',
  })

  const { data: reportsQueue, isLoading: loadingReports } = useQuery({
    queryKey: ['reports-queue'],
    queryFn: () => ReportsService.getModerationQueueApiV1ReportsModerationQueueGet(),
    enabled: activeSection === 'reports',
  })

  const { data: reportsStats } = useQuery({
    queryKey: ['reports-stats'],
    queryFn: () => ReportsService.getModerationStatsApiV1ReportsModerationStatsGet(),
  })

  const hideCommentMutation = useMutation({
    mutationFn: ({ entityId, reason }: { entityId: number; reason: string }) =>
      ModeratorService.hideCommentApiV1ModeratorCommentsEntityIdHidePost(entityId, { reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flagged-comments'] })
      queryClient.invalidateQueries({ queryKey: ['moderator-stats'] })
      toast.success('Comment hidden successfully')
    },
    onError: () => toast.error('Failed to hide comment'),
  })

  const restoreCommentMutation = useMutation({
    mutationFn: (entityId: number) =>
      ModeratorService.restoreCommentApiV1ModeratorCommentsEntityIdRestorePost(entityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flagged-comments'] })
      queryClient.invalidateQueries({ queryKey: ['moderator-stats'] })
      toast.success('Comment restored successfully')
    },
    onError: () => toast.error('Failed to restore comment'),
  })

  const verifyProblemMutation = useMutation({
    mutationFn: ({ entityId, note }: { entityId: number; note?: string }) =>
      ModeratorService.verifyProblemApiV1ModeratorProblemsEntityIdVerifyPost(entityId, { note }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suspicious-problems'] })
      queryClient.invalidateQueries({ queryKey: ['pending-problems'] })
      queryClient.invalidateQueries({ queryKey: ['moderator-stats'] })
      toast.success('Problem approved successfully')
    },
    onError: () => toast.error('Failed to approve problem'),
  })

  const rejectProblemMutation = useMutation({
    mutationFn: ({ entityId, reason }: { entityId: number; reason: string }) =>
      // ModeratorService не имеет reject — используем прямой fetch или импортируем AdminService
      // Если у модератора есть доступ к /admin/problems/:id/reject через роль — используем AdminService
      fetch(`/api/v1/admin/problems/${entityId}/reject`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
        body: JSON.stringify({ reason }),
      }).then(r => { if (!r.ok) throw r; return r.json() }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-problems'] })
      queryClient.invalidateQueries({ queryKey: ['suspicious-problems'] })
      queryClient.invalidateQueries({ queryKey: ['moderator-stats'] })
      toast.success('Problem rejected successfully')
    },
    onError: () => toast.error('Failed to reject problem'),
  })

  const resolveReportMutation = useMutation({
    mutationFn: ({ entityId, status, notes }: { entityId: number; status: 'resolved' | 'rejected'; notes?: string }) =>
      ReportsService.resolveReportApiV1ReportsModerationEntityIdResolvePatch(entityId, {
        status,
        resolution_note: notes,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports-queue'] })
      queryClient.invalidateQueries({ queryKey: ['reports-stats'] })
      toast.success('Report resolved successfully')
    },
    onError: (error: any) => toast.error(error?.body?.detail || 'Failed to resolve report'),
  })

  return (
    <div className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard label="Verified" value={stats.problems_verified} icon={CheckCircle} color="text-green-500" />
          <StatCard label="Rejected" value={stats.problems_rejected} icon={XCircle} color="text-red-500" />
          <StatCard label="Hidden Comments" value={stats.comments_hidden} icon={EyeOff} color="text-orange-500" />
          <StatCard label="Suspended Users" value={stats.users_suspended} icon={AlertTriangle} color="text-yellow-500" />
          <StatCard label="Flagged Pending" value={stats.flagged_pending} icon={MessageSquare} color="text-blue-500" />
          <StatCard label="Suspicious" value={stats.suspicious_pending} icon={AlertTriangle} color="text-purple-500" />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border overflow-x-auto">
        <TabButton active={activeSection === 'pending'} onClick={() => setActiveSection('pending')}>
          Pending Problems
        </TabButton>
        <TabButton active={activeSection === 'flagged'} onClick={() => setActiveSection('flagged')}>
          Flagged Comments ({stats?.flagged_pending || 0})
        </TabButton>
        <TabButton active={activeSection === 'suspicious'} onClick={() => setActiveSection('suspicious')}>
          Suspicious ({stats?.suspicious_pending || 0})
        </TabButton>
        <TabButton active={activeSection === 'reports'} onClick={() => setActiveSection('reports')}>
          <Flag className="w-4 h-4 inline mr-1" />
          Reports ({reportsStats?.pending_count || 0})
        </TabButton>
      </div>

      <div>
        {/* PENDING PROBLEMS */}
        {activeSection === 'pending' && (
          <div className="space-y-4">
            {loadingPending ? (
              <div className="text-center py-8 text-text-muted">Loading...</div>
            ) : pendingProblems?.items.length === 0 ? (
              <div className="text-center py-8 text-text-muted">No pending problems</div>
            ) : (
              pendingProblems?.items.map(problem => (
                <div key={problem.entity_id} className="bg-dark-card border border-border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <Link to={`/problems/${problem.entity_id}`} className="text-lg font-semibold hover:text-primary text-text-primary">
                        {problem.title}
                      </Link>
                      <p className="text-sm text-text-muted mt-1">
                        by {problem.author_username} • {new Date(problem.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right text-sm">
                      <div className="text-text-primary">Truth: {(problem.truth_score * 100).toFixed(0)}%</div>
                      <div className="text-text-muted text-xs">Priority: {problem.priority_score.toFixed(2)}</div>
                    </div>
                  </div>
                  <p className="text-sm text-text-muted mb-3 line-clamp-2">{problem.description}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => verifyProblemMutation.mutate({ entityId: problem.entity_id })}
                      disabled={verifyProblemMutation.isPending}
                      className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                    >
                      <CheckCircle className="w-4 h-4 inline mr-1" />
                      Approve
                    </button>
                    <button
                      onClick={() => {
                        const reason = prompt('Reason for rejection:')
                        if (reason) rejectProblemMutation.mutate({ entityId: problem.entity_id, reason })
                      }}
                      disabled={rejectProblemMutation.isPending}
                      className="px-3 py-1.5 text-sm bg-red-500 hover:bg-red-600 text-white rounded disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4 inline mr-1" />
                      Reject
                    </button>
                    <Link
                      to={`/problems/${problem.entity_id}`}
                      className="px-3 py-1.5 text-sm bg-dark-input hover:bg-border text-text-primary rounded"
                    >
                      View
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* FLAGGED COMMENTS */}
        {activeSection === 'flagged' && (
          <div className="space-y-4">
            {loadingFlagged ? (
              <div className="text-center py-8 text-text-muted">Loading...</div>
            ) : flaggedComments?.items.length === 0 ? (
              <div className="text-center py-8 text-text-muted">No flagged comments</div>
            ) : (
              flaggedComments?.items.map(item => (
                <div key={item.comment.entity_id} className="bg-dark-card border border-border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <Link to={`/problems/${item.comment.problem_entity_id}`} className="text-sm text-primary hover:underline">
                        Problem #{item.comment.problem_entity_id}
                      </Link>
                      <p className="text-sm text-text-muted mt-1">
                        by {item.comment.author_username} • {new Date(item.comment.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className="text-red-500 font-medium text-sm">{item.flag_count} reports</span>
                  </div>
                  <div className="bg-dark-input rounded p-3 mb-3">
                    <p className="text-sm text-text-primary">{item.comment.content}</p>
                  </div>
                  {item.flag_reasons.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-3">
                      {item.flag_reasons.map((reason, idx) => (
                        <span key={idx} className="text-xs bg-red-500/10 text-red-500 px-2 py-1 rounded">
                          {reason}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        const reason = prompt('Reason for hiding:')
                        if (reason) hideCommentMutation.mutate({ entityId: item.comment.entity_id, reason })
                      }}
                      disabled={hideCommentMutation.isPending}
                      className="px-3 py-1.5 text-sm bg-red-500 hover:bg-red-600 text-white rounded disabled:opacity-50"
                    >
                      <EyeOff className="w-4 h-4 inline mr-1" />
                      Hide
                    </button>
                    <button
                      onClick={() => restoreCommentMutation.mutate(item.comment.entity_id)}
                      disabled={restoreCommentMutation.isPending}
                      className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                    >
                      <Eye className="w-4 h-4 inline mr-1" />
                      Dismiss
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* SUSPICIOUS */}
        {activeSection === 'suspicious' && (
          <div className="space-y-4">
            {loadingSuspicious ? (
              <div className="text-center py-8 text-text-muted">Loading...</div>
            ) : suspiciousProblems?.items.length === 0 ? (
              <div className="text-center py-8 text-text-muted">No suspicious problems</div>
            ) : (
              suspiciousProblems?.items.map(item => (
                <div key={item.problem.entity_id} className="bg-dark-card border border-border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <Link to={`/problems/${item.problem.entity_id}`} className="text-lg font-semibold hover:text-primary text-text-primary">
                        {item.problem.title}
                      </Link>
                      <p className="text-sm text-text-muted mt-1">
                        by {item.problem.author_username} • {new Date(item.problem.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-red-500">
                        Truth: {(item.problem.truth_score * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-text-muted">{item.reason}</div>
                    </div>
                  </div>
                  <p className="text-sm text-text-muted mb-3 line-clamp-2">{item.problem.description}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => verifyProblemMutation.mutate({ entityId: item.problem.entity_id })}
                      disabled={verifyProblemMutation.isPending}
                      className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                    >
                      <CheckCircle className="w-4 h-4 inline mr-1" />
                      Verify Valid
                    </button>
                    <Link
                      to={`/problems/${item.problem.entity_id}`}
                      className="px-3 py-1.5 text-sm bg-dark-input hover:bg-border text-text-primary rounded"
                    >
                      View
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* REPORTS */}
        {activeSection === 'reports' && (
          <div className="space-y-4">
            {loadingReports ? (
              <div className="text-center py-8 text-text-muted">Loading...</div>
            ) : reportsQueue?.items.length === 0 ? (
              <div className="text-center py-8 text-text-muted">No reports to review</div>
            ) : (
              <div className="space-y-3">
                {reportsQueue?.items.map(report => (
                  <div key={report.entity_id} className="bg-dark-card border border-border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Flag className="w-4 h-4 text-red-500" />
                          <span className="font-semibold text-text-primary">
                            {report.target_type === 'problem' && 'Problem Report'}
                            {report.target_type === 'comment' && 'Comment Report'}
                            {report.target_type === 'user' && 'User Report'}
                          </span>
                          <span className="text-xs px-2 py-1 rounded bg-yellow-500/10 text-yellow-500">
                            {report.status}
                          </span>
                        </div>
                        <p className="text-sm text-text-secondary mb-1">
                          Reason: <span className="text-text-primary font-medium">{report.reason}</span>
                        </p>
                        {report.description && (
                          <p className="text-sm text-text-muted">{report.description}</p>
                        )}
                        <p className="text-xs text-text-muted mt-2">
                          {new Date(report.created_at).toLocaleString()}
                        </p>
                      </div>
                      <Link
                        to={
                          report.target_type === 'problem'
                            ? `/problems/${report.target_entity_id}`
                            : report.target_type === 'user'
                            ? `/users/${report.target_entity_id}`
                            : `/problems/${(report as any).problem_entity_id || report.target_entity_id}#comment-${report.target_entity_id}`
                        }
                        className="text-sm text-primary hover:underline ml-4 shrink-0"
                      >
                        View Target →
                      </Link>
                    </div>

                    {report.status === 'pending' && (
                      <div className="flex gap-2 pt-3 border-t border-border">
                        <button
                          onClick={() => {
                            const notes = prompt('Resolution notes (optional):')
                            resolveReportMutation.mutate({
                              entityId: report.entity_id,
                              status: 'resolved',
                              notes: notes || undefined,
                            })
                          }}
                          disabled={resolveReportMutation.isPending}
                          className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                        >
                          <CheckCircle className="w-4 h-4 inline mr-1" />
                          Resolve
                        </button>
                        <button
                          onClick={() => {
                            const notes = prompt('Reason for rejection (optional):')
                            resolveReportMutation.mutate({
                              entityId: report.entity_id,
                              status: 'rejected',
                              notes: notes || undefined,
                            })
                          }}
                          disabled={resolveReportMutation.isPending}
                          className="px-3 py-1.5 text-sm bg-red-500 hover:bg-red-600 text-white rounded disabled:opacity-50"
                        >
                          <XCircle className="w-4 h-4 inline mr-1" />
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-medium border-b-2 -mb-px transition-colors whitespace-nowrap ${
        active ? 'border-primary text-primary' : 'border-transparent text-text-muted hover:text-text-primary'
      }`}
    >
      {children}
    </button>
  )
}

function StatCard({ label, value, icon: Icon, color }: {
  label: string; value: number; icon: any; color: string
}) {
  return (
    <div className="bg-dark-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-text-muted">{label}</span>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <div className="text-2xl font-bold text-text-primary">{value}</div>
    </div>
  )
}