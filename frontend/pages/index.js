import Layout from '../components/Layout'
import HeroSection from '../components/sections/HeroSection'
import ApproachSection from '../components/sections/ApproachSection'
import ConditionsSection from '../components/sections/ConditionsSection'
import DoctorSection from '../components/sections/DoctorSection'
import ConsultationSection from '../components/sections/ConsultationSection'
import TestimonialSection from '../components/sections/TestimonialSection'
import RequestSection from '../components/sections/RequestSection'

export default function Home() {
  return (
    <Layout>
      <HeroSection />
      <ApproachSection />
      <ConditionsSection />
      <DoctorSection />
      <ConsultationSection />
      <TestimonialSection />
      <RequestSection />
    </Layout>
  )
}
