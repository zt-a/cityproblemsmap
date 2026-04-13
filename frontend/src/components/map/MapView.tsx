import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { ZoomIn, ZoomOut, Locate, X, Maximize2, Sun, Moon } from 'lucide-react'
import { getInitialLocation, getUserLocation, saveLocation } from '../../utils/geolocation'
import type { ProblemPublic } from '../../api/generated/models/ProblemPublic'

interface MapViewProps {
  onMarkerClick: (id: number) => void
  onToggleMap?: () => void
  isMapExpanded?: boolean
  selectedProblemId?: number | null
  mapCenter?: [number, number] | null
  isPanelOpen?: boolean
  problems?: ProblemPublic[]
}

// Custom marker icons by problem type
const createMarkerIcon = (status: string, problemType?: string) => {
  const statusColors = {
    pending: '#EF4444',
    in_progress: '#F59E0B',
    resolved: '#10B981',
    rejected: '#6B7280',
  }

  // Icons for different problem types
  const typeIcons = {
    pothole: '🕳️',
    garbage: '🗑️',
    road_work: '🚧',
    pollution: '☠️',
    traffic_light: '🚦',
    flooding: '💧',
    lighting: '💡',
    construction: '🏗️',
    roads: '🛣️',
    infrastructure: '🏢',
    other: '⚠️',
  }

  const icon = typeIcons[problemType as keyof typeof typeIcons] || '📍'
  const color = statusColors[status as keyof typeof statusColors] || '#6B7280'

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        position: relative;
        width: 40px;
        height: 40px;
      ">
        <div style="
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 0;
          border-left: 8px solid transparent;
          border-right: 8px solid transparent;
          border-top: 12px solid ${color};
        "></div>
        <div style="
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 32px;
          height: 32px;
          background: ${color};
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
        ">${icon}</div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  })
}

function MarkerWithRef({ problem, isSelected, onMarkerClick, markersRef }: {
  problem: ProblemPublic
  isSelected: boolean
  onMarkerClick: (id: number) => void
  markersRef: React.RefObject<{ [key: number]: L.Marker }>
}) {
  const markerRef = useRef<L.Marker>(null)
  const navigate = useNavigate()

  // Validate coordinates
  const hasValidCoordinates =
    problem.latitude !== undefined &&
    problem.latitude !== null &&
    problem.longitude !== undefined &&
    problem.longitude !== null &&
    !isNaN(problem.latitude) &&
    !isNaN(problem.longitude)

  useEffect(() => {
    const markers = markersRef.current
    if (markerRef.current && markers) {
      markers[problem.entity_id] = markerRef.current
    }
    return () => {
      if (markers) {
        delete markers[problem.entity_id]
      }
    }
  }, [problem.entity_id, markersRef])

  const handlePopupClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    navigate(`/problems/${problem.entity_id}`)
  }

  if (!hasValidCoordinates) {
    return null
  }

  return (
    <Marker
      ref={markerRef}
      position={[problem.latitude, problem.longitude]}
      icon={createMarkerIcon(problem.status, problem.problem_type)}
      eventHandlers={{
        click: () => onMarkerClick(problem.entity_id),
      }}
      zIndexOffset={isSelected ? 1000 : 0}
    >
      <Popup>
        <div className="text-sm">
          <p className="font-semibold text-gray-900">{problem.title}</p>
          <button
            onClick={handlePopupClick}
            className="text-xs text-blue-600 hover:text-blue-800 hover:underline mt-1 cursor-pointer"
          >
            Нажмите для деталей →
          </button>
        </div>
      </Popup>
    </Marker>
  )
}

function MapController({ center }: { center: [number, number] | null }) {
  const map = useMap()

  useEffect(() => {
    if (center) {
      // Force map to recalculate its size before centering
      map.invalidateSize()

      // Small delay to ensure size is updated
      setTimeout(() => {
        map.setView(center, 15, { animate: true })
      }, 100)
    }
  }, [center, map])

  return null
}

function MapResizeHandler({ isMapExpanded, isPanelOpen }: { isMapExpanded?: boolean; isPanelOpen?: boolean }) {
  const map = useMap()

  useEffect(() => {
    // Invalidate size when component mounts
    const timer = setTimeout(() => {
      map.invalidateSize()
    }, 100)

    // Listen for window resize
    const handleResize = () => {
      map.invalidateSize()
    }

    window.addEventListener('resize', handleResize)

    return () => {
      clearTimeout(timer)
      window.removeEventListener('resize', handleResize)
    }
  }, [map])

  // Invalidate size when map expands/collapses (mobile)
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize()
    }, 350) // Wait for transition to complete

    return () => clearTimeout(timer)
  }, [isMapExpanded, map])

  // Invalidate size when panel opens/closes (desktop)
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize()
    }, 350) // Wait for transition to complete

    return () => clearTimeout(timer)
  }, [isPanelOpen, map])

  return null
}

export default function MapView({
  onMarkerClick,
  onToggleMap,
  isMapExpanded = true,
  selectedProblemId,
  mapCenter,
  isPanelOpen,
  problems = []
}: MapViewProps) {
  const mapRef = useRef<L.Map | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const markersRef = useRef<{ [key: number]: L.Marker }>({})
  const [initialCenter, setInitialCenter] = useState<[number, number]>([42.8746, 74.5698]) // Default: Bishkek
  const [isLocating, setIsLocating] = useState(false)
  const [isDarkTheme, setIsDarkTheme] = useState(true) // Dark theme by default

  // Получить начальное местоположение по IP при монтировании
  useEffect(() => {
    getInitialLocation().then(location => {
      setInitialCenter([location.latitude, location.longitude])
    })
  }, [])

  // Open popup for selected marker
  useEffect(() => {
    if (selectedProblemId && markersRef.current) {
      const marker = markersRef.current[selectedProblemId]
      if (marker) {
        // Small delay to ensure map has centered before opening popup
        setTimeout(() => {
          marker.openPopup()
        }, 300)
      }
    }
  }, [selectedProblemId])

  // Observe container size changes
  useEffect(() => {
    if (!containerRef.current || !mapRef.current) return

    const resizeObserver = new ResizeObserver(() => {
      if (mapRef.current) {
        setTimeout(() => {
          mapRef.current?.invalidateSize()
        }, 300)
      }
    })

    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
    }
  }, [])

  const handleZoomIn = () => {
    mapRef.current?.zoomIn()
  }

  const handleZoomOut = () => {
    mapRef.current?.zoomOut()
  }

  const handleLocate = async () => {
    setIsLocating(true)
    try {
      const location = await getUserLocation()
      mapRef.current?.setView([location.latitude, location.longitude], 15)
      // Сохраняем точное местоположение
      saveLocation(location)
    } catch (error) {
      console.error('Failed to get user location:', error)
      alert('Не удалось получить ваше местоположение. Проверьте разрешения браузера.')
    } finally {
      setIsLocating(false)
    }
  }

  return (
    <div ref={containerRef} className="relative h-full w-full rounded-2xl overflow-hidden" style={{ background: '#0B1220' }}>
      <MapContainer
        center={initialCenter}
        zoom={13}
        className="h-full w-full"
        zoomControl={false}
        attributionControl={false}
        ref={mapRef}
        style={{ background: '#0B1220' }}
      >
        {/* Dark theme tile layer */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution=""
        />

        {/* Markers */}
        {problems.map((problem) => {
          const isSelected = problem.entity_id === selectedProblemId
          return (
            <MarkerWithRef
              key={problem.entity_id}
              problem={problem}
              isSelected={isSelected}
              onMarkerClick={onMarkerClick}
              markersRef={markersRef}
            />
          )
        })}

        <MapController center={mapCenter} />
        <MapResizeHandler isMapExpanded={isMapExpanded} isPanelOpen={isPanelOpen} />
      </MapContainer>

      {/* Toggle button - top right (mobile only) */}
      {onToggleMap && (
        <div className="md:hidden absolute top-4 right-4 z-[1000]">
          <button
            onClick={onToggleMap}
            className="w-10 h-10 bg-dark-card hover:bg-dark-hover border border-border rounded-2xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 active:scale-95"
            aria-label={isMapExpanded ? 'Свернуть карту' : 'Развернуть карту'}
          >
            {isMapExpanded ? (
              <X className="w-5 h-5 text-text-primary" />
            ) : (
              <Maximize2 className="w-5 h-5 text-text-primary" />
            )}
          </button>
        </div>
      )}

      {/* Floating controls - moved to bottom right */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2 z-[1000]">
        <button
          onClick={handleZoomIn}
          className="w-10 h-10 bg-dark-card hover:bg-dark-hover border border-border rounded-2xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 active:scale-95"
        >
          <ZoomIn className="w-5 h-5 text-text-primary" />
        </button>
        <button
          onClick={handleZoomOut}
          className="w-10 h-10 bg-dark-card hover:bg-dark-hover border border-border rounded-2xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 active:scale-95"
        >
          <ZoomOut className="w-5 h-5 text-text-primary" />
        </button>
        <button
          onClick={handleLocate}
          disabled={isLocating}
          className="w-10 h-10 bg-dark-card hover:bg-dark-hover border border-border rounded-2xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Определить моё местоположение"
        >
          {isLocating ? (
            <div className="w-5 h-5 border-2 border-text-primary border-t-transparent rounded-full animate-spin" />
          ) : (
            <Locate className="w-5 h-5 text-text-primary" />
          )}
        </button>
      </div>
    </div>
  )
}
