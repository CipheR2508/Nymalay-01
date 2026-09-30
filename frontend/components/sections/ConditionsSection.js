import Reveal from '../Reveal'
import { conditions } from '../../lib/site'

export default function ConditionsSection() {
  return (
    <section className="section" id="conditions">
      <div className="shell">
        <Reveal className="section-head">
          <div>
            <span className="eyebrow">Commonly treated</span>
            <h2>A general homoeopathic practice.</h2>
          </div>
          <div className="copy">
            <p className="lead">
              These come up often, but case-taking isn’t limited to this list.
            </p>
          </div>
        </Reveal>

        <div className="conditions-grid">
          {conditions.map((condition, index) => (
            <Reveal className="condition" key={condition}>
              <span>{condition}</span>
              <b>{String(index + 1).padStart(2, '0')}</b>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
