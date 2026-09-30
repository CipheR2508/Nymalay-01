import { useRef, useState } from 'react'
import { ArrowRight, Mail, MessageCircle } from 'lucide-react'
import {
  EMAIL_HELPER,
  REQUEST_FIELDS,
  WHATSAPP_HELPER,
  formatPlainSummary,
  validateRequest,
} from '../lib/consultationRequest'
import {
  emailHandoffUrl,
  plainEmailUrl,
  whatsappHandoffUrl,
} from '../lib/contact'
import { clinic, privacyNote } from '../lib/site'

/**
 * The consultation request form.
 *
 * This form does not book anything. It validates six fields and then hands the
 * patient's own text to a contact channel they choose, so the clinic receives
 * it through WhatsApp or email. Deliberately absent:
 *
 *   - no API call and no database write, because the website cannot approve a
 *     request and must not appear to;
 *   - no date or time field, because the doctor assigns the slot personally;
 *   - any "Request received" style confirmation, because opening a draft does
 *     not prove anything was sent;
 *   - any persistence, local or otherwise. Values live in React state for this
 *     page view and are gone on navigation, which is the privacy-correct
 *     behaviour for health details.
 *
 * The form deliberately does not clear after a handoff, so a patient who
 * declines the WhatsApp prompt still has everything typed out to copy.
 */
export default function ConsultationRequestForm({ initialChannel = 'whatsapp' }) {
  const [values, setValues] = useState(() => blank())
  const [errors, setErrors] = useState({})
  const [draft, setDraft] = useState(null)
  const formRef = useRef(null)
  // A ref, not state: the click that records the channel happens in the same
  // tick as the submit, so state would still hold the previous value.
  const clickedChannel = useRef(initialChannel)

  function blank() {
    return REQUEST_FIELDS.reduce((seed, field) => ({ ...seed, [field.name]: '' }), {})
  }

  function update(event) {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
    setErrors((current) => (current[name] ? { ...current, [name]: undefined } : current))
  }

  /**
   * Validate, then hand off. The draft is stored in state rather than
   * navigating, so the rendered fallback can offer both channels and a
   * copyable version without the patient re-typing anything.
   */
  function submitTo(event) {
    event.preventDefault()
    // SubmitEvent.submitter is recent; the ref is the fallback for browsers
    // that do not expose it. Pressing Enter in a field submits with the first
    // button, and the ref holds the default channel, which is that same button.
    const chosen = event.nativeEvent.submitter?.value ?? clickedChannel.current

    const result = validateRequest(values, { channel: chosen })

    if (!result.ok) {
      setErrors(result.errors)
      // Move focus to the first problem so keyboard and screen-reader users
      // are not left guessing why nothing happened.
      const first = REQUEST_FIELDS.find((field) => result.errors[field.name])
      if (first) formRef.current?.querySelector(`#${first.name}`)?.focus()
      return
    }

    setErrors({})
    setDraft({ request: result.value, channel: chosen })
  }

  const whatsappUrl = draft ? whatsappHandoffUrl(draft.request) : null
  const emailUrl = draft ? emailHandoffUrl(draft.request) : null

  if (draft) {
    return (
      <div className="notice notice-info" role="status">
        <h2 className="handoff-heading">Your request is ready to send</h2>
        <p>
          {draft.channel === 'email' ? EMAIL_HELPER : WHATSAPP_HELPER}
        </p>
        <div className="hero-actions">
          {draft.channel === 'email' ? (
            <a
              className="btn btn-primary"
              href={emailUrl}
              // A mailto: draft opens the patient's mail app, not a new tab.
            >
              <Mail aria-hidden="true" /> Open your email application
            </a>
          ) : (
            <a
              className="btn btn-primary"
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageCircle aria-hidden="true" /> Open WhatsApp
            </a>
          )}

          {/* The other channel stays one click away, for a patient who picked
              the wrong one or has no WhatsApp. */}
          {draft.channel === 'email' ? (
            <a
              className="btn btn-secondary"
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageCircle aria-hidden="true" /> Use WhatsApp instead
            </a>
          ) : (
            <a
              className="btn btn-secondary"
              href={emailUrl}
            >
              <Mail aria-hidden="true" /> Email instead
            </a>
          )}

          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setDraft(null)}
          >
            Edit my details
          </button>
        </div>

        {/* Fallback for a device with no WhatsApp and no mail app configured. */}
        <div className="handoff-fallback">
          <p className="form-note">
            Neither app opened? Send this to{' '}
            <a href={plainEmailUrl()}>{clinic.email}</a> from any email
            account, or message{' '}
            <a
              href={clinic.whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              {clinic.whatsappDisplay}
            </a>{' '}
            on WhatsApp.
          </p>
          <pre className="handoff-preview">{formatPlainSummary(draft.request)}</pre>
          <p className="form-note">{privacyNote}</p>
        </div>
      </div>
    )
  }

  return (
    // method="post" is deliberate. Without JavaScript the submit is blocked
    // anyway, and a GET would put a health complaint, name and phone number
    // into the address bar, the browser history and any referrer header. A POST
    // to the same URL keeps them out of the URL.
    <form onSubmit={submitTo} method="post" noValidate ref={formRef}>
      <div className="form-grid">
        {REQUEST_FIELDS.map((field) => (
          <div className={`field${field.full ? ' full' : ''}`} key={field.name}>
            <label htmlFor={field.name}>
              {field.label}
              {field.required ? null : (
                <span className="field-optional"> optional</span>
              )}
            </label>

            {field.type === 'textarea' ? (
              <textarea
                id={field.name}
                name={field.name}
                value={values[field.name]}
                onChange={update}
                required={field.required}
                maxLength={field.maxLength}
                placeholder={field.placeholder}
                aria-invalid={Boolean(errors[field.name])}
                aria-describedby={
                  errors[field.name] ? `${field.name}-error` : undefined
                }
              />
            ) : (
              <input
                id={field.name}
                name={field.name}
                type={field.type}
                inputMode={field.inputMode}
                autoComplete={field.autoComplete}
                value={values[field.name]}
                onChange={update}
                required={field.required}
                maxLength={field.maxLength}
                placeholder={field.placeholder}
                aria-invalid={Boolean(errors[field.name])}
                aria-describedby={
                  errors[field.name] ? `${field.name}-error` : undefined
                }
              />
            )}

            {errors[field.name] ? (
              <span className="field-error" id={`${field.name}-error`}>
                {errors[field.name]}
              </span>
            ) : null}
          </div>
        ))}
      </div>

      {/*
        A submit button per channel, each carrying its own `value`, so one form
        can validate differently for the email path. The click handler is the
        fallback for browsers without SubmitEvent.submitter.
      */}
      <div className="hero-actions form-submit">
        <button
          className="btn btn-primary"
          type="submit"
          name="channel"
          value="whatsapp"
          onClick={() => {
            clickedChannel.current = 'whatsapp'
          }}
        >
          Continue to WhatsApp <ArrowRight aria-hidden="true" />
        </button>
        <button
          className="btn btn-secondary"
          type="submit"
          name="channel"
          value="email"
          onClick={() => {
            clickedChannel.current = 'email'
          }}
        >
          <Mail aria-hidden="true" /> Email instead
        </button>
      </div>

      <p className="form-note">{WHATSAPP_HELPER}</p>
      <p className="form-note">{clinic.approvalNote}.</p>
      <p className="form-note">{privacyNote}</p>
    </form>
  )
}
