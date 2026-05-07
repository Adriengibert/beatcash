import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

const PROTECTED = ["/account"];

export async function middleware(req: NextRequest) {
  const res = NextResponse.next({ request: req });

  const supa = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => req.cookies.getAll(),
        setAll: (toSet) =>
          toSet.forEach(({ name, value, options }) => {
            req.cookies.set(name, value);
            res.cookies.set(name, value, options);
          }),
      },
    },
  );

  // Indispensable : refresh session token sur chaque requête
  const { data: { user } } = await supa.auth.getUser();

  // Gate
  const isProtected = PROTECTED.some((p) => req.nextUrl.pathname.startsWith(p));
  if (isProtected && !user) {
    const login = req.nextUrl.clone();
    login.pathname = "/login";
    login.searchParams.set("next", req.nextUrl.pathname);
    return NextResponse.redirect(login);
  }

  return res;
}

export const config = {
  matcher: [
    "/((?!api/webhook|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|css|js)$).*)",
  ],
};
