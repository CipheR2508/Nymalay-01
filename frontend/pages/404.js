import Head from 'next/head'
import Link from 'next/link'
import Layout from '../components/Layout'
import { clinic } from '../lib/site'

export default function NotFound() {
  return (
    <Layout>
      <Head>
        <title>Page not found</title>
      </Head>

      <section className="section" style={{ paddingTop: 120 }}>
        <div className="shell" style={{ textAlign: 'center' }}>
          <p className="eyebrow" style={{ justifyContent: 'center' }}>
            404
          </p>
          <h1 style={{ margin: '18px auto 24px' }}>
            We couldn’t find that page.
          </h1>
          <p className="lead" style={{ margin: '0 auto 40px' }}>
            It may have moved. Head back to the homepage, or message{' '}
            {clinic.shortName} directly and we’ll point you the right way.
          </p>
          <div className="hero-actions" style={{ justifyContent: 'center' }}>
            <Link className="btn btn-primary" href="/">
              Back to home
            </Link>
            <a
              className="btn btn-secondary"
              href={clinic.whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              Contact on WhatsApp
            </a>
          </div>
        </div>
      </section>
    </Layout>
  )
}
