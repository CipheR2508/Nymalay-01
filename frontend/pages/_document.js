import { Html, Head, Main, NextScript } from 'next/document'

/*
 * Scroll-reveal animations hide their targets until IntersectionObserver
 * marks them visible. If that never runs, the page renders blank.
 *
 * `no-js` is set on <html> in the server HTML and stripped by a blocking
 * script here, before first paint. So the reveal styles only ever apply when
 * we know JS is alive to undo them.
 */
const NO_JS_GUARD = `document.documentElement.classList.remove('no-js')`

export default function Document() {
  return (
    <Html lang="en" className="no-js">
      <Head>
        <meta charSet="utf-8" />
        <link rel="icon" href="/images/logo.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;650;800;900&display=swap"
        />
        <script dangerouslySetInnerHTML={{ __html: NO_JS_GUARD }} />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
