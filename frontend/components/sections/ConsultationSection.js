import Reveal from '../Reveal'
import { clinic, consultationSteps } from '../../lib/site'

export default function ConsultationSection() {
  return (
    <section className="section" id="consultation">
      <div className="shell consultation-grid">
        <Reveal className="consultation-intro">
          <span className="eyebrow">Your first consultation</span>
          <h2>Thoughtful from the first conversation.</h2>
          <p className="lead">
            Everything happens online over {clinic.platform}, wherever you’re
            based. {clinic.platformNote}.
          </p>
        </Reveal>

        <div className="timeline">
          {consultationSteps.map((step) => (
            <Reveal as="article" className="timeline-item" key={step.title}>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
