import { clinic } from './site'

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
