import { describe, expect, it } from 'vitest'
import { feeSummary } from '../lib/consultationRequest'
import { clinic } from '../lib/site'

describe('feeSummary', () => {
  it('shows the clinic consultation fee', () => {
    expect(feeSummary().amount).toBe(
      `₹${clinic.consultationFeeInr.toLocaleString('en-IN')}`,
    )
  })

  it('states that medicine and courier costs are separate', () => {
    expect(feeSummary().detail).toMatch(/Medicine and courier charges are separate/)
  })
})
