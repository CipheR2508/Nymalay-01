import Link from 'next/link'
import { MessageCircle } from 'lucide-react'
import { clinic } from '../lib/site'

/**
 * Fixed WhatsApp + request dock. CSS shows it at 680px and below only.
 *
 * Label is "Contact on WhatsApp" rather than a bare "WhatsApp", because that is
 * what the link does: it opens a chat, and it does not send anything.
 */
export default function MobileBar() {
  return (
    <div className="mobile-bar" aria-label="Quick contact actions">
      <a
        className="btn btn-secondary"
        href={clinic.whatsappUrl}
        target="_blank"
        rel="noopener noreferrer"
      >
        <MessageCircle aria-hidden="true" /> WhatsApp
      </a>
      <Link className="btn btn-primary" href="/booking">
        Request
      </Link>
    </div>
  )
}
