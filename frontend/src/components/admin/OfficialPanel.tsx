import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { OfficialService } from '../../api/generated'
import { Briefcase, CheckCircle, Clock, MapPin, MessageSquare } from 'lucide-react'
import { toast } from 'sonner'
import { Link } from 'react-router-dom'
import type { ProblemStatus } from '../../api/generated'

export default function OfficialPanel() {
  const queryClient = useQueryClient()
  const [activeSection, setActiveSection] = useState<'assigned' | 'in-progress' | 'zones' | 'stats'>('stats')
  const [statusFilter, setStatusFilter] = useState<ProblemStatus | ''>('')

  // Fetch official stats
  const { data: stats } = useQuery({
    queryKey: ['official-stats'],
    queryFn: () => OfficialService.getOfficialStatsApiV1OfficialStatsGet(),
  })

  // Fetch assigned problems
  const { data: assignedProblems, isLoading: loadingAssigned } = useQuery({
    queryKey: ['assigned-problems', statusFilter],
    queryFn: () =>
      OfficialService.getAssignedProblemsApiV1OfficialProblemsAssignedGet(
        statusFilter || undefined
      ),
    enabled: activeSection === 'assigned',
  })

  // Fetch in-progress problems
  const { data: inProgressProblems, isLoading: loadingInProgress } = useQuery({
    queryKey: ['in-progress-problems'],
    queryFn: () => OfficialService.getInProgressProblemsApiV1OfficialProblemsInProgressGet(),
    enabled: activeSection === 'in-progress',
  })

  // Fetch zones
  const { data: zones, isLoading: loadingZones } = useQuery({
    queryKey: ['official-zones'],
    queryFn: () => OfficialService.getOfficialZonesApiV1OfficialZonesGet(),
    enabled: activeSection === 'zones',
  })

  // Take problem mutation
  const takeProblemMutation = useMutation({
    mutationFn: ({ entityId, note }: { entityId: number; note?: string }) =>
      OfficialService.takeProblemApiV1OfficialProblemsEntityIdTakePost(entityId, { note }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assigned-problems'] })
      queryClient.invalidateQueries({ queryKey: ['in-progress-problems'] })
      queryClient.invalidateQueries({ queryKey: ['official-stats'] })
      toast.success('Problem taken successfully')
    },
    onError: () => {
      toast.error('Failed to take problem')
    },
  })

  // Resolve problem mutation
  const resolveProblemMutation = useMutation({
    mutationFn: ({ entityId, resolution_notes }: { entityId: number; resolution_notes: string }) =>
      OfficialService.resolveProblemApiV1OfficialProblemsEntityIdResolvePost(entityId, {
        resolution_notes,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assigned-problems'] })
      queryClient.invalidateQueries({ queryKey: ['in-progress-problems'] })
      queryClient.invalidateQueries({ queryKey: ['official-stats'] })
      toast.success('Problem resolved successfully')
    },
    onError: () => {
      toast.error('Failed to resolve problem')
    },
  })

  // Add official comment mutation
  const addCommentMutation = useMutation({
    mutationFn: ({ entityId, content }: { entityId: number; content: string }) =>
      OfficialService.addOfficialCommentApiV1OfficialProblemsEntityIdCommentPost(entityId, {
        content,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['official-stats'] })
      toast.success('Official comment added successfully')
    },
    onError: () => {
      toast.error('Failed to add comment')
    },
  })

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard
            label="Assigned"
            value={stats.problems_assigned}
            icon={Briefcase}
            color="text-blue-500"
          />
          <StatCard
            label="In Progress"
            value={stats.problems_in_progress}
            icon={Clock}
            color="text-yellow-500"
          />
          <StatCard
            label="Resolved"
            value={stats.problems_resolved}
            icon={CheckCircle}
            color="text-green-500"
          />
          <StatCard
            label="Avg Resolution"
            value={stats.avg_resolution_days ? `${stats.avg_resolution_days.toFixed(1)}d` : 'N/A'}
            icon={Clock}
            color="text-purple-500"
            isString
          />
          <StatCard
            label="Zones Managed"
            value={stats.zones_managed}
            icon={MapPin}
            color="text-orange-500"
          />
          <StatCard
            label="Official Responses"
            value={stats.official_responses}
            icon={MessageSquare}
            color="text-indigo-500"
          />
        </div>
      )}

      {/* Section Tabs */}
      <div className="flex gap-2 border-b border-border">
        <button
          onClick={() => setActiveSection('stats')}
          className={`px-4 py-2 font-medium border-b-2 -mb-px transition-colors ${
            activeSection === 'stats'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveSection('assigned')}
          className={`px-4 py-2 font-medium border-b-2 -mb-px transition-colors ${
            activeSection === 'assigned'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Assigned Problems ({stats?.problems_assigned || 0})
        </button>
        <button
          onClick={() => setActiveSection('in-progress')}
          className={`px-4 py-2 font-medium border-b-2 -mb-px transition-colors ${
            activeSection === 'in-progress'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          In Progress ({stats?.problems_in_progress || 0})
        </button>
        <button
          onClick={() => setActiveSection('zones')}
          className={`px-4 py-2 font-medium border-b-2 -mb-px transition-colors ${
            activeSection === 'zones'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          My Zones ({stats?.zones_managed || 0})
        </button>
      </div>

      {/* Content */}
      <div>
        {activeSection === 'stats' && (
          <div className="text-center py-12">
            <Briefcase className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Official Dashboard</h3>
            <p className="text-muted-foreground">
              Select a tab above to manage your assigned problems and zones
            </p>
          </div>
        )}

        {activeSection === 'assigned' && (
          <div className="space-y-4">
            {/* Filter */}
            <div className="flex gap-4 items-center">
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value as ProblemStatus | '')}
                className="px-4 py-2 bg-dark-input text-text-primary border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary [&>option]:bg-dark-card [&>option]:text-text-primary"
              >
                <option value="">All Status</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            {loadingAssigned ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : assignedProblems?.items.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No assigned problems found
              </div>
            ) : (
              <div className="space-y-3">
                {assignedProblems?.items.map(item => (
                  <div key={item.problem.entity_id} className="bg-card border border-border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <Link
                          to={`/problems/${item.problem.entity_id}`}
                          className="text-lg font-semibold hover:text-primary"
                        >
                          {item.problem.title}
                        </Link>
                        <p className="text-sm text-muted-foreground mt-1">
                          by {item.problem.author_username} • {new Date(item.problem.created_at).toLocaleString()}
                        </p>
                        {item.assigned_at && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Assigned: {new Date(item.assigned_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <span className={`text-xs px-2 py-1 rounded ${getStatusBadgeColor(item.problem.status)}`}>
                          {item.problem.status}
                        </span>
                        <div className="text-xs text-muted-foreground mt-1">
                          Priority: {item.problem.priority_score.toFixed(2)}
                        </div>
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{item.problem.description}</p>

                    <div className="flex gap-2">
                      {item.problem.status === 'open' && (
                        <button
                          onClick={() => {
                            const note = prompt('Add note (optional):')
                            takeProblemMutation.mutate({
                              entityId: item.problem.entity_id,
                              note: note || undefined,
                            })
                          }}
                          disabled={takeProblemMutation.isPending}
                          className="px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors disabled:opacity-50"
                        >
                          <Clock className="w-4 h-4 inline mr-1" />
                          Take Problem
                        </button>
                      )}
                      {item.problem.status === 'in_progress' && (
                        <>
                          <button
                            onClick={() => {
                              const notes = prompt('Resolution notes (required):')
                              if (notes) {
                                resolveProblemMutation.mutate({
                                  entityId: item.problem.entity_id,
                                  resolution_notes: notes,
                                })
                              }
                            }}
                            disabled={resolveProblemMutation.isPending}
                            className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded transition-colors disabled:opacity-50"
                          >
                            <CheckCircle className="w-4 h-4 inline mr-1" />
                            Mark Resolved
                          </button>
                          <button
                            onClick={() => {
                              const content = prompt('Official comment:')
                              if (content) {
                                addCommentMutation.mutate({
                                  entityId: item.problem.entity_id,
                                  content,
                                })
                              }
                            }}
                            disabled={addCommentMutation.isPending}
                            className="px-3 py-1.5 text-sm bg-primary hover:bg-primary/90 text-primary-foreground rounded transition-colors disabled:opacity-50"
                          >
                            <MessageSquare className="w-4 h-4 inline mr-1" />
                            Add Comment
                          </button>
                        </>
                      )}
                      <Link
                        to={`/problems/${item.problem.entity_id}`}
                        className="px-3 py-1.5 text-sm bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded transition-colors"
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

        {activeSection === 'in-progress' && (
          <div className="space-y-4">
            {loadingInProgress ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : inProgressProblems?.items.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No problems in progress
              </div>
            ) : (
              <div className="space-y-3">
                {inProgressProblems?.items.map(item => (
                  <div key={item.problem.entity_id} className="bg-card border border-border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <Link
                          to={`/problems/${item.problem.entity_id}`}
                          className="text-lg font-semibold hover:text-primary"
                        >
                          {item.problem.title}
                        </Link>
                        <p className="text-sm text-muted-foreground mt-1">
                          by {item.problem.author_username}
                        </p>
                        {item.assigned_at && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Started: {new Date(item.assigned_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Priority: {item.problem.priority_score.toFixed(2)}
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{item.problem.description}</p>

                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          const notes = prompt('Resolution notes (required):')
                          if (notes) {
                            resolveProblemMutation.mutate({
                              entityId: item.problem.entity_id,
                              resolution_notes: notes,
                            })
                          }
                        }}
                        disabled={resolveProblemMutation.isPending}
                        className="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded transition-colors disabled:opacity-50"
                      >
                        <CheckCircle className="w-4 h-4 inline mr-1" />
                        Mark Resolved
                      </button>
                      <button
                        onClick={() => {
                          const content = prompt('Official comment:')
                          if (content) {
                            addCommentMutation.mutate({
                              entityId: item.problem.entity_id,
                              content,
                            })
                          }
                        }}
                        disabled={addCommentMutation.isPending}
                        className="px-3 py-1.5 text-sm bg-primary hover:bg-primary/90 text-primary-foreground rounded transition-colors disabled:opacity-50"
                      >
                        <MessageSquare className="w-4 h-4 inline mr-1" />
                        Add Comment
                      </button>
                      <Link
                        to={`/problems/${item.problem.entity_id}`}
                        className="px-3 py-1.5 text-sm bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded transition-colors"
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

        {activeSection === 'zones' && (
          <div className="space-y-4">
            {loadingZones ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : zones?.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No zones assigned to you
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {zones?.map(zone => (
                  <div key={zone.zone_id} className="bg-card border border-border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{zone.zone_name}</h3>
                        <p className="text-xs text-muted-foreground mt-1">
                          Zone ID: {zone.zone_id}
                        </p>
                      </div>
                      <MapPin className="w-5 h-5 text-primary" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Open Problems:</span>
                        <span className="font-medium">{zone.open_problems}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">In Progress:</span>
                        <span className="font-medium">{zone.in_progress_problems}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Resolved:</span>
                        <span className="font-medium text-green-500">{zone.resolved_problems}</span>
                      </div>
                    </div>
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

function StatCard({ label, value, icon: Icon, color, isString = false }: {
  label: string
  value: number | string
  icon: any
  color: string
  isString?: boolean
}) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <Icon className={`w-4 h-4 ${color}`} />
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  )
}

function getStatusBadgeColor(status: string) {
  switch (status) {
    case 'open':
      return 'bg-yellow-500/10 text-yellow-500'
    case 'in_progress':
      return 'bg-blue-500/10 text-blue-500'
    case 'resolved':
      return 'bg-green-500/10 text-green-500'
    case 'rejected':
      return 'bg-red-500/10 text-red-500'
    default:
      return 'bg-gray-500/10 text-gray-500'
  }
}
