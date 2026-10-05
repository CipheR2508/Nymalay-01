import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { directWhatsappUrl } from '../lib/contact'
import { policies, policyLinks } from '../lib/policies'
import { clinic } from '../lib/site'

/*
 * Source-level guarantees about the public bundle.
 *
 * The public site is a landing page: it must make no API call, collect no date,
 * take no payment and show no confirmation. Those are properties of the whole
 * tree rather than of any one module, and none of them fails a unit test on its
 * own — a stray `type="date"` or a re-imported legacy module would build, lint
 * and deploy cleanly. So they are asserted by reading the shipped source.
 */

const root = fileURLToPath(new URL('..', import.meta.url))
const PUBLIC_DIRS = ['pages', 'components', 'lib', 'styles']

/** Every file the public site can actually ship, excluding archived work. */
function publicSourceFiles(dir = root) {
  const found = []
  for (const entry of readdirSync(dir)) {
    if (entry === 'node_modules' || entry === '.next' || entry === '_inactive') {
      continue
    }
    const full = join(dir, entry)
    if (statSync(full).isDirectory()) {
      if (PUBLIC_DIRS.includes(entry) || dir !== root) {
        found.push(...publicSourceFiles(full))
      }
      continue
    }
    if (/\.(js|css|json)$/.test(entry)) found.push(full)
  }
  return found
}

const files = publicSourceFiles()

function readAll(paths) {
  return paths.map((path) => ({
    path: relative(root, path).split(sep).join('/'),
    text: readFileSync(path, 'utf8'),
  }))
}

const sources = readAll(files)

/** Source that is not a comment, so prose about these words is not a hit. */
function codeOf(text) {
  return text
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/(^|[^:])\/\/.*$/gm, '$1')
}

describe('the public tree', () => {
  it('has source files to check, so these tests are not vacuous', () => {
    expect(sources.length).toBeGreaterThan(20)
  })

  it('never imports the archived legacy modules', () => {
    const offenders = sources.filter((file) =>
      /(from|require\()\s*['"][^'"]*_inactive/.test(codeOf(file.text)),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('never references an API URL or the booking client', () => {
    const offenders = sources.filter((file) =>
      /NEXT_PUBLIC_API_URL|localhost:8000|127\.0\.0\.1:8000|lib[\\/]api|lib-api|\bfetch\s*\(|\baxios\b|\/api\//i.test(
        codeOf(file.text),
      ),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('keeps WhatsApp as a direct clinic link with no message or form data', () => {
    const offenders = sources.filter((file) =>
      /whatsappHandoffUrl|whatsappLink|\?text=/.test(codeOf(file.text)),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
    expect(directWhatsappUrl()).toBe(`https://wa.me/${clinic.whatsappNumber}`)
  })

  it('does not render a fixed mobile WhatsApp bar', () => {
    const offenders = sources.filter((file) =>
      /MobileBar|mobile-bar/.test(codeOf(file.text)),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('offers direct clinic email links without embedding consultation details', () => {
    expect(clinic.email).toBe('nymalayhomoeopathy@gmail.com')

    const offenders = sources.filter((file) =>
      /ConsultationRequestForm|emailHandoffUrl|email draft|mailto:[^'"`]*[?&](?:name|phone|concern)=/i.test(
        codeOf(file.text),
      ),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
    expect(
      sources.some((file) =>
        codeOf(file.text).includes('mailto:${clinic.email}'),
      ),
    ).toBe(true)
  })

  it('keeps the clinic name, email and safety copy visible on the public site', () => {
    const header = sources.find((file) => file.path === 'components/Header.js')
    const footer = sources.find((file) => file.path === 'components/Footer.js')
    const request = sources.find(
      (file) => file.path === 'components/sections/RequestSection.js',
    )
    const styles = sources.find((file) => file.path === 'styles/globals.css')

    expect(header.text).toContain('<span>{clinic.tagline}</span>')
    expect(styles.text).not.toMatch(
      /\.brand-copy span\s*\{\s*display:\s*none\s*;/,
    )
    expect(footer.text).toContain('Email: {clinic.email}')
    expect(footer.text).toContain(
      'Homoeopathic medicines\n          are not a substitute for Emergency or in-person medical care.',
    )
    expect(request.text).not.toContain('fee-box')
  })

  it('collects no date or time from the patient', () => {
    // The doctor assigns the slot, so there is nothing for the patient to pick.
    const offenders = sources.filter((file) =>
      /type\s*=\s*["'](date|time|datetime-local|month|week)["']/.test(file.text),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('names no preferred date or time field', () => {
    const offenders = sources.filter((file) =>
      /preferred_?(date|time)|appointment_datetime/.test(codeOf(file.text)),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('takes no payment', () => {
    const offenders = sources.filter((file) =>
      /razorpay|paymentUrl|payNow|pay_now|checkout\.razorpay|upi:\/\//i.test(
        codeOf(file.text),
      ),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('persists nothing about the patient', () => {
    const offenders = sources.filter((file) =>
      /localStorage|sessionStorage|document\.cookie|indexedDB/.test(
        codeOf(file.text),
      ),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('does not claim a request was received or confirmed', () => {
    // Opening a chat proves nothing, so no page may state otherwise. The one
    // legitimate mention of the phrase is in a comment explaining why the site
    // never uses it, so this scans code rather than prose.
    const offenders = sources.filter((file) =>
      /request (has been |was )?(received|registered|submitted)|we have (received|booked)|your (appointment|booking) is confirmed(?! after)/i.test(
        codeOf(file.text),
      ),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('does not claim the website books a slot itself', () => {
    const offenders = sources
      .filter((file) => !file.path.startsWith('lib/consultationRequest.js'))
      .filter((file) =>
        /\bbook (a|an|your) (consultation|appointment|slot)|book now|book online/i.test(
          codeOf(file.text),
        ),
      )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('never mentions Zoom or the superseded 45-60 minute duration', () => {
    const offenders = sources.filter((file) =>
      /zoom|45\s*(?:-|–|to)\s*60/i.test(file.text),
    )

    expect(offenders.map((file) => file.path)).toEqual([])
  })

  it('keeps the real contact details, not a placeholder', () => {
    expect(clinic.whatsappNumber).toMatch(/^\d{10,15}$/)
    expect(clinic.whatsappUrl).toBe(`https://wa.me/${clinic.whatsappNumber}`)
    // No stale example.com / care@ address from the earlier version.
    expect(sources.filter((file) => /care@nymalay/.test(file.text))).toEqual([])
  })
})

describe('clinic facts', () => {
  it('uses the requested Nymalay Homoeopathy brand', () => {
    expect(clinic.name).toBe('Nymalay Homoeopathy')
    expect(clinic.shortName).toBe('Nymalay')
    expect(clinic.tagline).toBe('Homoeopathy')
  })

  it('carries only the facts the plan supplied', () => {
    expect(clinic.consultationFeeInr).toBe(700)
    expect(clinic.availability).toBe('Monday–Saturday')
    expect(clinic.duration).toContain('60')
    expect(clinic.advanceNotice).toContain('3 hours')
    expect(clinic.platform).toBe('Google Meet')
    expect(clinic.platformNote).toContain('30 minutes')
  })

  it('publishes no working hours, which were never supplied', () => {
    // `scheduling` says a slot is assigned personally rather than listing times.
    expect(clinic.scheduling).toMatch(/personally/i)
    expect(JSON.stringify(clinic)).not.toMatch(/\d{1,2}\s*[:.]\s*\d{2}\s*(am|pm)/i)
  })

  it('states that the doctor approves every request', () => {
    expect(clinic.approvalNote).toMatch(/approval/i)
  })
})

describe('policies', () => {
  it('publishes exactly the three policies the plan asked for', () => {
    expect(policies.map((policy) => policy.slug)).toEqual([
      'consultation-policy',
      'cancellation-policy',
      'refund-policy',
    ])
  })

  it('gives every policy a title, a summary and some body content', () => {
    for (const policy of policies) {
      expect(policy.title).toBeTruthy()
      expect(policy.summary).toBeTruthy()
      expect(
        (policy.paragraphs?.length ?? 0) + (policy.points?.length ?? 0),
      ).toBeGreaterThan(0)
    }
  })

  it('links each policy to its own route, without duplicating a page', () => {
    for (const policy of policies) {
      expect(policyLinks).toContainEqual({
        href: `/policies/${policy.slug}`,
        label: policy.title,
      })
    }
  })

  it('invents no refund-processing timeline that was not supplied', () => {
    // The policy says refunds go via the original method, with no fixed number
    // of days, because none was given.
    const refund = policies.find((policy) => policy.slug === 'refund-policy')

    expect(JSON.stringify(refund)).not.toMatch(/\b\d+\s*(working\s*)?(business\s*)?days?\b/i)
  })
})
