const ALLOWED_PATHS = ["/dashboard", "/reports", "/cars", "/profile"];

export function getSafeReturnPath(returnTo: string | null): string {
  if (!returnTo || !returnTo.startsWith("/") || returnTo.startsWith("//")) {
    return "/dashboard";
  }

  const pathname = returnTo.split("?")[0];
  if (!ALLOWED_PATHS.includes(pathname)) {
    return "/dashboard";
  }

  return returnTo;
}

export function buildLoginPath(returnTo: string): string {
  return `/login?returnTo=${encodeURIComponent(returnTo)}`;
}
