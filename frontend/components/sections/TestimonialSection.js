import Reveal from '../Reveal'
import { testimonials } from '../../lib/site'

export default function TestimonialSection() {
  return (
    <section className="testimonial" id="testimonials">
      <div className="shell">
        {testimonials.map((item) => (
          <Reveal className="quote" key={item.quote}>
            <div className="quote-mark" aria-hidden="true">
              &ldquo;
            </div>
            <blockquote>{item.quote}</blockquote>
            <cite>{item.attribution}</cite>
          </Reveal>
        ))}
      </div>
    </section>
  )
}
