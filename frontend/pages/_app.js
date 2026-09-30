import '../styles/globals.css'

export const metadata = {
  metadataBase: new URL('https://nymalay.clinic'),
  title: {
    default: 'Nymalay — Homoeopathic Clinic',
    template: '%s | Nymalay Homoeopathic Clinic',
  },
  description:
    'Nymalay Homoeopathic Clinic — individualised online homoeopathic consultations with Dr. Arya Nerli.',
  themeColor: '#F6F2EA',
  openGraph: {
    title: 'Nymalay — Homoeopathic Clinic',
    description:
      'Individualised online homoeopathic consultations with Dr. Arya Nerli.',
    type: 'website',
  },
}

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
