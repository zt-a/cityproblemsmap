import { useState, useRef, useEffect } from 'react'
import ProblemList from '../components/problem/ProblemList'
import MapView from '../components/map/MapView'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useProblems } from '../hooks/useProblems'

export default function MapPage() {
  const [selectedProblemId, setSelectedProblemId] = useState<number | null>(null)
  const [isPanelOpen, setIsPanelOpen] = useState(false) // Закрыта по умолчанию на /map
  const [isMapExpanded, setIsMapExpanded] = useState(true) // true = full, false = mini
  const [mapCenter, setMapCenter] = useState<[number, number] | null>(null)
  const startY = useRef(0)

  // Load problems from API
  const { data: problemsData } = useProblems({ limit: 100 })
  const problems = problemsData?.items || []

  // When clicking on a problem card, center map on that marker
  const handleCardClick = (id: number, lat: number, lng: number) => {
    setSelectedProblemId(id)
    setMapCenter([lat, lng])

    // On mobile: expand map and show header
    if (window.innerWidth < 768) {
      setIsMapExpanded(true)
    }
  }

  // When clicking on a map marker, show problem card and minimize map
  const handleMarkerClick = (id: number) => {
    setSelectedProblemId(id)

    // On mobile: minimize map first, then center after resize
    if (window.innerWidth < 768) {
      setIsMapExpanded(false)

      // Center map after it resizes to mini mode
      setTimeout(() => {
        const problem = problems.find(p => p.entity_id === id)
        if (problem) {
          setMapCenter([problem.latitude, problem.longitude])
        }
      }, 400) // Wait for transition + invalidateSize
    } else {
      // On desktop: center immediately
      const problem = problems.find(p => p.entity_id === id)
      if (problem) {
        setMapCenter([problem.latitude, problem.longitude])
      }
    }

    // On desktop: open panel if closed
    if (window.innerWidth >= 768 && !isPanelOpen) {
      setIsPanelOpen(true)
    }
  }

  // Hide/show header based on map state on mobile
  useEffect(() => {
    const header = document.querySelector('header')
    const menuButton = document.querySelector('header button:first-of-type') as HTMLButtonElement
    const floatingButton = document.getElementById('floating-menu-button')

    if (header && window.innerWidth < 768) {
      if (isMapExpanded) {
        // Show header, remove floating button
        header.style.transform = 'translateY(0)'
        if (floatingButton) {
          floatingButton.remove()
        }
      } else {
        // Hide header, show floating button
        header.style.transform = 'translateY(-100%)'

        if (menuButton && !floatingButton) {
          const buttonClone = menuButton.cloneNode(true) as HTMLElement
          buttonClone.style.position = 'fixed'
          buttonClone.style.top = '1rem'
          buttonClone.style.left = '1rem'
          buttonClone.style.zIndex = '10001'
          buttonClone.id = 'floating-menu-button'

          // Add click handler to cloned button
          buttonClone.addEventListener('click', () => {
            menuButton.click() // Trigger original button's click
          })

          document.body.appendChild(buttonClone)
        }
      }
    }

    // Cleanup: restore header and remove floating button on unmount
    return () => {
      if (header) {
        header.style.transform = 'translateY(0)'
      }
      const floatingBtn = document.getElementById('floating-menu-button')
      if (floatingBtn) {
        floatingBtn.remove()
      }
    }
  }, [isMapExpanded])

  // Touch handlers for mobile swipe
  const handleTouchStart = (e: React.TouchEvent) => {
    startY.current = e.touches[0].clientY
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    // Prevent default scrolling behavior
    e.preventDefault()
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    const endY = e.changedTouches[0].clientY
    const deltaY = endY - startY.current

    // Threshold for swipe detection (50px)
    if (Math.abs(deltaY) > 50) {
      if (deltaY < 0) {
        // Swipe up - minimize map (show problems list)
        setIsMapExpanded(false)
      } else {
        // Swipe down - expand map (full screen)
        setIsMapExpanded(true)
      }
    }
  }

  const mobileMapHeight = isMapExpanded ? 100 : 37 // 100% or 37%

  return (
    <div
      className="flex relative overflow-hidden md:h-[calc(100dvh-5rem)] md:mt-20"
      style={{
        height: isMapExpanded
          ? 'calc(100dvh - 5rem)' // Full map: minus only header (bottom nav overlays)
          : 'calc(100dvh - 4rem)', // Mini map: minus only bottom nav
      }}
    >
      {/* Desktop: Problem List - Left (collapsible) */}
      <div
        className={`border-r border-border overflow-hidden transition-all duration-300 flex-shrink-0 hidden md:block ${
          isPanelOpen ? 'w-problem-list' : 'w-0'
        }`}
      >
        <ProblemList
          selectedProblemId={selectedProblemId}
          onCardClick={handleCardClick}
          onClose={() => setIsPanelOpen(false)}
        />
      </div>

      {/* Desktop: Toggle button */}
      <button
        onClick={() => setIsPanelOpen(!isPanelOpen)}
        className={`hidden md:flex absolute top-1/2 -translate-y-1/2 z-[1001] w-8 h-16 bg-dark-card hover:bg-dark-hover border border-border items-center justify-center shadow-lg transition-all ${
          isPanelOpen ? 'rounded-r-xl left-problem-list' : 'rounded-xl left-4'
        }`}
      >
        {isPanelOpen ? (
          <ChevronLeft className="w-5 h-5 text-text-primary" />
        ) : (
          <ChevronRight className="w-5 h-5 text-text-primary" />
        )}
      </button>

      {/* Desktop: Map - Right (adaptive) */}
      <div className="hidden md:flex flex-1 p-4 overflow-hidden">
        <MapView
          onMarkerClick={handleMarkerClick}
          selectedProblemId={selectedProblemId}
          mapCenter={mapCenter}
          isPanelOpen={isPanelOpen}
          problems={problems}
        />
      </div>

      {/* Mobile: Swipeable Layout */}
      <div className="md:hidden flex flex-col w-full h-full relative">
        {/* Map Container - Swipeable */}
        <div
          className={`relative flex-shrink-0 transition-all duration-300 ease-out ${
            isMapExpanded ? 'mt-20' : 'mt-0'
          }`}
          style={{
            height: isMapExpanded ? 'calc(100% - 5rem)' : `${mobileMapHeight}%`,
          }}
        >
          {/* Map */}
          <div className="h-full w-full p-2">
            <MapView
              onMarkerClick={handleMarkerClick}
              onToggleMap={() => setIsMapExpanded(!isMapExpanded)}
              isMapExpanded={isMapExpanded}
              selectedProblemId={selectedProblemId}
              mapCenter={mapCenter}
              problems={problems}
            />
          </div>

          {/* Swipe Handle - Bottom of Map */}
          <div
            className="absolute bottom-0 left-0 right-0 z-[1002] flex items-center justify-center py-3 cursor-grab active:cursor-grabbing bg-gradient-to-t from-dark-bg/80 to-transparent touch-none"
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            <div className="w-12 h-1.5 bg-text-muted/60 rounded-full"></div>
          </div>
        </div>

        {/* Problem List - Bottom with global scroll */}
        {!isMapExpanded && (
          <div className="flex-1 overflow-y-auto overflow-x-hidden">
            <ProblemList
              selectedProblemId={selectedProblemId}
              onCardClick={handleCardClick}
              onClose={() => setIsMapExpanded(true)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
