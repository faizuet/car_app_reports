import { useEffect, useState, type FormEvent } from "react";
import {
  User,
  Save,
  Shield,
  Mail,
  Phone,
  FileText,
  AtSign,
  Calendar,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { changePassword, updateProfile, uploadAvatar, removeAvatar } from "../api/profile";
import { PageHeader } from "../components/ui/PageHeader";
import { Spinner } from "../components/ui/Spinner";
import { ProfileAvatar } from "../components/profile/ProfileAvatar";
import { useToast } from "../context/ToastContext";

type Tab = "general" | "account" | "security";

const tabs: { id: Tab; label: string; icon: typeof User }[] = [
  { id: "general", label: "General", icon: User },
  { id: "account", label: "Account", icon: Mail },
  { id: "security", label: "Security", icon: Shield },
];

export function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<Tab>("general");

  const [displayName, setDisplayName] = useState("");
  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [savingGeneral, setSavingGeneral] = useState(false);
  const [savingAccount, setSavingAccount] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name ?? "");
      setUsername(user.username);
      setBio(user.bio ?? "");
      setPhone(user.phone ?? "");
      setEmail(user.email);
    }
  }, [user]);

  const handleGeneralSave = async (e: FormEvent) => {
    e.preventDefault();
    setSavingGeneral(true);
    try {
      await updateProfile({
        display_name: displayName || undefined,
        username,
        bio: bio || undefined,
        phone: phone || undefined,
      });
      await refreshUser();
      toast("Profile updated!", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Update failed", "error");
    } finally {
      setSavingGeneral(false);
    }
  };

  const handleAccountSave = async (e: FormEvent) => {
    e.preventDefault();
    setSavingAccount(true);
    try {
      await updateProfile({ email });
      await refreshUser();
      toast("Email updated!", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Update failed", "error");
    } finally {
      setSavingAccount(false);
    }
  };

  const handlePasswordSave = async (e: FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast("Passwords do not match", "error");
      return;
    }
    setSavingPassword(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      toast("Password changed successfully!", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Password change failed", "error");
    } finally {
      setSavingPassword(false);
    }
  };

  const handleAvatarUpload = async (file: File) => {
    try {
      await uploadAvatar(file);
      await refreshUser();
      toast("Profile photo updated!", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Upload failed", "error");
      throw err;
    }
  };

  const handleAvatarRemove = async () => {
    try {
      await removeAvatar();
      await refreshUser();
      toast("Profile photo removed", "info");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to remove photo", "error");
      throw err;
    }
  };

  const displayLabel = user?.display_name || user?.username || "User";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <PageHeader title="Profile" description="Manage your photo, personal info, and security" />

      {/* Profile header card */}
      <div className="card overflow-hidden">
        <div className="bg-gradient-to-br from-brand-600 via-brand-700 to-indigo-800 px-6 pb-16 pt-8">
          <div className="flex flex-col items-center text-center sm:flex-row sm:items-end sm:gap-6 sm:text-left">
            <div className="-mb-12 sm:-mb-0 sm:translate-y-8">
              <ProfileAvatar
                name={displayLabel}
                imageUrl={user?.profile_image ?? null}
                size="lg"
                editable
                onUpload={handleAvatarUpload}
                onRemove={handleAvatarRemove}
              />
            </div>
            <div className="mt-14 sm:mt-0 sm:pb-2">
              <h2 className="font-display text-2xl font-bold text-white">{displayLabel}</h2>
              <p className="text-sm text-white/70">@{user?.username}</p>
              {user?.bio && (
                <p className="mt-2 max-w-md text-sm text-white/60">{user.bio}</p>
              )}
            </div>
          </div>
        </div>

        <div
          role="tablist"
          aria-label="Profile settings"
          className="flex flex-wrap gap-1 border-b border-surface-200 px-4 pt-4 sm:px-6"
        >
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              role="tab"
              id={`tab-${id}`}
              aria-selected={activeTab === id}
              aria-controls={`panel-${id}`}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 rounded-t-lg px-4 py-2.5 text-sm font-medium transition ${
                activeTab === id
                  ? "border-b-2 border-brand-600 text-brand-600"
                  : "text-surface-800/60 hover:text-surface-900"
              }`}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              {label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === "general" && (
            <div role="tabpanel" id="panel-general" aria-labelledby="tab-general">
            <form onSubmit={handleGeneralSave} className="space-y-5">
              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium">
                  <User className="h-4 w-4 text-surface-800/50" /> Display name
                </label>
                <input
                  className="input-field"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="How you want to be called"
                />
                <p className="mt-1 text-xs text-surface-800/50">Shown on your profile and dashboard</p>
              </div>

              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium">
                  <AtSign className="h-4 w-4 text-surface-800/50" /> Username
                </label>
                <input
                  className="input-field"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  minLength={3}
                />
              </div>

              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium">
                  <FileText className="h-4 w-4 text-surface-800/50" /> Bio
                </label>
                <textarea
                  className="input-field min-h-[100px] resize-y"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Tell us a bit about yourself..."
                  maxLength={500}
                />
                <p className="mt-1 text-right text-xs text-surface-800/50">{bio.length}/500</p>
              </div>

              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium">
                  <Phone className="h-4 w-4 text-surface-800/50" /> Phone
                </label>
                <input
                  type="tel"
                  className="input-field"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 234 567 8900"
                />
              </div>

              <button type="submit" className="btn-primary" disabled={savingGeneral}>
                {savingGeneral ? <Spinner size="sm" className="text-white" /> : (
                  <><Save className="h-4 w-4" /> Save changes</>
                )}
              </button>
            </form>
            </div>
          )}

          {activeTab === "account" && (
            <div role="tabpanel" id="panel-account" aria-labelledby="tab-account">
            <form onSubmit={handleAccountSave} className="space-y-5">
              <div className="rounded-lg bg-surface-50 p-4 text-sm text-surface-800/70">
                <p className="font-medium text-surface-900">Account information</p>
                <p className="mt-1">Your email is used for login and account recovery.</p>
              </div>

              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium">
                  <Mail className="h-4 w-4 text-surface-800/50" /> Email address
                </label>
                <input
                  type="email"
                  className="input-field"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              {user?.created_at && (
                <div className="flex items-center gap-2 text-sm text-surface-800/50">
                  <Calendar className="h-4 w-4" />
                  Member since {new Date(user.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </div>
              )}

              <button type="submit" className="btn-primary" disabled={savingAccount}>
                {savingAccount ? <Spinner size="sm" className="text-white" /> : (
                  <><Save className="h-4 w-4" /> Update email</>
                )}
              </button>
            </form>
            </div>
          )}

          {activeTab === "security" && (
            <div role="tabpanel" id="panel-security" aria-labelledby="tab-security">
            <form onSubmit={handlePasswordSave} className="space-y-5">
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                Choose a strong password with at least 6 characters.
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">Current password</label>
                <input
                  type="password"
                  className="input-field"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">New password</label>
                <input
                  type="password"
                  className="input-field"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={6}
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">Confirm new password</label>
                <input
                  type="password"
                  className="input-field"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                />
              </div>

              <button type="submit" className="btn-primary" disabled={savingPassword}>
                {savingPassword ? <Spinner size="sm" className="text-white" /> : (
                  <><Shield className="h-4 w-4" /> Change password</>
                )}
              </button>
            </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
