import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import { X, MapPin, Loader2, Navigation } from 'lucide-react'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix Leaflet default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface LocationPickerProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (lat: number, lng: number, address?: string) => void
  initialPosition?: { lat: number; lng: number }
}

function LocationMarker({
  position,
  setPosition,
}: {
  position: [number, number]
  setPosition: (pos: [number, number]) => void
}) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng])
    },
  })

  return <Marker position={position} />
}

export default function LocationPicker({
  isOpen,
  onClose,
  onSelect,
  initialPosition,
}: LocationPickerProps) {
  const [position, setPosition] = useState<[number, number]>([
    initialPosition?.lat || 43.238293,
    initialPosition?.lng || 76.945465,
  ])
  const [isGettingLocation, setIsGettingLocation] = useState(false)
  const [address, setAddress] = useState<string>('')

  useEffect(() => {
    if (initialPosition) {
      setPosition([initialPosition.lat, initialPosition.lng])
    }
  }, [initialPosition])

  // Get address from coordinates (reverse geocoding)
  useEffect(() => {
    const fetchAddress = async () => {
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${position[0]}&lon=${position[1]}&accept-language=ru`
        )
        const data = await response.json()
        setAddress(data.display_name || '')
      } catch (error) {
        console.error('Failed to fetch address:', error)
      }
    }

    if (isOpen) {
      fetchAddress()
    }
  }, [position, isOpen])

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Геолокация не поддерживается вашим браузером')
      return
    }

    setIsGettingLocation(true)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setPosition([pos.coords.latitude, pos.coords.longitude])
        setIsGettingLocation(false)
      },
      (error) => {
        console.error('Ошибка получения геолокации:', error)
        alert('Не удалось получить вашу геолокацию')
        setIsGettingLocation(false)
      }
    )
  }

  const handleConfirm = () => {
    onSelect(position[0], position[1], address)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[10002] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-dark-card rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-dark-card border-b border-border p-4 flex items-center justify-between flex-shrink-0">
          <div>
            <h2 className="text-xl font-bold text-text-primary">Выберите местоположение</h2>
            <p className="text-sm text-text-secondary mt-1">
              Нажмите на карту или используйте свою геолокацию
            </p>
          </div>
          <button
            onClick={onClose}
            className="btn-ghost p-2 hover:bg-dark-hover rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Map */}
        <div className="flex-1 relative min-h-[400px]">
          <MapContainer
            center={position}
            zoom={15}
            className="w-full h-full"
            style={{ minHeight: '400px' }}
            zoomControl={false}
            attributionControl={false}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution=""
            />
            <LocationMarker position={position} setPosition={setPosition} />
          </MapContainer>

          {/* Get Location Button */}
          <button
            onClick={handleGetCurrentLocation}
            disabled={isGettingLocation}
            className="absolute top-4 right-4 z-[1000] btn-primary flex items-center gap-2 shadow-lg"
          >
            {isGettingLocation ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Navigation className="w-5 h-5" />
            )}
            Моя геолокация
          </button>
        </div>

        {/* Footer */}
        <div className="bg-dark-card border-t border-border p-4 flex-shrink-0">
          {/* Address Display */}
          {address && (
            <div className="mb-4 p-3 bg-dark-hover rounded-lg">
              <div className="flex items-start gap-2">
                <MapPin className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-text-muted mb-1">Адрес:</p>
                  <p className="text-sm text-text-primary">{address}</p>
                </div>
              </div>
            </div>
          )}

          {/* Coordinates */}
          <div className="mb-4 grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-text-muted mb-1">Широта</label>
              <input
                type="text"
                value={position[0].toFixed(6)}
                readOnly
                className="input w-full text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-text-muted mb-1">Долгота</label>
              <input
                type="text"
                value={position[1].toFixed(6)}
                readOnly
                className="input w-full text-sm"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button onClick={onClose} className="btn-ghost flex-1">
              Отмена
            </button>
            <button onClick={handleConfirm} className="btn-primary flex-1">
              Подтвердить
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
