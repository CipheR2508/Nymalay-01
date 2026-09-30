import Head from 'next/head'
import Link from 'next/link'
import Layout from '../../components/Layout'
import Reveal from '../../components/Reveal'
import { policies } from '../../lib/policies'

/**
 * One page per policy, generated from `lib/policies.js`.
 *
 * A single route rather than three near-identical files: the policies differ
 * only in content, and the content already lives in data.
 */
export default function Policy({ policy, otherPolicies }) {
  return (
    <Layout>
      <Head>
        <title>{policy.title}</title>
        <meta name="description" content={policy.summary} />
      </Head>

      <section className="page-head">
        <div className="shell">
          <p className="eyebrow">Policies</p>
          <h1>{policy.title}</h1>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="shell">
          <Reveal className="prose-clinic" style={{ maxWidth: 760 }}>
            <p className="lead">{policy.summary}</p>

            {policy.paragraphs?.map((paragraph) => (
              <p key={paragraph.slice(0, 32)}>{paragraph}</p>
            ))}

            {policy.points?.length ? (
              <ul className="policy-list">
                {policy.points.map((point) => (
                  <li key={point.slice(0, 32)}>{point}</li>
                ))}
              </ul>
            ) : null}

            {policy.note ? (
              <p className="form-note">{policy.note}</p>
            ) : null}
          </Reveal>

          <div className="card-list" style={{ marginTop: 44, maxWidth: 760 }}>
            <p className="eyebrow">Other policies</p>
            {otherPolicies.map((other) => (
              <Link
                className="quick-action"
                href={`/policies/${other.slug}`}
                key={other.slug}
              >
                <strong>{other.title}</strong>
                <span>{other.summary}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  )
}

/** Statically generated at build time: three static pages, no server needed. */
export async function getStaticPaths() {
  return {
    paths: policies.map((policy) => ({ params: { slug: policy.slug } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const policy = policies.find((item) => item.slug === params.slug)

  // `fallback: false` means an unknown slug never renders, so this is a guard
  // rather than a case that can actually be reached.
  if (!policy) return { notFound: true }

  return {
    props: {
      policy,
      otherPolicies: policies.filter((item) => item.slug !== policy.slug),
    },
  }
}
