import Head from 'next/head'
import Link from 'next/link'
import Layout from '../components/Layout'
import Reveal from '../components/Reveal'
import { clinic } from '../lib/site'
import { policyLinks } from '../lib/policies'

export default function Contact() {
  return (
    <Layout>
      <Head>
        <title>Contact</title>
        <meta
          name="description"
          content={`Contact ${clinic.name} on WhatsApp or email to request an online homoeopathic consultation with ${clinic.doctor.name}.`}
        />
      </Head>

      <section className="page-head">
        <div className="shell">
          <p className="eyebrow">Contact</p>
          <h1>Get in touch.</h1>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="shell booking-grid">
          <Reveal className="booking-copy">
            <h2>WhatsApp is fastest.</h2>
            <p className="lead">
              {clinic.doctor.name} keeps the clinic’s patient conversations, so
              WhatsApp is the fastest way to reach a real person. Prefer to send
              a written request first? Fill in the consultation form and choose
              WhatsApp or email.
            </p>

            <div className="quick-actions">
              <a
                className="quick-action"
                href={clinic.whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <strong>Contact on WhatsApp</strong>
                <span>{clinic.whatsappDisplay}</span>
              </a>
              <a className="quick-action" href={`mailto:${clinic.email}`}>
                <strong>Email us</strong>
                <span>{clinic.email}</span>
              </a>
              <div className="quick-action">
                <strong>Availability</strong>
                <span>{clinic.availability}</span>
              </div>
              <div className="quick-action">
                <strong>Scheduling</strong>
                <span>
                  {clinic.scheduling}. Please allow{' '}
                  {clinic.advanceNotice.toLowerCase()}.
                </span>
              </div>
              <div className="quick-action">
                <strong>Where we are</strong>
                <span>{clinic.location}</span>
              </div>
            </div>

            <p className="form-note" style={{ marginTop: 24 }}>
              <Link href="/booking">Request a consultation</Link> and send your
              details either way. WhatsApp is the primary channel for confirming
              your appointment and for any change to your slot; email is used
              when WhatsApp is not available.
            </p>
          </Reveal>

          <Reveal className="booking-card">
            <h2 style={{ fontSize: '1.6rem', marginBottom: 8 }}>
              Requesting a consultation
            </h2>
            <p className="lead" style={{ fontSize: '1.02rem' }}>
              {clinic.doctor.name} reviews every request personally and assigns
              the date and time. Nothing is confirmed automatically.
            </p>

            <div className="hero-actions" style={{ marginTop: 24 }}>
              <Link className="btn btn-primary" href="/booking">
                Request a consultation
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

            <nav className="policy-links" aria-label="Clinic policies" style={{ marginTop: 28 }}>
              <p className="eyebrow">Policies</p>
              <ul>
                {policyLinks.map((policy) => (
                  <li key={policy.href}>
                    <Link href={policy.href}>{policy.label}</Link>
                  </li>
                ))}
              </ul>
            </nav>

            <div className="notice notice-info" style={{ marginTop: 24 }}>
              This is a complementary therapy and not a substitute for
              emergency or in-person medical care. If something is urgent, please
              contact a hospital or emergency service instead.
            </div>
          </Reveal>
        </div>
      </section>
    </Layout>
  )
}
