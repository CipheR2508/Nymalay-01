import { describe, expect, it } from 'vitest'
import { directWhatsappUrl } from '../lib/contact'
import { clinic } from '../lib/site'

describe('directWhatsappUrl', () => {
  it('opens the clinic WhatsApp chat without a message', () => {
    expect(directWhatsappUrl()).toBe(clinic.whatsappUrl)
    expect(directWhatsappUrl()).toBe(`https://wa.me/${clinic.whatsappNumber}`)
    expect(new URL(directWhatsappUrl()).search).toBe('')
  })

  it('uses the E.164 form wa.me expects, without a plus sign', () => {
    expect(directWhatsappUrl()).toMatch(/^https:\/\/wa\.me\/\d{10,15}$/)
  })
})
