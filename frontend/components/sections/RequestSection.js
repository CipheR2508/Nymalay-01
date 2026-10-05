import Link from 'next/link'
import { MessageCircle } from 'lucide-react'
import Reveal from '../Reveal'
import { clinic } from '../../lib/site'
import { policyLinks } from '../../lib/policies'

/**
 * The request section, shown on the homepage and on most inner pages.
 *
 * `id="request"` rather than `id="booking"`: the doctor assigns the slot, so
 * this is a request, not a booking. The section never presents a payment
 * button or a claim that an appointment exists.
 */
export default function RequestSection() {
  return (
    <section className="booking" id="request">
      <div className="shell booking-grid">
        <Reveal className="booking-copy">
          <span className="eyebrow">Consultation request</span>
          <h2>Talk to the clinic.</h2>
          <p className="lead">
            All consultations are held online over {clinic.platform}. Contact
            {` ${clinic.doctor.name}`} directly on WhatsApp to discuss a
            consultation.
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
            <a className="btn btn-secondary" href={`mailto:${clinic.email}`}>
              Email the clinic
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
