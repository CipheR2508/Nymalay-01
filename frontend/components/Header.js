import { useEffect, useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { Menu, X } from 'lucide-react'
import { clinic, navigation } from '../lib/site'

export default function Header() {
  const [open, setOpen] = useState(false)
  const router = useRouter()

  // A tap-through to another page must not leave the panel hanging open.
  useEffect(() => {
    const close = () => setOpen(false)
    router.events.on('routeChangeComplete', close)
    return () => router.events.off('routeChangeComplete', close)
  }, [router.events])

  // Escape closes the panel; the label flips so it never lies about state.
  useEffect(() => {
    if (!open) return undefined
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open])

  const isCurrent = (href) =>
    href === '/' ? router.pathname === '/' : router.pathname.startsWith(href)

  return (
    <header className="site-header">
      <div className="shell nav">
        <Link href="/" className="brand" aria-label={`${clinic.shortName} home`}>
          <Image
            src={clinic.doctor.logo}
            alt={`${clinic.name} logo`}
            width={44}
            height={44}
            className="brand-mark"
            priority
          />
          <span className="brand-copy">
            <strong>{clinic.shortName.toUpperCase()}</strong>
            <span>{clinic.tagline}</span>
          </span>
        </Link>

        <nav
          className={`nav-links${open ? ' open' : ''}`}
          id="nav-links"
          aria-label="Primary navigation"
        >
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isCurrent(item.href) ? 'page' : undefined}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </Link>
          ))}
          <Link href="/booking" className="nav-cta" onClick={() => setOpen(false)}>
            Request a consultation
          </Link>
        </nav>

        <button
          type="button"
          className="menu-btn"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
          aria-controls="nav-links"
          onClick={() => setOpen((value) => !value)}
        >
          {open ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
        </button>
      </div>
    </header>
  )
}
