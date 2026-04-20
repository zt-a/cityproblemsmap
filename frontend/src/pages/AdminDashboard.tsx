import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { UserRole } from '../api/generated'
import { Shield, Users, Briefcase } from 'lucide-react'
import AdminPanel from '../components/admin/AdminPanel'
import ModeratorPanel from '../components/admin/ModeratorPanel'
import OfficialPanel from '../components/admin/OfficialPanel'

type TabType = 'admin' | 'moderator' | 'official'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>(() => {
    // Auto-select tab based on user role
    if (user?.role === UserRole.ADMIN) return 'admin'
    if (user?.role === UserRole.MODERATOR) return 'moderator'
    if (user?.role === UserRole.OFFICIAL) return 'official'
    return 'moderator'
  })

  // Check if user has access to admin features
  const hasAdminAccess = user?.role === UserRole.ADMIN
  const hasModeratorAccess = user?.role === UserRole.ADMIN || user?.role === UserRole.MODERATOR
  const hasOfficialAccess = user?.role === UserRole.ADMIN || user?.role === UserRole.OFFICIAL

  if (!hasAdminAccess && !hasModeratorAccess && !hasOfficialAccess) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <Shield className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2 text-text-primary">Access Denied</h1>
          <p className="text-text-secondary">
            You don't have permission to access this page.
          </p>
        </div>
      </div>
    )
  }

  const tabs = [
    {
      id: 'admin' as TabType,
      label: 'Admin',
      icon: Shield,
      visible: hasAdminAccess,
    },
    {
      id: 'moderator' as TabType,
      label: 'Moderator',
      icon: Users,
      visible: hasModeratorAccess,
    },
    {
      id: 'official' as TabType,
      label: 'Official',
      icon: Briefcase,
      visible: hasOfficialAccess,
    },
  ].filter(tab => tab.visible)

  return (
    <div className="min-h-screen bg-dark-bg">
      <div className="border-b border-border bg-dark-card">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between py-4">
            <h1 className="text-2xl font-bold text-text-primary">Admin Dashboard</h1>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <span>Role:</span>
              <span className="font-medium text-text-primary">{user?.role}</span>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1">
            {tabs.map(tab => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-3 font-medium transition-colors
                    border-b-2 -mb-px
                    ${isActive
                      ? 'border-primary text-primary'
                      : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="container mx-auto px-4 py-6">
        {activeTab === 'admin' && hasAdminAccess && <AdminPanel />}
        {activeTab === 'moderator' && hasModeratorAccess && <ModeratorPanel />}
        {activeTab === 'official' && hasOfficialAccess && <OfficialPanel />}
      </div>
    </div>
  )
}
