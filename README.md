# Signposting the Scholarly Web

_How do we link scholarly information on the web in a way that humans and machines can find their way around?_

We are moving to a world with most scholarly information on the web and toward common use of identifiers for works/instances of both papers and data (CrossRef and DataCite DOIs in particular), and for people (ORCID). There are initiatives in versioning and connection to independent archives (Memento), and in annotation (W3C OA and Hypothes.is). Work on the semantic web is shifting to a more pactical focus on linked open data (including LDP and JSON-LD). The problem is that there are very inconsistent linking practices and when a machine or user gets to a resource (URI), it is often hard to work out _what_ the resource is, and what the _context_ is. There are many web standards that might help with this but they often solve only part of the problem, are little understood and inconsistently used. Can we work out patterns of linking, using HTTP Link headers in particular, that would help facilitate some key use case?

## Background

  * PID/splash-page pattern - Herbert's video created for FORCE2015 where he notes "I make no claims this is THE way to do it, rather it's just a quick stab at it" - <https://www.youtube.com/watch?v=deejMy4-zTU>
  * Blog post by Michael Nelson re HATEOAS that includes several further pointers - <http://ws-dl.blogspot.com/2013/11/2013-11-19-rest-hateoas-and-follow-your.html>
  * Web Linking RFC - <https://tools.ietf.org/html/rfc5988>
  * IANA link relation type registry - <http://www.iana.org/assignments/link-relations/link-relations.xhtml>
  * Erik Wilde's GitHub repo with link relation types - <https://github.com/dret/sedola/blob/master/MD/linkrels.md>
  * Memento as a versioning pattern - <http://mementoweb.org/guide/howto/>
  * Basic provenance: derivedFrom defined in - <https://tools.ietf.org/html/draft-hoffman-xml2rfc-15>
  * Requesting to "connect" resources: webmention defined in <http://indiewebcamp.com/webmention>
  * Categorizing resources: `type` defined in <http://tools.ietf.org/html/rfc6903>

## Use Cases

1. Citation, Altmetrics, Annotations - follow rel="canonical" and, if necessary rel="collection", links that would usually get up to a DOI or similar identifier for the citable object (work or expression).

*Example story:* A user pastes a splash page URI into a citation management system, how can the system understand that there is a DOI for this item and offer the option to cite that instead so that the resulting is more robust and more likely to be associated with the work in question?

2. Preservation - Use case like LOCKSS is the need to answer the question: What are all the components of this work that should be preserved? Follow all rel="describedby" and rel="item" links (potentially multiple levels perhaps through describedby and item). This could also be done with ORE aggregates so perhaps include ore:aggregates links too.

3. Crawler with preferred formats - look for rel="alternate" links to preferred formats and understand that content in different formats is equivalent. (Note that alternate in intended to be transitive per <http://www.w3.org/TR/html5/links.html#rel-alternate>).

## Scenarios

### DOI, splash page, full-text

This is the basic journal publication scenario with the possibility of more than one full-text format (perhaps HTML and PDF).

![journal_with_pdf_html.svg]

### 

