/*
 * Clinic details in one place.
 *
 * These values were hard-coded in the design prototype and repeated across its
 * markup. Centralising them keeps the WhatsApp deep links, the contact details
 * and the page copy from drifting apart.
 *
 * Every value here is doctor-supplied. The plan for this site is explicit that
 * facts are not to be invented: no daily working hours, no response-time
 * guarantee, no payment deadline, no maximum booking window, and no
 * medicine or courier prices, because none of those have been supplied. Adding
 * one as a "helpful detail" would be a fabrication the clinic then has to honour.
 */

export const clinic = {
  name: 'Nymalay Homoeopathy',
  shortName: 'Nymalay',
  tagline: 'Homoeopathy',
  description:
    'Individualised online homoeopathy consultations with Dr. Arya Nerli.',
  email: 'nymalayhomoeopathy@gmail.com',

  // E.164 without the leading +, which is the form wa.me expects.
  whatsappNumber: '919270467358',
  whatsappDisplay: '+91 92704 67358',
  whatsappUrl: 'https://wa.me/919270467358',

  consultationFeeInr: 700,
  availability: 'Monday–Saturday',
  /** Slots are assigned personally, so there are no hours to publish. */
  scheduling: 'Date and time are personally assigned and agreed by the doctor',
  advanceNotice: 'At least 3 hours before your consultation',
  duration: 'A minimum of 60 minutes',
  platform: 'Google Meet',
  platformNote: 'The meeting link is shared 30 minutes before your consultation',
  approvalNote:
    'Every request needs the doctor’s approval before an appointment is confirmed',

  location: 'Online consultations, India',

  doctor: {
    name: 'Dr. Arya Nerli',
    role: 'Consulting Homoeopath',
    image: '/images/doctor-photo.jpg',
    logo: '/images/logo.png',
    credentials:
      'BHMS · PG Diploma in Counselling Psychology · CGO',
    training:
      'BHMS · Post Graduate Diploma in Counselling Psychology · Certificate in Gynaecology & Obstetrics (CGO)',
    bio: [
      'Dr. Arya Nerli is a BHMS-qualified consulting homoeopath with additional training in counselling psychology and gynaecology & obstetrics (CGO). Her approach brings together an understanding of physical health, emotional wellbeing, and lifestyle — recognising that health concerns are rarely caused by just one thing.',
      'With training in both homoeopathy and counselling psychology, she places emphasis on understanding each person’s concerns in depth — health history, symptoms, emotional experience, and everyday lifestyle — before arriving at an individualised approach to care. She believes good healthcare begins with being heard and understood as a whole person, not just an isolated symptom.',
    ],
    points: [
      {
        title: 'Individualised care',
        body: 'Each consultation begins with understanding the person’s unique health concerns and history.',
      },
      {
        title: 'Mind–body perspective',
        body: 'Physical and emotional wellbeing are treated as interconnected aspects of overall health.',
      },
      {
        title: 'Patient-centred consultations',
        body: 'A comfortable, non-judgmental space where patients can openly discuss what’s really going on.',
      },
      {
        title: 'Integrative understanding',
        body: 'Her background in counselling psychology complements her clinical training, so emotional and behavioural factors are considered alongside physical symptoms.',
      },
    ],
  },
}

export const navigation = [
  { href: '/', label: 'Home' },
  { href: '/services', label: 'Services' },
  { href: '/doctor', label: 'Doctor' },
  { href: '/consultation', label: 'Consultation' },
  { href: '/testimonials', label: 'Testimonials' },
  { href: '/contact', label: 'Contact' },
]

export const approachSteps = [
  {
    number: '01',
    title: 'Detailed case-taking',
    body: 'A first consultation runs long on purpose — history, temperament, and pattern matter as much as the presenting complaint.',
  },
  {
    number: '02',
    title: 'Individualised remedy',
    body: 'No two patients with the same diagnosis receive the same remedy. The prescription follows the person.',
  },
  {
    number: '03',
    title: 'Follow-through',
    body: 'Regular follow-ups to track response and refine the remedy, potency, or dosing as things shift.',
  },
]

export const conditions = [
  'Allergies & sinusitis',
  'Skin conditions (eczema, psoriasis, acne)',
  'Migraines & recurring headaches',
  'Digestive complaints (IBS, acidity)',
  'Hormonal & menstrual concerns',
  'Anxiety & sleep difficulties',
  'Joint pain & arthritis',
  'Childhood recurrent infections',
  'All acute and chronic conditions',
]

export const consultationSteps = [
  {
    title: 'Case history',
    body: 'A consultation of at least 60 minutes, covering your presenting concerns, medical history, symptoms, lifestyle and previous treatment in depth.',
  },
  {
    title: 'Remedy selection',
    body: 'Your remedy and potency are chosen to match your specific case, not just the diagnosis, and shipped or arranged wherever you are.',
  },
  {
    title: 'Follow-up',
    body: 'A later review call to assess your response and adjust if needed. Any change to an agreed slot goes through WhatsApp.',
  },
]

export const testimonials = [
  {
    quote:
      'For the first time, someone asked about my sleep and my stress before asking about my rash.',
    attribution: 'A patient, treated for chronic eczema',
  },
  {
    quote:
      'The first consultation lasted nearly an hour. Nothing had ever been that thorough before.',
    attribution: 'A patient, treated for recurring migraines',
  },
  {
    quote:
      'Video calls meant I did not have to travel three hours each way. The follow-ups kept me on track.',
    attribution: 'A patient, treated for chronic acidity',
  },
]

/**
 * Consent, approval and payment wording, kept in one place so no page can
 * quietly imply the website books or confirms anything by itself.
 */
export const approvalCopy =
  'Consultations are arranged personally by the doctor. Payment instructions will be shared through WhatsApp after a slot is agreed. Your appointment is confirmed after the doctor’s approval and payment verification.'
