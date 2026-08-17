import { useRef, useState } from "react";
import { Camera, Trash2, User } from "lucide-react";
import { getAvatarUrl } from "../../api/client";
import { Spinner } from "../ui/Spinner";

interface ProfileAvatarProps {
  name: string;
  imageUrl: string | null;
  size?: "md" | "lg";
  editable?: boolean;
  onUpload?: (file: File) => Promise<void>;
  onRemove?: () => Promise<void>;
}

const sizes = {
  md: "h-16 w-16 text-xl",
  lg: "h-28 w-28 text-4xl",
};

export function ProfileAvatar({
  name,
  imageUrl,
  size = "lg",
  editable = false,
  onUpload,
  onRemove,
}: ProfileAvatarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const avatarUrl = getAvatarUrl(imageUrl);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !onUpload) return;

    setUploading(true);
    try {
      await onUpload(file);
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div className="relative inline-block">
      <div
        className={`${sizes[size]} relative flex items-center justify-center overflow-hidden rounded-2xl border-4 border-white bg-brand-100 font-bold text-brand-700 shadow-lg`}
      >
        {uploading ? (
          <Spinner size="md" />
        ) : avatarUrl ? (
          <img src={avatarUrl} alt={name} className="h-full w-full object-cover" />
        ) : (
          <span>{name.charAt(0).toUpperCase()}</span>
        )}
      </div>

      {editable && (
        <>
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            className="hidden"
            onChange={handleFile}
          />
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={uploading}
            className="absolute -bottom-1 -right-1 flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-brand-600 text-white shadow-md transition hover:bg-brand-700"
            title="Upload photo"
          >
            <Camera className="h-4 w-4" />
          </button>
          {avatarUrl && onRemove && (
            <button
              type="button"
              onClick={onRemove}
              disabled={uploading}
              className="absolute -bottom-1 -left-1 flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-red-500 text-white shadow-md transition hover:bg-red-600"
              title="Remove photo"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </>
      )}

      {!avatarUrl && !uploading && editable && (
        <div className="absolute inset-0 flex items-center justify-center rounded-2xl bg-black/0 transition hover:bg-black/10">
          <User className="h-8 w-8 text-transparent" />
        </div>
      )}
    </div>
  );
}
