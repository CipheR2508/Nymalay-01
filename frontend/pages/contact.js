import Head from 'next/head'
import Link from 'next/link'
import { MessageCircle } from 'lucide-react'
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
          content={`Contact ${clinic.name} on WhatsApp to request an online homoeopathic consultation with ${clinic.doctor.name}.`}
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
            <h2>Contact us on WhatsApp.</h2>
            <p className="lead">
              All clinic communication happens directly through WhatsApp. Send
              your question or consultation request there and {clinic.doctor.name}{' '}
              will reply personally.
            </p>

            <div className="quick-actions">
              <a
                className="btn btn-primary"
                href={clinic.whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <MessageCircle aria-hidden="true" /> Contact on WhatsApp
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
          </Reveal>

          <Reveal className="booking-card">
            <h2 style={{ fontSize: '1.6rem', marginBottom: 8 }}>
              Discuss a consultation
            </h2>
            <p className="lead" style={{ fontSize: '1.02rem' }}>
              {clinic.doctor.name} reviews every request personally and assigns
              the date and time. Nothing is confirmed automatically.
            </p>

            <div className="hero-actions" style={{ marginTop: 24 }}>
              <a
                className="btn btn-primary"
                href={clinic.whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <MessageCircle aria-hidden="true" /> Contact on WhatsApp
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
