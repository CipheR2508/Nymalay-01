import Image from 'next/image'
import Reveal from '../Reveal'
import { clinic } from '../../lib/site'

export default function DoctorSection() {
  const { doctor } = clinic

  return (
    <section className="section doctor" id="doctor">
      <div className="shell doctor-grid">
        <Reveal className="doctor-photo">
          <Image
            src={doctor.image}
            alt={`${doctor.name}, ${doctor.role}`}
            width={1086}
            height={1448}
            sizes="(max-width: 980px) 100vw, 40vw"
          />
        </Reveal>

        <Reveal className="doctor-content">
          <span className="eyebrow">Know your doctor · {doctor.credentials}</span>
          <h2>{doctor.name}</h2>
          <p className="doctor-title">{doctor.role}</p>

          <div className="doctor-copy">
            {doctor.bio.map((paragraph) => (
              <p key={paragraph.slice(0, 32)}>{paragraph}</p>
            ))}
          </div>

          <div className="doctor-points">
            {doctor.points.map((point) => (
              <div className="doctor-point" key={point.title}>
                <strong>{point.title}</strong>
                <p>{point.body}</p>
              </div>
            ))}
          </div>

          <p className="training">
            <strong>Training:</strong> {doctor.training}
          </p>
        </Reveal>
      </div>
    </section>
  )
}
