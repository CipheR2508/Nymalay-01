import Head from 'next/head'
import Link from 'next/link'
import Layout from '../components/Layout'
import Reveal from '../components/Reveal'
import ApproachSection from '../components/sections/ApproachSection'
import ConditionsSection from '../components/sections/ConditionsSection'
import RequestSection from '../components/sections/RequestSection'

export default function Services() {
  return (
    <Layout>
      <Head>
        <title>Services</title>
        <meta
          name="description"
          content="How Nyalay Homoeopathy works, and the conditions we commonly treat."
        />
      </Head>

      <section className="page-head">
        <div className="shell">
          <Reveal as="p" className="eyebrow">
            Services
          </Reveal>
          <Reveal as="h1">A general homoeopathic practice.</Reveal>
        </div>
      </section>

      <ApproachSection />
      <ConditionsSection />
      <RequestSection />
    </Layout>
  )
}
