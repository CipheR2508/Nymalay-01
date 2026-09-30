import Head from 'next/head'
import Link from 'next/link'
import Layout from '../components/Layout'
import Reveal from '../components/Reveal'
import { clinic } from '../lib/site'

export default function About() {
  return (
    <Layout>
      <Head>
        <title>About</title>
      </Head>

      <section className="page-head">
        <div className="shell">
          <Reveal as="p" className="eyebrow">
            About the clinic
          </Reveal>
          <Reveal as="h1">
            Individualised care, built around a real case history.
          </Reveal>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="shell">
          <Reveal className="prose-clinic" style={{ maxWidth: 760 }}>
            <p>
              {clinic.name} provides individualised online homoeopathic
              consultations with {clinic.doctor.name}, offering personalised care
              that addresses the root cause of health concerns rather than just
              treating symptoms.
            </p>
            <p>
              Our approach combines traditional homoeopathic principles with
              modern telemedicine technology to bring quality healthcare to your
              doorstep.
            </p>
            <p>
              A first consultation is intentionally long. History, temperament
              and pattern matter as much as the presenting complaint, so the
              prescription follows the person rather than the diagnosis.
            </p>
          </Reveal>

          <Reveal className="card-list" style={{ marginTop: 48, maxWidth: 760 }}>
            <div className="quick-action">
              <strong>Meet {clinic.doctor.name}</strong>
              <span>{clinic.doctor.credentials}</span>
            </div>
            <div className="quick-action">
              <strong>What we treat</strong>
              <span>Chronic and everyday conditions, case by case.</span>
            </div>
            <div className="quick-action">
              <strong>How it works</strong>
              <span>
                Online over {clinic.platform}, {clinic.availability.toLowerCase()}.
                The doctor assigns the date and time personally.
              </span>
            </div>
          </Reveal>

          <Reveal className="hero-actions" style={{ marginTop: 40 }}>
            <Link className="btn btn-primary" href="/booking">
              Request a consultation
            </Link>
            <Link className="btn btn-secondary" href="/services">
              Our approach
            </Link>
          </Reveal>
        </div>
      </section>
    </Layout>
  )
}
