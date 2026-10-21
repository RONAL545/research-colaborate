import { NextRequest, NextResponse } from "next/server";
import { isSameOrigin } from "@/lib/server-origin";
export async function DELETE(request: NextRequest) {
  if (!isSameOrigin(request))
    return NextResponse.json({ detail: "Invalid origin" }, { status: 403 });
  const response = NextResponse.json({ authenticated: false });
  response.cookies.delete("nexo_session");
  return response;
}
