import { Navigate, Link, useSearchParams } from "react-router-dom";
import { Car, ArrowRight, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useState, type FormEvent } from "react";
import { Spinner } from "../components/ui/Spinner";
import { getSafeReturnPath } from "../utils/authRedirect";

export function LoginPage() {
  const { login, user, loading: authLoading } = useAuth();
  const [searchParams] = useSearchParams();
  const returnTo = getSafeReturnPath(searchParams.get("returnTo"));
  const signupLink = searchParams.get("returnTo")
    ? `/signup?returnTo=${encodeURIComponent(searchParams.get("returnTo")!)}`
    : "/signup";

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
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-surface-950 p-12 text-white lg:flex">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-600/20 via-transparent to-violet-600/10" />
        <div className="relative flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 shadow-lg shadow-brand-600/40">
            <Car className="h-6 w-6" />
          </div>
          <span className="font-display text-xl font-bold">AutoReport</span>
        </div>

        <div className="relative">
          <h1 className="font-display text-4xl font-bold leading-tight">
            Search car registration
            <br />
            <span className="bg-gradient-to-r from-brand-400 to-blue-300 bg-clip-text text-transparent">
              reports instantly
            </span>
          </h1>
          <p className="mt-4 max-w-md text-lg text-white/60">
            Access manufacturer data, filter by make, model, year, and registration date.
          </p>
          <div className="mt-8 flex gap-6 text-sm text-white/40">
            <div><span className="block text-2xl font-bold text-white">3,600+</span> vehicles</div>
            <div><span className="block text-2xl font-bold text-white">2012–22</span> year range</div>
            <div><span className="block text-2xl font-bold text-white">4</span> filters</div>
          </div>
        </div>

        <p className="relative text-sm text-white/40">© 2026 AutoReport · Car Registration Portal</p>
      </div>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md animate-fade-in">
          <div className="mb-8 lg:hidden">
            <div className="flex items-center gap-2">
              <Car className="h-6 w-6 text-brand-600" />
              <span className="font-display text-xl font-bold">AutoReport</span>
            </div>
          </div>

          <h2 className="font-display text-2xl font-bold text-surface-900">Welcome back</h2>
          <p className="mt-1 text-sm text-surface-800/60">Sign in to access your reports dashboard</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            {error && (
              <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="login-email" className="mb-1.5 block text-sm font-medium text-surface-800">
                Email
              </label>
              <input
                id="login-email"
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
              <label htmlFor="login-password" className="mb-1.5 block text-sm font-medium text-surface-800">
                Password
              </label>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  className="input-field pr-10"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
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
            </div>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Spinner size="sm" className="text-white" /> : (
                <>Sign in <ArrowRight className="h-4 w-4" /></>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-surface-800/60">
            Don&apos;t have an account?{" "}
            <Link to={signupLink} className="font-semibold text-brand-600 hover:text-brand-700">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
