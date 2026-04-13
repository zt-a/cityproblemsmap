import { useState, useRef } from 'react'
import { Upload, X, Image as ImageIcon, Video, Loader2 } from 'lucide-react'

interface MediaFile {
  id: string
  file: File
  preview: string
  type: 'image' | 'video'
}

interface MediaUploaderProps {
  files: MediaFile[]
  onChange: (files: MediaFile[]) => void
  maxImageSize?: number // MB
  maxVideoSize?: number // MB
}

export default function MediaUploader({
  files,
  onChange,
  maxImageSize = 30,
  maxVideoSize = 250,
}: MediaUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: MediaFile[] = []

    Array.from(selectedFiles).forEach((file) => {
      const isImage = file.type.startsWith('image/')
      const isVideo = file.type.startsWith('video/')

      if (!isImage && !isVideo) {
        alert(`Файл ${file.name} не является изображением или видео`)
        return
      }

      const maxSize = isImage ? maxImageSize : maxVideoSize
      const fileSizeMB = file.size / (1024 * 1024)

      if (fileSizeMB > maxSize) {
        alert(
          `Файл ${file.name} слишком большой (${fileSizeMB.toFixed(1)} МБ). Максимум: ${maxSize} МБ`
        )
        return
      }

      const preview = URL.createObjectURL(file)
      newFiles.push({
        id: `${Date.now()}-${Math.random()}`,
        file,
        preview,
        type: isImage ? 'image' : 'video',
      })
    })

    onChange([...files, ...newFiles])
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleRemove = (id: string) => {
    const fileToRemove = files.find((f) => f.id === id)
    if (fileToRemove) {
      URL.revokeObjectURL(fileToRemove.preview)
    }
    onChange(files.filter((f) => f.id !== id))
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200
          ${
            isDragging
              ? 'border-primary bg-primary/5 scale-[1.02]'
              : 'border-border hover:border-primary/50 hover:bg-dark-hover'
          }
        `}
      >
        <Upload className="w-12 h-12 text-text-muted mx-auto mb-3" />
        <p className="text-text-primary font-medium mb-1">
          Нажмите или перетащите файлы
        </p>
        <p className="text-sm text-text-secondary">
          Изображения до {maxImageSize} МБ, видео до {maxVideoSize} МБ
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,video/*"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />
      </div>

      {/* Preview Grid */}
      {files.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {files.map((file) => (
            <div
              key={file.id}
              className="relative aspect-square rounded-lg overflow-hidden bg-dark-hover group"
            >
              {file.type === 'image' ? (
                <img
                  src={file.preview}
                  alt="Preview"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center">
                  <Video className="w-8 h-8 text-primary mb-2" />
                  <p className="text-xs text-text-secondary px-2 text-center truncate w-full">
                    {file.file.name}
                  </p>
                </div>
              )}

              {/* Remove Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleRemove(file.id)
                }}
                className="absolute top-2 right-2 w-6 h-6 bg-danger/90 hover:bg-danger rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4 text-white" />
              </button>

              {/* Type Badge */}
              <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/60 rounded text-xs text-white flex items-center gap-1">
                {file.type === 'image' ? (
                  <ImageIcon className="w-3 h-3" />
                ) : (
                  <Video className="w-3 h-3" />
                )}
                {(file.file.size / (1024 * 1024)).toFixed(1)} МБ
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
