/*
 * Contact-channel handoff.
 *
 * One module owns every outbound contact URL, so the WhatsApp number and the
 * email address can never disagree between the form, the footer and the
 * contact page. It is pure string building: no network, no storage, no
 * appointment state.
 *
 * Both channels open a *draft*. Neither delivers anything. The patient must
 * press Send in WhatsApp or in their email application, and the site has no
 * way to know whether they did. So nothing downstream may say a request was
 * received — see the acknowledgement wording in `site.js`.
 */

import { clinic, whatsappLink } from './site'
import { MESSAGE_SUBJECT, formatRequestMessage } from './consultationRequest'

/** The clinic's WhatsApp chat, with no prefilled text. */
export function directWhatsappUrl() {
  return clinic.whatsappUrl
}

/** The WhatsApp chat with a consultation request already typed out. */
export function whatsappHandoffUrl(request) {
  return whatsappLink(formatRequestMessage(request))
}

/**
 * A `mailto:` draft addressed to the clinic.
 *
 * Two encodings matter here. `encodeURIComponent` is right for the subject and
 * body because it percent-encodes newlines as %0A, which every mail client
 * renders as a line break. It also encodes `&` and `=`, so the body cannot
 * inject extra parameters such as `&cc=` or `&bcc=` into the URL — which
 * matters here, since the body contains user-supplied text.
 *
 * The whole href is then not re-encoded, because that would double-encode the
 * percent signs and deliver a wall of `%20` to the patient.
 */
export function emailHandoffUrl(request) {
  const body = formatRequestMessage(request)
  return (
    `mailto:${encodeURIComponent(clinic.email)}` +
    `?subject=${encodeURIComponent(MESSAGE_SUBJECT)}` +
    `&body=${encodeURIComponent(body)}`
  )
}

/** A plain `mailto:` with no draft, for general contact links. */
export function plainEmailUrl() {
  return `mailto:${clinic.email}`
}

/**
 * Whether the patient has a usable email address.
 *
 * Only ever true for a syntactically valid address; whether the mailbox
 * exists is not knowable from here. Used to decide if the email action is
 * worth offering, not to promise delivery.
 */
export function canUseEmail(request) {
  return Boolean(request?.email) && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(request.email)
}
