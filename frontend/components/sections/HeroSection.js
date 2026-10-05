import Image from 'next/image'
import Link from 'next/link'
import { MessageCircle } from 'lucide-react'
import Reveal from '../Reveal'
import { clinic } from '../../lib/site'

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="shell hero-grid">
        <div className="hero-copy">
          <Reveal as="p" className="eyebrow">
            {clinic.shortName} · Online consultations
          </Reveal>
          <Reveal as="h1">
            Treatment that looks at the whole person, not just the symptom.
          </Reveal>
          <Reveal as="p" className="lead">
            {clinic.shortName} offers classical homoeopathic care for chronic and
            everyday conditions — gentle, individualised, and built around a
            proper case history. Consultations are online, wherever you are.
          </Reveal>
          <Reveal className="hero-actions">
            <a
              className="btn btn-primary"
              href={clinic.whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageCircle aria-hidden="true" /> Contact on WhatsApp
            </a>
            <a className="btn btn-secondary" href={`mailto:${clinic.email}`}>
              Email the clinic
            </a>
            <Link className="btn btn-secondary" href="/services">
              Our approach
            </Link>
          </Reveal>
        </div>

        <Reveal className="hero-visual">
          <div className="photo-frame">
            <Image
              src={clinic.doctor.image}
              alt={`${clinic.doctor.name} at ${clinic.name}`}
              fill
              sizes="(max-width: 980px) 100vw, 40vw"
              priority
            />
          </div>
          <div className="hero-note">
            <strong>Care that starts with listening.</strong>
            <span>
              Detailed case-taking · Individualised remedy · Thoughtful
              follow-through
            </span>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
