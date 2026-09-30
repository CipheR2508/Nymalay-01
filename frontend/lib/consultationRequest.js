/*
 * The consultation request: shape, validation, and message formatting.
 *
 * Deliberately independent of WhatsApp, of the email draft, and of any API.
 * A validated request is a plain object, so the channel that carries it is a
 * separate concern and a future direct-booking API can accept the same object
 * without this module changing.
 *
 * Nothing here talks to a network, and nothing here stores anything. The
 * request exists in page memory for the length of one interaction: no
 * localStorage, no sessionStorage, no cookies, no database, no URL parameters.
 * The website must not be able to create an appointment, reserve a slot, or
 * claim a request was received, because it cannot know any of that.
 */

import { clinic } from './site'

export const NOT_PROVIDED = 'Not provided'

/**
 * Field definitions drive the form, the validation order and the labels, so
 * adding a field means editing one list rather than three places.
 *
 * `required` is false for Email and Occupation: the WhatsApp path works fine
 * without them, and demanding an address the clinic may not use is the most
 * common reason a health form gets abandoned halfway. Email is instead required
 * when the patient chooses the email channel, since a draft with no reply
 * address is not deliverable.
 */
export const REQUEST_FIELDS = [
  {
    name: 'name',
    label: 'Full name',
    type: 'text',
    autoComplete: 'name',
    required: true,
    maxLength: 120,
    placeholder: 'Your full name',
  },
  {
    name: 'age',
    label: 'Age',
    type: 'text',
    inputMode: 'numeric',
    autoComplete: 'off',
    required: true,
    maxLength: 5,
    placeholder: 'Years',
  },
  {
    name: 'phone',
    label: 'Phone number',
    type: 'tel',
    autoComplete: 'tel',
    required: true,
    maxLength: 24,
    placeholder: 'Include your country code if outside India',
  },
  {
    name: 'email',
    label: 'Email',
    type: 'email',
    autoComplete: 'email',
    required: false,
    maxLength: 160,
    placeholder: 'you@example.com',
  },
  {
    name: 'occupation',
    label: 'Occupation',
    type: 'text',
    autoComplete: 'organization-title',
    required: false,
    maxLength: 80,
    placeholder: 'What do you do?',
  },
  {
    name: 'concern',
    label: 'Brief description of your health concern',
    type: 'textarea',
    required: true,
    maxLength: 1000,
    full: true,
    placeholder:
      'A sentence or two is plenty. Please keep it brief — the doctor will take the full history during the consultation.',
  },
]

export const EMPTY_REQUEST = Object.freeze(
  REQUEST_FIELDS.reduce((seed, field) => ({ ...seed, [field.name]: '' }), {}),
)

/**
 * Loose but deliberate: an international number may be written `+91 98765 43210`,
 * `0091-98765-43210` or `(020) 7946 0000`, and rejecting valid formats would lose
 * real patients. The length window rejects typos without guessing at country
 * codes, which the site has no verified list of.
 *
 * The first character may be a digit or an opening bracket, so a bracketed area
 * code is not mistaken for garbage. The rest is digits and the separators people
 * actually type. Seven digits is the shortest plausible subscriber number, and
 * is checked separately because separators alone would otherwise pass the
 * length window: `()----()` is long enough but contains no number.
 */
const PHONE_PATTERN = /^\+?[\d(][\d\s().-]{5,23}$/
const MIN_PHONE_DIGITS = 7

/**
 * Intentionally permissive. The only real test of an address is delivering to
 * it, and this site sends nothing server-side. Over-strict patterns reject
 * valid addresses more often than they catch typos.
 */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

/** Upper bound on age. 122 is the oldest verified human, so this catches typos. */
const MAX_AGE = 122

/**
 * Validate and normalise a request.
 *
 * `channel` matters because the same email field is optional on WhatsApp and
 * required for email. Returns the trimmed request on success, or a map of
 * field name to message on failure, which is shaped for direct use as
 * `aria-describedby` targets.
 *
 * Never throws, never logs, never persists.
 */
export function validateRequest(values, { channel = 'whatsapp' } = {}) {
  const clean = {}
  const errors = {}

  for (const field of REQUEST_FIELDS) {
    const raw = values?.[field.name] ?? ''
    // Collapse internal runs of whitespace: it makes no difference to the
    // clinic and keeps the generated message tidy.
    clean[field.name] = String(raw).replace(/\s+/g, ' ').trim()
  }

  // The concern is prose, so only trim its edges rather than reflowing it.
  clean.concern = String(values?.concern ?? '').trim()

  if (clean.name.length < 2) {
    errors.name = 'Please enter your name.'
  } else if (clean.name.length > REQUEST_FIELDS[0].maxLength) {
    errors.name = 'That name is unusually long. Please shorten it.'
  }

  const ageError = validateAge(clean.age)
  if (ageError) errors.age = ageError

  if (!clean.phone) {
    errors.phone = 'Enter a phone number we can reach you on.'
  } else if (!isUsablePhone(clean.phone)) {
    errors.phone = 'That does not look like a phone number.'
  }

  if (channel === 'email' && !clean.email) {
    errors.email = 'An email address is needed for the email option.'
  } else if (clean.email && !EMAIL_PATTERN.test(clean.email)) {
    errors.email = 'That does not look like an email address.'
  }

  if (clean.concern.length < 10) {
    errors.concern = 'A sentence or two helps the doctor prepare.'
  } else if (clean.concern.length > 1000) {
    errors.concern = 'Please keep this brief — 1000 characters is the limit.'
  }

  if (Object.keys(errors).length > 0) return { ok: false, errors }

  return { ok: true, value: clean, errors: {} }
}

/**
 * A phone number is only checked for shape. Nothing here can tell whether the
 * number is reachable, and guessing at country codes would reject valid numbers,
 * so the rule is: plausible characters, and enough of them to be a number.
 */
function isUsablePhone(value) {
  if (!PHONE_PATTERN.test(value)) return false
  return value.replace(/\D/g, '').length >= MIN_PHONE_DIGITS
}

/**
 * Age is validated as a number, not constrained to adults.
 * Infants and children are legitimate homoeopathy patients, so a minimum age
 * would exclude real patients on an assumption rather than a clinical one.
 * Zero is allowed and is how a guardian would express an infant; the upper
 * bound only exists to catch a mistyped year.
 */
function validateAge(value) {
  if (!value) return 'Please enter an age.'

  // Accept "7", "7 years", "7yo", "1.5" — parents write all of these.
  const match = String(value)
    .trim()
    .match(/^(\d{1,3}(?:\.\d{1,2})?)\s*(?:years?|yrs?|yo)?$/i)
  if (!match) return 'Enter an age in years, for example 34.'

  const age = Number(match[1])
  if (!Number.isFinite(age) || age < 0) return 'Age cannot be negative.'
  if (age > MAX_AGE) return 'Please check the age — that does not look right.'
  return null
}

/** The exact message body shared by the WhatsApp and email channels. */
export const MESSAGE_SUBJECT = 'Consultation request — Nymalay Homoeopathic Clinic'

/**
 * Format a validated request into the message the patient will send.
 *
 * One formatter for both channels on purpose: the clinic should not receive a
 * materially different account of the same request depending on which channel
 * the patient picked. Optional fields state "Not provided" rather than being
 * omitted, so the recipient can tell a blank field from a missed one.
 */
export function formatRequestMessage(request) {
  return [
    MESSAGE_SUBJECT,
    '',
    `Name: ${request.name}`,
    `Age: ${request.age}`,
    `Phone: ${request.phone}`,
    `Email: ${request.email || NOT_PROVIDED}`,
    `Occupation: ${request.occupation || NOT_PROVIDED}`,
    '',
    'Health concern:',
    request.concern,
    '',
    'Please review my request and let me know a suitable consultation date and time.',
  ].join('\n')
}

/** A short plain-text summary, used for the copyable fallback. */
export function formatPlainSummary(request) {
  return [
    `${request.name}, age ${request.age}`,
    `Phone: ${request.phone}`,
    request.email ? `Email: ${request.email}` : null,
    request.occupation ? `Occupation: ${request.occupation}` : null,
    '',
    request.concern,
  ]
    .filter((line) => line !== null)
    .join('\n')
}

/** Shown next to the WhatsApp action. Deliberately not a confirmation. */
export const WHATSAPP_HELPER =
  'WhatsApp will open with your consultation request. Press Send to share it with the clinic. Your appointment requires the doctor’s approval.'

/** Shown next to the email action. */
export const EMAIL_HELPER =
  'Your email application will open with the request. Press Send there to deliver it to the clinic. Your appointment requires the doctor’s approval.'

/** Fee wording. The one-time scope beyond this consultation is not specified. */
export function feeSummary() {
  const fee = `₹${clinic.consultationFeeInr.toLocaleString('en-IN')}`
  return {
    amount: fee,
    line: `${fee} one-time consultation fee`,
    detail:
      'Medicine and courier charges are separate and communicated according to your case.',
  }
}
