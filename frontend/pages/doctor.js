import Head from 'next/head'
import Layout from '../components/Layout'
import DoctorSection from '../components/sections/DoctorSection'
import RequestSection from '../components/sections/RequestSection'

export default function Doctor() {
  return (
    <Layout>
      <Head>
        <title>Doctor</title>
        <meta
          name="description"
          content="Dr. Arya Nerli, BHMS — consulting homoeopath at Nymalay Homoeopathy."
        />
      </Head>

      <section className="page-head">
        <div className="shell">
          <p className="eyebrow">Know your doctor</p>
          <h1>Care that starts with being heard.</h1>
        </div>
      </section>

      <DoctorSection />
      <RequestSection />
    </Layout>
  )
}
