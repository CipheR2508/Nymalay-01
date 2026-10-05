import Head from 'next/head'
import Layout from '../components/Layout'
import TestimonialSection from '../components/sections/TestimonialSection'
import RequestSection from '../components/sections/RequestSection'
import { clinic } from '../lib/site'

export default function Testimonials() {
  return (
    <Layout>
      <Head>
        <title>Testimonials</title>
        <meta
          name="description"
          content="What patients say about consultations at Nymalay Homoeopathy."
        />
      </Head>

      <section className="page-head">
        <div className="shell">
          <p className="eyebrow">Testimonials</p>
          <h1>In their words.</h1>
        </div>
      </section>

      <TestimonialSection />

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="shell">
          <div className="section-head">
            <div>
              <span className="eyebrow">A note on these</span>
              <h2>What these are, and are not.</h2>
            </div>
            <div className="copy">
              <p className="lead">
                Individual results vary, and homoeopathy is a complementary
                therapy. Nothing here is a promise of an outcome.
              </p>
            </div>
          </div>

          <div className="card-list" style={{ maxWidth: 760 }}>
            <div className="quick-action">
              <strong>Attribution</strong>
              <span>
                These accounts are shared with patients’ permission. Full names
                are withheld, and quotes are lightly edited for length only.
              </span>
            </div>
            <div className="quick-action">
              <strong>Ask us directly</strong>
              <span>
                Questions about whether homoeopathy suits your situation are
                welcome — message {clinic.shortName} on{' '}
                <a href={clinic.whatsappUrl} target="_blank" rel="noopener noreferrer">
                  WhatsApp
                </a>
                .
              </span>
            </div>
          </div>
        </div>
      </section>

      <RequestSection />
    </Layout>
  )
}
