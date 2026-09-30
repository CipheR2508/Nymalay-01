import Reveal from '../Reveal'
import { approachSteps } from '../../lib/site'

export default function ApproachSection() {
  return (
    <section className="section approach" id="approach">
      <div className="shell">
        <Reveal className="section-head">
          <div>
            <span className="eyebrow">How we work</span>
            <h2>Care built around the case, not a checklist.</h2>
          </div>
          <div className="copy">
            <p className="lead">
              Every case starts the same way, no matter how small the complaint
              or how long-standing it is.
            </p>
          </div>
        </Reveal>

        <div className="steps">
          {approachSteps.map((step) => (
            <Reveal as="article" className="step-card" key={step.number}>
              <span className="step-num">{step.number}</span>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
