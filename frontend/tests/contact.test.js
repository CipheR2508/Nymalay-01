import { describe, expect, it } from 'vitest'
import {
  canUseEmail,
  directWhatsappUrl,
  emailHandoffUrl,
  plainEmailUrl,
  whatsappHandoffUrl,
} from '../lib/contact'
import { validateRequest } from '../lib/consultationRequest'
import { clinic } from '../lib/site'

/**
 * A request whose text deliberately contains characters that break naive URL
 * building: a space, a newline, an ampersand, a question mark, a plus sign, a
 * hash and a quote.
 */
const request = validateRequest({
  name: 'Meera Rao',
  age: '34',
  phone: '+91 98765 43210',
  email: 'meera.rao@example.com',
  occupation: 'Teacher',
  concern:
    'Acidity & reflux since March. Worse after meals; wakes me at 3am.\n' +
    'Taking "Omeprazole" 10mg — how long until I can stop? #acid',
}).value

describe('directWhatsappUrl', () => {
  it('is the clinic number with no prefilled text', () => {
    expect(directWhatsappUrl()).toBe(clinic.whatsappUrl)
    expect(directWhatsappUrl()).not.toContain('?text=')
  })

  it('is the E.164 form wa.me expects, without a plus sign', () => {
    expect(directWhatsappUrl()).toMatch(/^https:\/\/wa\.me\/\d{10,15}$/)
  })
})

describe('whatsappHandoffUrl', () => {
  const url = whatsappHandoffUrl(request)

  it('targets the clinic number', () => {
    expect(url.startsWith(`${clinic.whatsappUrl}?text=`)).toBe(true)
  })

  it('carries the full request, correctly encoded', () => {
    const text = decodeURIComponent(url.split('?text=')[1])

    expect(text).toContain('Name: Meera Rao')
    expect(text).toContain(request.concern)
  })

  it('encodes characters that would otherwise truncate the link', () => {
    // An unencoded space, # or & would cut the message short or add a fragment.
    expect(url).not.toMatch(/[ #]/)
    expect(url).not.toContain('&')
  })

  it('encodes newlines as %0A, which WhatsApp renders as line breaks', () => {
    expect(url).toContain('%0A')
    expect(url).not.toMatch(/\n/)
  })

  it('is a valid absolute URL', () => {
    expect(() => new URL(url)).not.toThrow()
    expect(new URL(url).searchParams.get('text')).toContain('Name: Meera Rao')
  })

  it('is a handoff, not a send: it only ever opens a draft', () => {
    // There is no API key and no send endpoint here by design.
    expect(url).not.toContain('send')
    expect(url).not.toContain('token')
  })
})

describe('emailHandoffUrl', () => {
  const url = emailHandoffUrl(request)

  it('is a mailto addressed to the clinic', () => {
    expect(url.startsWith(`mailto:${encodeURIComponent(clinic.email)}?`)).toBe(true)
  })

  it('is not double-encoded', () => {
    // Re-encoding the whole href would deliver a wall of %20 to the patient.
    expect(url).not.toContain('%2520')
    expect(url).not.toContain('%25')
  })

  it('keeps the body from injecting extra mail parameters', () => {
    // The body is user-supplied. An unescaped & would let it add &cc= or
    // &bcc= to the patient's own draft.
    const [, query] = url.split('?')
    const [subject, body] = query.split('&body=')

    expect(subject).toMatch(/^subject=/)
    expect(body).not.toMatch(/&(cc|bcc)=/)
  })

  it('round-trips through a URL parser to the original body', () => {
    const parsed = new URL(url)

    expect(parsed.searchParams.get('body')).toContain(request.concern)
    expect(parsed.searchParams.get('subject')).toBeTruthy()
  })
})

describe('plainEmailUrl', () => {
  it('is a bare mailto with no draft', () => {
    expect(plainEmailUrl()).toBe(`mailto:${clinic.email}`)
    expect(plainEmailUrl()).not.toContain('?')
  })
})

describe('canUseEmail', () => {
  it.each([
    ['meera.rao@example.com', true],
    ['a@b.co', true],
    ['meera at example.com', false],
    ['', false],
    [undefined, false],
  ])('%s -> %s', (email, expected) => {
    expect(canUseEmail({ email })).toBe(expected)
  })
})
