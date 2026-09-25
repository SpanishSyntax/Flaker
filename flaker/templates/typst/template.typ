#import "@preview/charged-ieee:0.1.4": ieee

#let conf(
  title: none,
  authors: (),
  abstract: [],
  paper-size: "a4",
  index-terms: (),
  bibliography: none,
  body,
) = {
  // 1. Apply the IEEE template base
  show: ieee.with(
    title: title,
    authors: authors,
    abstract: abstract,
    paper-size: paper-size,
    index-terms: index-terms,
    bibliography: bibliography,
  )

  // 2. Set document language and region
  set text(lang: "en", region: "us")

  // 3. Set global show rules for code blocks
  show raw.where(block: true): it => block(
    fill: luma(230),
    inset: 10pt,
    radius: 5pt,
    width: 100%,
    stroke: (left: 2pt + gray),
    it,
  )

  show raw.where(block: false): it => box(
    fill: luma(230),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 3pt,
    it,
  )

  // 4. Render the actual content
  body
}
