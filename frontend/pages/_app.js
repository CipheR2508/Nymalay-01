import '../styles/globals.css'

export const metadata = {
  metadataBase: new URL('https://nymalay.clinic'),
  title: {
    default: 'Nymalay Homoeopathy',
    template: '%s | Nymalay Homoeopathy',
  },
  description:
    'Nymalay Homoeopathy — individualised online homoeopathy consultations with Dr. Arya Nerli.',
  themeColor: '#F6F2EA',
  openGraph: {
    title: 'Nymalay Homoeopathy',
    description:
      'Individualised online homoeopathic consultations with Dr. Arya Nerli.',
    type: 'website',
  },
}

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
