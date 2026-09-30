import Link from 'next/link'
import Reveal from '../Reveal'
import ConsultationRequestForm from '../ConsultationRequestForm'
import { clinic, approvalCopy } from '../../lib/site'
import { feeSummary } from '../../lib/consultationRequest'
import { policyLinks } from '../../lib/policies'

/**
 * The request section, shown on the homepage and on most inner pages.
 *
 * `id="request"` rather than `id="booking"`: the doctor assigns the slot, so
 * this is a request, not a booking. The section states the fee and the
 * approval requirement without ever presenting a payment button or a claim
 * that an appointment exists.
 */
export default function RequestSection() {
  const fee = feeSummary()

  return (
    <section className="booking" id="request">
      <div className="shell booking-grid">
        <Reveal className="booking-copy">
          <span className="eyebrow">Consultation request</span>
          <h2>Request a consultation.</h2>
          <p className="lead">
            All consultations are held online over {clinic.platform}. Fill in a
            few details and send them to {clinic.doctor.name}, who will review
            your request and arrange a date and time with you personally.
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
          </div>

          <div className="card-list" style={{ marginTop: 28, maxWidth: 560 }}>
            <div className="quick-action">
              <strong>Scheduling</strong>
              <span>
                {clinic.scheduling}. Please allow {clinic.advanceNotice.toLowerCase()}.
              </span>
            </div>
            <div className="quick-action">
              <strong>Consultation length</strong>
              <span>
                {clinic.duration}, varying by case complexity. {clinic.platformNote}.
              </span>
            </div>
          </div>
        </Reveal>

        <Reveal className="booking-card">
          <ConsultationRequestForm />

          
          {/* Policies are reachable from the form itself, not only the footer,
              because this is where a patient is actually deciding. */}
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
  )
}
