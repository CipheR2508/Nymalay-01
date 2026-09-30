import { describe, expect, it } from 'vitest'
import {
  MESSAGE_SUBJECT,
  NOT_PROVIDED,
  REQUEST_FIELDS,
  formatPlainSummary,
  formatRequestMessage,
  validateRequest,
} from '../lib/consultationRequest'

/**
 * A complete, valid request. Individual tests override one field at a time so
 * a failure points at the field that caused it rather than at "the form".
 */
function valid(overrides = {}) {
  return {
    name: 'Meera Rao',
    age: '34',
    phone: '+91 98765 43210',
    email: 'meera.rao@example.com',
    occupation: 'Teacher',
    concern: 'Recurring acidity for the past six months, worse after meals.',
    ...overrides,
  }
}

describe('validateRequest', () => {
  it('accepts a complete request', () => {
    const result = validateRequest(valid())

    expect(result.ok).toBe(true)
    expect(result.errors).toEqual({})
    expect(result.value.name).toBe('Meera Rao')
  })

  it('collapses internal whitespace but leaves the concern as prose', () => {
    const result = validateRequest(
      valid({
        name: '  Meera   Rao  ',
        concern: '  Recurring acidity.\n\nWorse after meals.  ',
      }),
    )

    expect(result.value.name).toBe('Meera Rao')
    // Line breaks carry meaning in a symptom description, so they survive.
    expect(result.value.concern).toBe('Recurring acidity.\n\nWorse after meals.')
  })

  it.each([
    ['name', { name: '' }],
    ['name', { name: 'A' }],
    ['phone', { phone: '' }],
    ['phone', { phone: '12345' }],
    ['phone', { phone: 'not-a-phone' }],
    ['age', { age: '' }],
    ['concern', { concern: '' }],
    ['concern', { concern: 'short' }],
  ])('rejects an invalid %s', (field, overrides) => {
    const result = validateRequest(valid(overrides))

    expect(result.ok).toBe(false)
    expect(result.errors[field]).toBeTruthy()
  })

  it('returns errors keyed by field name, for aria-describedby', () => {
    const result = validateRequest(valid({ name: '', phone: '' }))

    expect(Object.keys(result.errors).sort()).toEqual(['name', 'phone'])
  })

  describe('age', () => {
    it.each(['0', '7', '1.5', '34', '7 years', '7yrs', '7yo', '122'])(
      'accepts %s',
      (age) => {
        expect(validateRequest(valid({ age })).ok).toBe(true)
      },
    )

    it.each(['-1', '123', 'abc', '1000'])('rejects %s', (age) => {
      const result = validateRequest(valid({ age }))

      expect(result.ok).toBe(false)
      expect(result.errors.age).toBeTruthy()
    })

    it('accepts an infant, because children are legitimate patients', () => {
      // A minimum age would exclude real patients on an assumption.
      expect(validateRequest(valid({ age: '0' })).ok).toBe(true)
    })
  })

  describe('phone', () => {
    it.each(['9876543210', '+91 98765 43210', '0091-98765-43210', '(020) 7946 0000'])(
      'accepts %s',
      (phone) => {
        expect(validateRequest(valid({ phone })).ok).toBe(true)
      },
    )
  })

  describe('optional fields', () => {
    it('accepts a WhatsApp request with no email or occupation', () => {
      const result = validateRequest(
        valid({ email: '', occupation: '' }),
        { channel: 'whatsapp' },
      )

      expect(result.ok).toBe(true)
    })

    it('requires an email for the email channel', () => {
      const result = validateRequest(valid({ email: '' }), { channel: 'email' })

      expect(result.ok).toBe(false)
      expect(result.errors.email).toBeTruthy()
    })

    it('still checks a malformed email that was volunteered', () => {
      const result = validateRequest(valid({ email: 'meera at example.com' }))

      expect(result.ok).toBe(false)
      expect(result.errors.email).toBeTruthy()
    })

    it('does not require an occupation on either channel', () => {
      expect(validateRequest(valid({ occupation: '' }), { channel: 'email' }).ok).toBe(
        true,
      )
    })
  })

  it('never throws on missing input', () => {
    expect(() => validateRequest({})).not.toThrow()
    expect(validateRequest({}).ok).toBe(false)
    expect(validateRequest(undefined).ok).toBe(false)
  })

  it('exposes exactly the six fields the plan specifies, and no date', () => {
    expect(REQUEST_FIELDS.map((field) => field.name)).toEqual([
      'name',
      'age',
      'phone',
      'email',
      'occupation',
      'concern',
    ])
  })

  it('has no field of a type that would collect a date or time', () => {
    const types = REQUEST_FIELDS.map((field) => field.type)

    expect(types).not.toContain('date')
    expect(types).not.toContain('time')
    expect(types).not.toContain('datetime-local')
  })
})

describe('formatRequestMessage', () => {
  const request = validateRequest(valid()).value

  it('carries every field the patient entered', () => {
    const message = formatRequestMessage(request)

    expect(message).toContain('Name: Meera Rao')
    expect(message).toContain('Age: 34')
    expect(message).toContain('Phone: +91 98765 43210')
    expect(message).toContain('Email: meera.rao@example.com')
    expect(message).toContain('Occupation: Teacher')
    expect(message).toContain(request.concern)
  })

  it('asks for a date and time rather than proposing one', () => {
    // The doctor assigns the slot, so the message requests it.
    expect(formatRequestMessage(request)).toMatch(/date and time/i)
  })

  it('states a blank optional field explicitly, so it reads as omitted', () => {
    const message = formatRequestMessage(
      validateRequest(valid({ occupation: '' })).value,
    )

    expect(message).toContain(`Occupation: ${NOT_PROVIDED}`)
  })

  it('is the same message body on both channels', () => {
    // The clinic should not receive a materially different account depending on
    // which channel the patient picked.
    const viaEmail = validateRequest(valid(), { channel: 'email' }).value

    expect(formatRequestMessage(request)).toBe(formatRequestMessage(viaEmail))
  })
})

describe('formatPlainSummary', () => {
  it('omits absent optional lines rather than printing empty ones', () => {
    const request = validateRequest(valid({ occupation: '' })).value
    const summary = formatPlainSummary(request)

    expect(summary).not.toContain('Occupation:')
    expect(summary).toContain('Email: meera.rao@example.com')
  })

  it('includes the concern, which is the part the doctor reads first', () => {
    const request = validateRequest(valid()).value

    expect(formatPlainSummary(request)).toContain(request.concern)
  })
})

describe('MESSAGE_SUBJECT', () => {
  it('is the first line of the body, so it reads as a title in both channels', () => {
    const request = validateRequest(valid()).value

    expect(formatRequestMessage(request).split('\n')[0]).toBe(MESSAGE_SUBJECT)
  })
})
