import { Navigate, Link, useSearchParams } from "react-router-dom";
import { Car, ArrowRight, Eye, EyeOff, CheckCircle2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useState, type FormEvent } from "react";
import { Spinner } from "../components/ui/Spinner";
import { getSafeReturnPath } from "../utils/authRedirect";

export function SignupPage() {
  const { signup, user, loading: authLoading } = useAuth();
  const [searchParams] = useSearchParams();
  const returnTo = getSafeReturnPath(searchParams.get("returnTo"));
  const loginLink = searchParams.get("returnTo")
    ? `/login?returnTo=${encodeURIComponent(searchParams.get("returnTo")!)}`
    : "/login";

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (user) return <Navigate to={returnTo} replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(username, email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  const passwordChecks = [
    { label: "At least 6 characters", ok: password.length >= 6 },
  ];

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 p-6 gradient-mesh">
      <div className="w-full max-w-md animate-fade-in">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-600 shadow-lg shadow-brand-600/30">
            <Car className="h-8 w-8 text-white" />
          </div>
          <h1 className="font-display text-2xl font-bold">Create your account</h1>
          <p className="mt-1 text-sm text-surface-800/60">
            Start searching car registration reports
          </p>
        </div>

        <div className="card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="signup-username" className="mb-1.5 block text-sm font-medium">
                Username
              </label>
              <input
                id="signup-username"
                className="input-field"
                placeholder="johndoe"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={3}
                autoComplete="username"
              />
            </div>

            <div>
              <label htmlFor="signup-email" className="mb-1.5 block text-sm font-medium">
                Email
              </label>
              <input
                id="signup-email"
                type="email"
                className="input-field"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div>
              <label htmlFor="signup-password" className="mb-1.5 block text-sm font-medium">
                Password
              </label>
              <div className="relative">
                <input
                  id="signup-password"
                  type={showPassword ? "text" : "password"}
                  className="input-field pr-10"
                  placeholder="Min. 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-800/40 hover:text-surface-800"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {password && (
                <ul className="mt-2 space-y-1">
                  {passwordChecks.map(({ label, ok }) => (
                    <li key={label} className={`flex items-center gap-1.5 text-xs ${ok ? "text-emerald-600" : "text-surface-800/40"}`}>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      {label}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Spinner size="sm" className="text-white" /> : (
                <>Create account <ArrowRight className="h-4 w-4" /></>
              )}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-sm text-surface-800/60">
          Already have an account?{" "}
          <Link to={loginLink} className="font-semibold text-brand-600 hover:text-brand-700">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
