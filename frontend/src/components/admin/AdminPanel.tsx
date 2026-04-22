import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AdminService, ModeratorService, ReportsService } from '../../api/generated'
import { Users, FileText, Shield, Ban, UserCheck, Search, Flag, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'sonner'
import { Link } from 'react-router-dom'
import type { UserRole, UserStatus, ProblemStatus } from '../../api/generated'

export default function AdminPanel() {
  const queryClient = useQueryClient()
  const [activeSection, setActiveSection] = useState<'users' | 'problems' | 'stats' | 'reports'>('stats')
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('')
  const [statusFilter, setStatusFilter] = useState<UserStatus | ''>('')
  const [problemStatusFilter, setProblemStatusFilter] = useState<ProblemStatus | ''>('pending' as ProblemStatus)

  const { data: stats } = useQuery({
    queryKey: ['system-stats'],
    queryFn: () => AdminService.getSystemStatsApiV1AdminStatsGet(),
  })

  const { data: users, isLoading: loadingUsers } = useQuery({
    queryKey: ['admin-users', searchQuery, roleFilter, statusFilter],
    queryFn: () =>
      AdminService.listUsersApiV1AdminUsersGet(
        roleFilter || undefined,
        statusFilter || undefined,
        undefined,
        searchQuery || undefined
      ),
    enabled: activeSection === 'users',
  })

  const { data: problems, isLoading: loadingProblems } = useQuery({
    queryKey: ['admin-problems', problemStatusFilter],
    queryFn: () =>
      AdminService.listProblemsAdminApiV1AdminProblemsGet(
        (problemStatusFilter as ProblemStatus) || undefined
      ),
    enabled: activeSection === 'problems',
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

  const changeRoleMutation = useMutation({
    mutationFn: ({ entityId, role }: { entityId: number; role: UserRole }) =>
      AdminService.changeUserRoleApiV1AdminUsersEntityIdRolePatch(entityId, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('User role updated successfully')
    },
    onError: () => toast.error('Failed to update user role'),
  })

  const suspendUserMutation = useMutation({
    mutationFn: ({ entityId, reason }: { entityId: number; reason: string }) =>
      AdminService.suspendUserApiV1AdminUsersEntityIdSuspendPatch(entityId, { reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('User suspended successfully')
    },
    onError: () => toast.error('Failed to suspend user'),
  })

  const unsuspendUserMutation = useMutation({
    mutationFn: (entityId: number) =>
      AdminService.unsuspendUserApiV1AdminUsersEntityIdUnsuspendPatch(entityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('User unsuspended successfully')
    },
    onError: () => toast.error('Failed to unsuspend user'),
  })

  const approveProblemMutation = useMutation({
    mutationFn: (entityId: number) =>
      ModeratorService.verifyProblemApiV1ModeratorProblemsEntityIdVerifyPost(entityId, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-problems'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('Problem approved successfully')
    },
    onError: () => toast.error('Failed to approve problem'),
  })

  const rejectProblemMutation = useMutation({
    mutationFn: ({ entityId, reason }: { entityId: number; reason: string }) =>
      AdminService.rejectProblemApiV1AdminProblemsEntityIdRejectPatch(entityId, { reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-problems'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('Problem rejected successfully')
    },
    onError: () => toast.error('Failed to reject problem'),
  })

  const restoreProblemMutation = useMutation({
    mutationFn: (entityId: number) =>
      AdminService.restoreProblemApiV1AdminProblemsEntityIdRestorePatch(entityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-problems'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('Problem restored successfully')
    },
    onError: () => toast.error('Failed to restore problem'),
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ entityId, status, resolutionNote }: { entityId: number; status: ProblemStatus; resolutionNote?: string }) =>
      AdminService.updateProblemStatusAdminApiV1AdminProblemsEntityIdStatusPatch(entityId, {
        status,
        resolution_note: resolutionNote,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-problems'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('Problem status updated successfully')
    },
    onError: (error: any) => toast.error(error?.body?.detail || 'Failed to update problem status'),
  })

  const approveProblemByAdminMutation = useMutation({
    mutationFn: (entityId: number) =>
      AdminService.approveProblemApiV1AdminProblemsEntityIdApprovePatch(entityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-problems'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
      toast.success('Problem approved by admin successfully')
    },
    onError: (error: any) => toast.error(error?.body?.detail || 'Failed to approve problem'),
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

  const PROBLEM_STATUSES: Array<{ value: ProblemStatus | ''; label: string }> = [
    { value: '', label: 'All' },
    { value: 'pending' as ProblemStatus, label: 'Pending' },
    { value: 'open' as ProblemStatus, label: 'Open' },
    { value: 'in_progress' as ProblemStatus, label: 'In Progress' },
    { value: 'solved' as ProblemStatus, label: 'Solved' },
    { value: 'rejected' as ProblemStatus, label: 'Rejected' },
  ]

  return (
    <div className="space-y-6">
      {/* Section Tabs */}
      <div className="flex gap-2 border-b border-border">
        {(['stats', 'users', 'problems', 'reports'] as const).map(section => (
          <button
            key={section}
            onClick={() => setActiveSection(section)}
            className={`px-4 py-2 font-medium border-b-2 -mb-px transition-colors capitalize ${
              activeSection === section
                ? 'border-primary text-primary'
                : 'border-transparent text-text-muted hover:text-text-primary'
            }`}
          >
            {section === 'reports' ? (
              <>
                <Flag className="w-4 h-4 inline mr-1" />
                Reports ({reportsStats?.pending_count || 0})
              </>
            ) : section === 'stats' ? 'System Stats'
              : section === 'users' ? 'User Management'
              : 'Problem Management'}
          </button>
        ))}
      </div>

      <div>
        {/* STATS */}
        {activeSection === 'stats' && stats && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Total Users" value={stats.total_users} icon={Users} color="text-blue-500" />
              <StatCard label="Active Users" value={stats.active_users} icon={UserCheck} color="text-green-500" />
              <StatCard label="Suspended Users" value={stats.suspended_users} icon={Ban} color="text-red-500" />
              <StatCard label="Cities Covered" value={stats.cities_covered} icon={Shield} color="text-purple-500" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Total Problems" value={stats.total_problems} icon={FileText} color="text-blue-500" />
              <StatCard label="Open Problems" value={stats.open_problems} icon={FileText} color="text-yellow-500" />
              <StatCard label="Solved Problems" value={stats.solved_problems} icon={FileText} color="text-green-500" />
              <StatCard label="Rejected Problems" value={stats.rejected_problems} icon={FileText} color="text-red-500" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard label="Total Votes" value={stats.total_votes} icon={Shield} color="text-indigo-500" />
              <StatCard label="Total Comments" value={stats.total_comments} icon={Shield} color="text-pink-500" />
              <StatCard label="Total Media" value={stats.total_media} icon={Shield} color="text-orange-500" />
            </div>
          </div>
        )}

        {/* USERS */}
        {activeSection === 'users' && (
          <div className="space-y-4">
            <div className="flex gap-4 items-center">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  type="text"
                  placeholder="Search by username or email..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-dark-input text-text-primary border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary placeholder:text-text-muted"
                />
              </div>
              <select
                value={roleFilter}
                onChange={e => setRoleFilter(e.target.value as UserRole | '')}
                className="px-4 py-2 bg-dark-input text-text-primary border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary [&>option]:bg-dark-card"
              >
                <option value="">All Roles</option>
                <option value="user">User</option>
                <option value="volunteer">Volunteer</option>
                <option value="moderator">Moderator</option>
                <option value="official">Official</option>
                <option value="admin">Admin</option>
              </select>
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value as UserStatus | '')}
                className="px-4 py-2 bg-dark-input text-text-primary border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary [&>option]:bg-dark-card"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>

            {loadingUsers ? (
              <div className="text-center py-8 text-text-muted">Loading...</div>
            ) : users?.items.length === 0 ? (
              <div className="text-center py-8 text-text-muted">No users found</div>
            ) : (
              <div className="space-y-3">
                {users?.items.map(user => (
                  <div key={user.entity_id} className="bg-dark-card border border-border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Link to={`/users/${user.entity_id}`} className="text-lg font-semibold hover:text-primary">
                            {user.username}
                          </Link>
                          <span className={`text-xs px-2 py-1 rounded ${getRoleBadgeColor(user.role)}`}>
                            {user.role}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded ${getStatusBadgeColor(user.status)}`}>
                            {user.status}
                          </span>
                        </div>
                        <p className="text-sm text-text-muted">
                          {user.email} • Reputation: {user.reputation_score}
                        </p>
                        <p className="text-xs text-text-muted mt-1">
                          Joined: {new Date(user.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <select
                          value={user.role}
                          onChange={e => {
                            if (confirm(`Change role to ${e.target.value}?`)) {
                              changeRoleMutation.mutate({ entityId: user.entity_id, role: e.target.value as UserRole })
                            }
                          }}
                          disabled={changeRoleMutation.isPending}
                          className="px-3 py-1.5 text-sm bg-dark-input text-text-primary border border-border rounded disabled:opacity-50 [&>option]:bg-dark-card"
                        >
                          <option value="user">User</option>
                          <option value="volunteer">Volunteer</option>
                          <option value="moderator">Moderator</option>
                          <option value="official">Official</option>
                          <option value="admin">Admin</option>
                        </select>
                        {user.status === 'active' ? (
                          <button
                            onClick={() => {
                              const reason = prompt('Reason for suspension:')
                              if (reason) suspendUserMutation.mutate({ entityId: user.entity_id, reason })
                            }}
                            disabled={suspendUserMutation.isPending}
                            className="px-3 py-1.5 text-sm bg-red-500 hover:bg-red-600 text-white rounded disabled:opacity-50"
                          >
                            <Ban className="w-4 h-4 inline mr-1" />
                            Suspend
                          </button>
                        ) : (
                          <button
                            onClick={() => unsuspendUserMutation.mutate(user.entity_id)}
                            disabled={unsuspendUserMutation.isPending}
                            className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                          >
                            <UserCheck className="w-4 h-4 inline mr-1" />
                            Unsuspend
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* PROBLEMS */}
        {activeSection === 'problems' && (
          <div className="space-y-4">
            {/* Status filter */}
            <div className="flex gap-2 flex-wrap">
              {PROBLEM_STATUSES.map(({ value, label }) => (
                <button
                  key={label}
                  onClick={() => setProblemStatusFilter(value)}
                  className={`px-3 py-1.5 text-sm rounded transition-colors ${
                    problemStatusFilter === value
                      ? 'bg-primary text-white'
                      : 'bg-dark-input text-text-muted hover:text-text-primary'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {loadingProblems ? (
              <div className="text-center py-8 text-text-muted">Loading...</div>
            ) : problems?.items.length === 0 ? (
              <div className="text-center py-8 text-text-muted">No problems found</div>
            ) : (
              <div className="space-y-3">
                {problems?.items.map(problem => (
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
                      <span className={`text-xs px-2 py-1 rounded ${getStatusBadgeColor(problem.status)}`}>
                        {problem.status}
                      </span>
                    </div>

                    <p className="text-sm text-text-muted mb-3 line-clamp-2">{problem.description}</p>

                    <div className="flex gap-2 items-center">
                      <select
                        value={problem.status}
                        onChange={e => {
                          const newStatus = e.target.value as ProblemStatus
                          const note = prompt('Resolution note (optional):')
                          if (newStatus !== problem.status) {
                            updateStatusMutation.mutate({
                              entityId: problem.entity_id,
                              status: newStatus,
                              resolutionNote: note || undefined,
                            })
                          }
                        }}
                        disabled={updateStatusMutation.isPending}
                        className="px-3 py-1.5 text-sm bg-dark-input text-text-primary border border-border rounded disabled:opacity-50 [&>option]:bg-dark-card"
                      >
                        <option value="pending">Pending</option>
                        <option value="open">Open</option>
                        <option value="in_progress">In Progress</option>
                        <option value="solved">Solved</option>
                        <option value="rejected">Rejected</option>
                        <option value="archived">Archived</option>
                      </select>
                      {problem.status === 'pending' && (
                        <button
                          onClick={() => approveProblemByAdminMutation.mutate(problem.entity_id)}
                          disabled={approveProblemByAdminMutation.isPending}
                          className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                        >
                          <CheckCircle className="w-4 h-4 inline mr-1" />
                          Approve
                        </button>
                      )}
                      {problem.status === 'rejected' ? (
                        <button
                          onClick={() => restoreProblemMutation.mutate(problem.entity_id)}
                          disabled={restoreProblemMutation.isPending}
                          className="px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded disabled:opacity-50"
                        >
                          Restore
                        </button>
                      ) : (
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
                      )}
                      <Link
                        to={`/problems/${problem.entity_id}`}
                        className="px-3 py-1.5 text-sm bg-dark-input hover:bg-border text-text-primary rounded transition-colors"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
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
                    <div className="flex items-start justify-between mb-3">
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
                          <p className="text-sm text-text-muted mt-1">{report.description}</p>
                        )}
                        <p className="text-xs text-text-muted mt-2">
                          Reported: {new Date(report.created_at).toLocaleString()}
                        </p>
                      </div>
                      <Link
                        to={
                          report.target_type === 'problem'
                            ? `/problems/${report.target_entity_id}`
                            : report.target_type === 'user'
                            ? `/users/${report.target_entity_id}`
                            : report.target_type === 'comment'
                            ? `/problems/${(report as any).problem_entity_id || report.target_entity_id}#comment-${report.target_entity_id}`
                            : `/problems/${report.target_entity_id}`
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

function getRoleBadgeColor(role: string) {
  switch (role) {
    case 'admin': return 'bg-red-500/10 text-red-500'
    case 'moderator': return 'bg-purple-500/10 text-purple-500'
    case 'official': return 'bg-blue-500/10 text-blue-500'
    case 'volunteer': return 'bg-green-500/10 text-green-500'
    default: return 'bg-gray-500/10 text-gray-500'
  }
}

function getStatusBadgeColor(status: string) {
  switch (status) {
    case 'active':
    case 'open':
    case 'in_progress': return 'bg-green-500/10 text-green-500'
    case 'suspended':
    case 'rejected': return 'bg-red-500/10 text-red-500'
    case 'solved':
    case 'resolved': return 'bg-blue-500/10 text-blue-500'
    case 'pending': return 'bg-yellow-500/10 text-yellow-500'
    default: return 'bg-gray-500/10 text-gray-500'
  }
}