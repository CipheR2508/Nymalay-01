/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Static export: the whole site is prerendered HTML, CSS and JS in `out/`.
  // Nothing runs on a server.
  //
  // This is a security decision as much as a hosting one. The site has no API
  // routes, no server actions and no data fetching, so a server would have
  // nothing to do except stay up and be patchable. Removing it removes the
  // entire Next.js server attack surface, which is where the outstanding
  // advisories live (image optimizer RCE, SSRF via rewrites, server function
  // disclosure). There is no server left to exploit them.
  output: 'export',

  // `output: 'export'` has no image optimizer, so `next/image` must emit a
  // plain <img>. Every image is already local and pre-sized in /public.
  images: { unoptimized: true },

  // Emit directory/index.html so the export works on any static host, not just
  // ones that rewrite clean URLs to .html.
  trailingSlash: true,
}

module.exports = nextConfig
