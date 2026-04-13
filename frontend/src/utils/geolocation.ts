// Определение местоположения по IP
export interface LocationData {
  latitude: number;
  longitude: number;
  city?: string;
  country?: string;
}

// Дефолтное местоположение (Бишкек, Кыргызстан)
const DEFAULT_LOCATION: LocationData = {
  latitude: 42.8746,
  longitude: 74.5698,
  city: 'Бишкек',
  country: 'Кыргызстан'
};

/**
 * Получить местоположение по IP адресу
 * Использует бесплатный API ipapi.co
 */
export async function getLocationByIP(): Promise<LocationData> {
  try {
    const response = await fetch('https://ipapi.co/json/');

    if (!response.ok) {
      throw new Error('Failed to fetch location');
    }

    const data = await response.json();

    return {
      latitude: data.latitude || DEFAULT_LOCATION.latitude,
      longitude: data.longitude || DEFAULT_LOCATION.longitude,
      city: data.city,
      country: data.country_name
    };
  } catch (error) {
    console.warn('Failed to get location by IP, using default:', error);
    return DEFAULT_LOCATION;
  }
}

/**
 * Получить точное местоположение через браузер (требует разрешения)
 */
export function getUserLocation(): Promise<LocationData> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      },
      (error) => {
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    );
  });
}

/**
 * Сохранить местоположение в localStorage
 */
export function saveLocation(location: LocationData): void {
  localStorage.setItem('user_location', JSON.stringify(location));
}

/**
 * Получить сохраненное местоположение из localStorage
 */
export function getSavedLocation(): LocationData | null {
  try {
    const saved = localStorage.getItem('user_location');
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.warn('Failed to parse saved location:', error);
  }
  return null;
}

/**
 * Получить местоположение с приоритетом:
 * 1. Сохраненное в localStorage
 * 2. По IP
 * 3. Дефолтное
 */
export async function getInitialLocation(): Promise<LocationData> {
  // Проверяем сохраненное местоположение
  const saved = getSavedLocation();
  if (saved) {
    return saved;
  }

  // Получаем по IP
  const ipLocation = await getLocationByIP();

  // Сохраняем для следующего раза
  saveLocation(ipLocation);

  return ipLocation;
}
