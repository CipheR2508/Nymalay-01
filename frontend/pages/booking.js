import Head from 'next/head'
import Link from 'next/link'
import Layout from '../components/Layout'
import Reveal from '../components/Reveal'
import ConsultationRequestForm from '../components/ConsultationRequestForm'
import { clinic, approvalCopy } from '../lib/site'
import { feeSummary } from '../lib/consultationRequest'
import { policyLinks } from '../lib/policies'

export default function Request() {
  const fee = feeSummary()

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
              All consultations are held online over {clinic.platform}. Fill in
              your details below and choose how to send them. {clinic.doctor.name}{' '}
              will review your request and agree a date and time with you
              personally.
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

            <p className="form-note" style={{ marginTop: 24 }}>
              No WhatsApp? Write to{' '}
              <a
                href={`mailto:${clinic.email}`}
                style={{ textDecoration: 'underline' }}
              >
                {clinic.email}
              </a>{' '}
              with the same details. WhatsApp is the primary channel for
              confirmation and for any change to your slot.
            </p>
          </Reveal>

          <Reveal className="booking-card">
            <ConsultationRequestForm />

            <div className="fee-box">
              <div className="fee-row">
                <strong>Consultation fee</strong>
                <strong className="price">{fee.amount}</strong>
              </div>
              <p style={{ marginBottom: 12, fontSize: '0.9rem' }}>{fee.detail}</p>
              <p className="fee-note">{approvalCopy}</p>
            </div>

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
