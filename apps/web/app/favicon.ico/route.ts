const faviconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0f2f2f"/>
  <path d="M18 17h28v8H18z" fill="#f4ead8"/>
  <path d="M18 30h28v8H18z" fill="#78b8a8"/>
  <path d="M18 43h18v8H18z" fill="#d6a85f"/>
  <path d="M42 43h4v8h-4z" fill="#f4ead8"/>
</svg>`;

export function GET() {
  return new Response(faviconSvg, {
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      "cache-control": "public, max-age=86400",
    },
  });
}
