import '../styles/globals.css'

export const metadata = {
  metadataBase: new URL('https://nymalay.clinic'),
  title: {
    default: 'Nyalay Homoeopathy',
    template: '%s | Nyalay Homoeopathy',
  },
  description:
    'Nyalay Homoeopathy — individualised online homoeopathy consultations with Dr. Arya Nerli.',
  themeColor: '#F6F2EA',
  openGraph: {
    title: 'Nyalay Homoeopathy',
    description:
      'Individualised online homoeopathic consultations with Dr. Arya Nerli.',
    type: 'website',
  },
}

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
