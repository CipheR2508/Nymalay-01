import Image from 'next/image'
import Link from 'next/link'
import { clinic, navigation } from '../lib/site'
import { policyLinks } from '../lib/policies'

export default function Footer() {
  return (
    <footer>
      <div className="shell">
        <div className="footer-grid">
          <div className="footer-brand">
            <Image
              src={clinic.doctor.logo}
              alt={`${clinic.name} logo`}
              width={40}
              height={40}
              className="brand-mark"
            />
            <div className="brand-copy">
              <strong>{clinic.shortName.toUpperCase()}</strong>
              <span>{clinic.tagline}</span>
            </div>
          </div>

          <div className="footer-meta">
            <nav aria-label="Footer pages">
              <ul className="footer-links">
                {navigation.map((item) => (
                  <li key={item.href}>
                    <Link href={item.href}>{item.label}</Link>
                  </li>
                ))}
              </ul>
            </nav>

            <nav aria-label="Policies" style={{ marginTop: 20 }}>
              <ul className="footer-links">
                {policyLinks.map((policy) => (
                  <li key={policy.href}>
                    <Link href={policy.href}>{policy.label}</Link>
                  </li>
                ))}
              </ul>
            </nav>

            <p style={{ marginTop: 20 }}>
              WhatsApp:{' '}
              <a
                href={clinic.whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                {clinic.whatsappDisplay}
              </a>
              <br />
              Online consultations · {clinic.availability}
            </p>
          </div>
        </div>

        <p className="copyright">
          © {new Date().getFullYear()} {clinic.name}. Homoeopathy is a
          complementary therapy and is not a substitute for emergency or
          in-person medical care.
        </p>
      </div>
    </footer>
  )
}
