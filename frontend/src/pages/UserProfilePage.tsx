import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin, Calendar, Users, FileText, Award, Loader2, UserPlus, UserMinus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useUserProfile } from '../hooks/useUser'
import { useProblems } from '../hooks/useProblems'
import { useFollowUser, useUnfollowUser, useFollowStatus } from '../hooks/useSocial'
import { useAuth } from '../hooks/useAuth'
import ProblemCard from '../components/problem/ProblemCard'

export default function UserProfilePage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const userEntityId = userId ? parseInt(userId) : undefined

  const { data: profile, isLoading: profileLoading, error } = useUserProfile(userEntityId)
  const { data: problemsData, isLoading: problemsLoading } = useProblems({
    // TODO: Add author filter when API supports it
  })
  const { data: followStatus } = useFollowStatus(userEntityId)
  const followMutation = useFollowUser()
  const unfollowMutation = useUnfollowUser()

  const isOwnProfile = currentUser?.entity_id === userEntityId
  const isFollowing = followStatus?.is_following || false

  const handleFollowToggle = async () => {
    if (!userEntityId) return

    try {
      if (isFollowing) {
        await unfollowMutation.mutateAsync(userEntityId)
      } else {
        await followMutation.mutateAsync(userEntityId)
      }
    } catch (error) {
      console.error('Failed to toggle follow:', error)
    }
  }

  if (profileLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-dark-bg">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-dark-bg">
        <div className="text-center">
          <p className="text-text-secondary text-lg mb-2">Пользователь не найден</p>
          <button
            onClick={() => navigate('/')}
            className="text-primary hover:underline"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    )
  }

  // Filter user's problems (temporary until API supports author filter)
  const userProblems = problemsData?.items.filter(
    (p) => p.author_entity_id === userEntityId
  ) || []

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <div className="bg-dark-card border-b border-border">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <button
            onClick={() => navigate(-1)}
            className="btn-ghost flex items-center gap-2 mb-4 hover:scale-105 active:scale-95"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Назад</span>
          </button>

          <div className="flex flex-col md:flex-row gap-6 items-start">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-dark-hover flex items-center justify-center text-4xl font-bold text-primary border-4 border-primary/20">
              {profile.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt={profile.username}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                profile.username.charAt(0).toUpperCase()
              )}
            </div>

            {/* Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-text-primary mb-2">
                {profile.username}
              </h1>

              {profile.bio && (
                <p className="text-text-secondary mb-4">{profile.bio}</p>
              )}

              {/* Stats */}
              <div className="flex flex-wrap gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-warning" />
                  <span className="text-text-secondary">Репутация:</span>
                  <span className="text-text-primary font-semibold">
                    {profile.reputation.toFixed(0)}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary" />
                  <span className="text-text-secondary">Проблем:</span>
                  <span className="text-text-primary font-semibold">
                    {profile.problems_count}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-success" />
                  <span className="text-text-secondary">Подписчиков:</span>
                  <span className="text-text-primary font-semibold">
                    {profile.followers_count}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-info" />
                  <span className="text-text-secondary">Подписок:</span>
                  <span className="text-text-primary font-semibold">
                    {profile.following_count}
                  </span>
                </div>
              </div>

              {/* Links */}
              {(profile.website || profile.social_links) && (
                <div className="flex flex-wrap gap-4 mt-4">
                  {profile.website && (
                    <a
                      href={profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline text-sm"
                    >
                      {profile.website}
                    </a>
                  )}
                  {profile.social_links && Object.entries(profile.social_links).map(([key, value]) => (
                    <a
                      key={key}
                      href={value as string}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline text-sm"
                    >
                      {key}
                    </a>
                  ))}
                </div>
              )}
            </div>

            {/* Follow Button */}
            {!isOwnProfile && currentUser && (
              <button
                onClick={handleFollowToggle}
                disabled={followMutation.isPending || unfollowMutation.isPending}
                className={`px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  isFollowing
                    ? 'bg-dark-hover text-text-primary hover:bg-dark-card border border-border'
                    : 'bg-primary text-white hover:bg-primary-hover'
                }`}
              >
                {followMutation.isPending || unfollowMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : isFollowing ? (
                  <>
                    <UserMinus className="w-4 h-4" />
                    Отписаться
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    Подписаться
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* User's Problems */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-text-primary mb-6">
          Проблемы пользователя ({userProblems.length})
        </h2>

        {problemsLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : userProblems.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {userProblems.map((problem) => (
              <ProblemCard
                key={problem.entity_id}
                problem={problem}
                onCardClick={() => navigate(`/problems/${problem.entity_id}`)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-text-muted mx-auto mb-4" />
            <p className="text-text-secondary">
              Пользователь ещё не создал ни одной проблемы
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
