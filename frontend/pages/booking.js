import Head from 'next/head'
import Link from 'next/link'
import { MessageCircle } from 'lucide-react'
import Layout from '../components/Layout'
import Reveal from '../components/Reveal'
import { clinic, approvalCopy } from '../lib/site'
import { policyLinks } from '../lib/policies'

export default function Request() {
  return (
    <Layout>
      <Head>
        <title>Request a consultation</title>
        <meta
          name="description"
          content={`Request an online homoeopathic consultation with ${clinic.doctor.name} at ${clinic.name}. The doctor reviews every request and assigns the time personally.`}
        />
      </Head>

      <section className="page-head">
        <div className="shell">
          <p className="eyebrow">Consultation request</p>
          <h1>Request a consultation.</h1>
        </div>
      </section>

      <section className="booking" style={{ paddingTop: 32 }}>
        <div className="shell booking-grid">
          <Reveal className="booking-copy">
            <p className="lead">
              All consultations are held online over {clinic.platform}. Contact
              {` ${clinic.doctor.name}`} on WhatsApp to discuss a consultation
              and agree a date and time personally.
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
                <strong>Scheduling</strong>
                <span>
                  {clinic.scheduling}. Please allow{' '}
                  {clinic.advanceNotice.toLowerCase()}.
                </span>
              </div>
              <div className="quick-action">
                <strong>Availability</strong>
                <span>{clinic.availability}</span>
              </div>
              <div className="quick-action">
                <strong>Consultation length</strong>
                <span>
                  {clinic.duration}. {clinic.platformNote}.
                </span>
              </div>
            </div>
          </Reveal>

          <Reveal className="booking-card">
            <p className="lead">{approvalCopy}</p>
            <nav className="policy-links" aria-label="Clinic policies">
              <p className="eyebrow">Before you request</p>
              <ul>
                {policyLinks.map((policy) => (
                  <li key={policy.href}>
                    <Link href={policy.href}>{policy.label}</Link>
                  </li>
                ))}
              </ul>
            </nav>
          </Reveal>
        </div>
      </section>
    </Layout>
  )
}
