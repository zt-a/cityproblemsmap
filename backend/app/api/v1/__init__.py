from fastapi import APIRouter
from . import ( users, auth, problems, comments, votes,
                zones, analytics, simulation, media, admin,
                moderator, official, notifications, health,
                two_factor, subscriptions, reports, ai, moderation_bans,
                user_settings, analytics_extended, gamification, social, streaming, resolution, duplicates, moderation_queue )

router = APIRouter(prefix='/v1')

router.include_router(users.router)
router.include_router(auth.router)
router.include_router(problems.router)
router.include_router(comments.router)
router.include_router(votes.router)
router.include_router(zones.router)
router.include_router(analytics.router)
router.include_router(analytics_extended.router)
router.include_router(simulation.router)
router.include_router(media.router)
router.include_router(streaming.router)
router.include_router(resolution.router)
router.include_router(duplicates.router)
router.include_router(moderation_queue.router)
router.include_router(admin.router)
router.include_router(moderator.router)
router.include_router(official.router)
router.include_router(notifications.router)
router.include_router(health.router)
router.include_router(two_factor.router)
router.include_router(subscriptions.router)
router.include_router(reports.router)
router.include_router(ai.router)
router.include_router(moderation_bans.router)
#router.include_router(fundraising.router) # в процессе разработки 
router.include_router(user_settings.router)
router.include_router(gamification.router)
router.include_router(social.router)