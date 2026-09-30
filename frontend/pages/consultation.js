import Head from 'next/head'
import Link from 'next/link'
import Layout from '../components/Layout'
import ConsultationSection from '../components/sections/ConsultationSection'
import RequestSection from '../components/sections/RequestSection'
import { clinic } from '../lib/site'
import { policyLinks } from '../lib/policies'

const FAQ = [
  {
    q: 'How do I request a consultation?',
    a: `Fill in the consultation form and choose “Continue to WhatsApp” or “Email instead”. ${clinic.doctor.name} reviews your request and will contact you to agree a date and time.`,
  },
  {
    q: 'Can I pick my own date and time?',
    a: `No — ${clinic.scheduling.toLowerCase()}. Please allow ${clinic.advanceNotice.toLowerCase()}.`,
  },
  {
    q: 'Is my appointment confirmed automatically?',
    a: `No. ${clinic.approvalNote}. Payment alone does not confirm an appointment; the doctor confirms it personally after verifying payment.`,
  },
  {
    q: 'When are consultations available?',
    a: `${clinic.availability}. Requests are reviewed by the doctor rather than booked by a calendar.`,
  },
  {
    q: 'How long does a first consultation take?',
    a: `${clinic.duration}, and longer where the case needs it. The time is spent on your history, temperament and pattern rather than only the presenting complaint.`,
  },
  {
    q: 'Is it really online?',
    a: `Yes. Consultations happen over ${clinic.platform}. ${clinic.platformNote}.`,
  },
  {
    q: 'What does it cost?',
    a: `₹${clinic.consultationFeeInr.toLocaleString('en-IN')}, charged once, covering the consultation and clinical assessment. Medicine and courier charges are separate and communicated according to your case. Payment instructions are shared after a slot is agreed.`,
  },
  {
    q: 'What do I need for the first call?',
    a: 'A quiet place, and if possible a note of any medicines or supplements you are currently taking, plus previous test reports or prescriptions you can share on screen.',
  },
  {
    q: 'How do I change or cancel my appointment?',
    // Deliberately not the refund terms: they are policy, and restating them
    // here is how two versions of the same rule drift apart. The full terms,
    // including the notice periods, live in the linked policies.
    a: 'Tell us on WhatsApp as early as possible so we can offer the slot to someone else. One patient-requested change is allowed. The notice periods and refund terms are set out in the cancellation and refund policies below.',
  },
  {
    q: 'Is this a replacement for in-person care?',
    a: 'No. Homoeopathy is a complementary therapy, and online consultation is not suitable for emergencies. Emergencies and conditions needing hospital assessment are always better handled in person, and we will say so if that applies to you.',
  },
]

export default function Consultation() {
  return (
    <Layout>
      <Head>
        <title>Consultation</title>
        <meta
          name="description"
          content={`What a homoeopathic consultation at ${clinic.name} involves, how it is conducted online, and how to request one.`}
        />
      </Head>

      <section className="page-head">
        <div className="shell">
          <p className="eyebrow">Consultation</p>
          <h1>Thoughtful from the first conversation.</h1>
        </div>
      </section>

      <ConsultationSection />

      <section className="section" id="faq" style={{ paddingTop: 0 }}>
        <div className="shell">
          <div className="section-head">
            <div>
              <span className="eyebrow">Before you request</span>
              <h2>Common questions.</h2>
            </div>
            <div className="copy">
              <p className="lead">
                Anything else, just ask on WhatsApp — it is usually the quickest
                way to get a straight answer.
              </p>
            </div>
          </div>

          <div className="timeline plain">
            {FAQ.map((item) => (
              <article className="timeline-item" key={item.q}>
                <h3>{item.q}</h3>
                <p>{item.a}</p>
              </article>
            ))}
          </div>

          <nav className="policy-links" aria-label="Clinic policies" style={{ marginTop: 36 }}>
            <p className="eyebrow">Policies</p>
            <ul>
              {policyLinks.map((policy) => (
                <li key={policy.href}>
                  <Link href={policy.href}>{policy.label}</Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </section>

      <RequestSection />
    </Layout>
  )
}
