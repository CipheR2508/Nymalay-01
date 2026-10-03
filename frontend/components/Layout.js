import Header from './Header'
import Footer from './Footer'

/** Every page renders inside this so chrome is never forgotten or doubled. */
export default function Layout({ children }) {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <Header />
      <main id="main">{children}</main>
      <Footer />
    </>
  )
}
