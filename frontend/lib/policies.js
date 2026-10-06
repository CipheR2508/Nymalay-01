/*
 * Clinic policy content.
 *
 * Every word here is doctor-supplied. Nothing is invented: no additional legal
 * requirement, no clinical claim, no consent clause the clinic did not ask
 * for, no refund term that was not given, and deliberately no fixed
 * refund-processing period because none was supplied.
 *
 * The three policies are kept as data rather than markup so the footer, the
 * request form and the policy pages all render the same words from one place.
 */

export const consultationPolicy = {
  slug: 'consultation-policy',
  title: 'Consultation Policy',
  summary: 'What a consultation involves and how long it takes.',
  paragraphs: [
    'Nymalay Homoeopathy consultations follow an individualised approach. The consultation involves a detailed understanding of the patient’s presenting concerns, medical history, symptoms, lifestyle, previous treatment, and relevant investigation reports.',
    'Each consultation has a minimum duration of 60 minutes. The actual duration may vary depending on case complexity and the information required. Patients should keep relevant medical reports, prescriptions, and medication details available during consultation.',
    'Online consultations are subject to the limitations of remote healthcare. Certain conditions may require physical examination, additional investigations, or an in-person consultation.',
    'Online consultation is not intended for emergency medical situations. Patients experiencing an emergency or severe or worsening symptoms should seek immediate medical attention at an appropriate healthcare facility.',
  ],
}

export const cancellationPolicy = {
  slug: 'cancellation-policy',
  title: 'Cancellation & Rescheduling Policy',
  summary: 'Refund eligibility by notice period, and how to change a booked slot.',
  paragraphs: [
    'Patients should inform the clinic as early as possible if they cannot attend.',
  ],
  points: [
    'Cancellation at least 24 hours before the appointment: eligible for a full refund.',
    'Cancellation less than 24 hours before the appointment: refunds are not available; patients may request rescheduling, subject to availability.',
    'Missed appointment without advance notice: no refund; the patient may request rescheduling, subject to availability.',
    'Patient-requested changes are allowed once and must be requested through WhatsApp.',
    'If the clinic cancels or becomes unavailable, the patient may choose another available slot or receive a full refund.',
  ],
  /*
   * How the one-change allowance interacts with a later missed appointment is
   * genuinely unresolved in the supplied policy, so it is not stated as a rule
   * here. It is reported as an open question rather than guessed at, because
   * inventing a penalty term would bind the clinic to something it never agreed.
   */
}

export const refundPolicy = {
  slug: 'refund-policy',
  title: 'Refund Policy',
  summary: 'When refunds are available and how they are processed.',
  points: [
    'A full refund applies when the appointment is cancelled at least 24 hours beforehand.',
    'Cancellations less than 24 hours beforehand are non-refundable.',
    'Refunds are not available once the consultation has commenced or been completed.',
    'Missed appointments are non-refundable.',
    'A clinic cancellation permits a full refund if the patient chooses it instead of rescheduling.',
    'Approved refunds are processed through the original method, subject to processing timelines.',
  ],
}

export const policies = [consultationPolicy, cancellationPolicy, refundPolicy]

/** Footer and in-page navigation. */
export const policyLinks = policies.map((policy) => ({
  href: `/policies/${policy.slug}`,
  label: policy.title,
}))
