import { NextRequest, NextResponse } from "next/server";
export async function DELETE(request: NextRequest) {
  const origin = request.headers.get("origin");
  if (
    (origin && origin !== request.nextUrl.origin) ||
    request.headers.get("sec-fetch-site") === "cross-site"
  )
    return NextResponse.json({ detail: "Invalid origin" }, { status: 403 });
  const response = NextResponse.json({ authenticated: false });
  response.cookies.delete("nexo_session");
  return response;
}
