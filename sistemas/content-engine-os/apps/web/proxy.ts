import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Redireciona para /login quem não tem cookie de sessão. A validação real
// (assinatura/expiração) é feita pela API; aqui é só o gate de navegação.
export function proxy(req: NextRequest) {
  if (req.cookies.has('cos_session')) {
    return NextResponse.next()
  }
  const url = req.nextUrl.clone()
  url.pathname = '/login'
  url.search = ''
  return NextResponse.redirect(url)
}

export const config = {
  matcher: ['/((?!login|_next/static|_next/image|favicon.ico|api/).*)'],
}
