# Link Relations

## Background, semantics and corresponding URI form

IANA, "Link Relations", <http://www.iana.org/assignments/link-relations/link-relations.xhtml> are defined by [RFC5988](http://tools.ietf.org/html/rfc5988). Link headers are explicitly defined to be semantically equivalent to HTML `\<link\>` elements ([RFC5988 section 5](http://tools.ietf.org/html/rfc5988#section-5)):

> The Link entity-header field provides a means for serialising one or
> more links in HTTP headers.  It is semantically equivalent to the
> `\<LINK\>` element in HTML, as well as the `atom:link` feed-level element
> in Atom [RFC4287](http://tools.ietf.org/html/rfc4287).

In Appendix B the URI prefix `http://www.iana.org/assignments/relation/` is specified to convert the relation types to absolute URIs whit noting that in Link headers they should be expressed in the registered form:

> Atom allows registered link relation types to be serialised as
> absolute URIs.  Such relation types SHOULD be converted to the
> appropriate registered form (e.g.,
> `"http://www.iana.org/assignments/relation/self"` to `"self"`) so that
> they are not mistaken for extension relation types.

Unfortunately, the IANA website does not support redirection from these absolute URIs to points in the registry, access to <http://www.iana.org/assignments/relation/self>, and to other absolute link relation URIs, gives a 404 NOT FOUND response.

We can infer that a resource `URI-CONTEXT` which gives and HTTP response with link relation `REL` to `URI-TARGET` is equivalent to the RDF statement (Turtle):

```turtle
prefix iana: <http://www.iana.org/assignments/link-relations/> .
<URI-CONTEXT> iana:REL <URI-TARGET> .
```

## Relevant link relations

### Preferred and alternate versions

*canonical* -- _"Designates the preferred version of a resource (the IRI and its contents)."_ Specified in [RFC6596](http://tools.ietf.org/html/rfc6596) where the suggested behavior of consuming applications is described as _"applications such as search engines can focus processing on the canonical, and references to the context (referring) IRI can be updated to reference the target (canonical) IRI"._

*alternate* -- _"Refers to a substitute for this context"_ and is defined as part of [HTML5](http://www.w3.org/TR/html5/links.html#rel-alternate) and is explicitly defined as transitive. This seems to be the appropriate relation for versions of an object in different formats such as HTML, PDF and PostScript versions of an article.

### Collections and members

*collection* -- _"The target IRI points to a resource that represents the_(should say "a") _collection resource for the context IRI."_ Defined in [RFC6573](http://tools.ietf.org/html/rfc6573) and inverse ("reciprocal") to *item*.

*item* -- _"The target IRI points to a resource that is a member of the collection represented by the context IRI."_ Defined in [RFC6573](http://tools.ietf.org/html/rfc6573) and inverse ("reciprocal") to *collection*. A single item may be in multiple collections. It does not make sense for an item to be its own collection.

### Metadata

*describes* -- Asserts that the context resource provides a description of the target resource. Defined by [RFC6892](http://tools.ietf.org/html/rfc6892) an explicitly defined as the inverse of *describedby*.

*describedby* -- Asserts that the target resource provides a description of the context resource. The inverse of *describes*. Originally defined by [POWDER](http://www.w3.org/TR/powder-dr/#assoc-linking) and more recently redefined by [LDP](http://www.w3.org/TR/ldp/#link-relation-describedby). The POWDER specification says that the two URIs `http://www.w3.org/2007/05/powder-s#describedby` and `http://www.iana.org/assignments/relation/describedby` may be used interchangably (implied `owl:sameAs`).

### Memento link relations

Section 2.2 of the [Memento RFC7089](http://tools.ietf.org/html/rfc7089#section-2.2) defines 4 link relations (and associated attributes that are not included here):

*original* -- _"A link with an "original" Relation Type is used to point from a TimeGate or a Memento to its associated Original Resource."_

*timegate* -- _"A link with a "timegate" Relation Type is used to point from the Original Resource, as well as from a Memento associated with the Original Resource, to a TimeGate for the Original Resource."_

*timemap* -- _"A link with a "timemap" Relation Type is used to point from a TimeGate or a Memento associated with an Original Resource, as well as from the Original Resource itself, to a TimeMap for the Original Resource."_

*memento* -- _"A link with a "memento" Relation Type is used to point from a TimeGate or a Memento for an Original Resource, as well as from the Original Resource itself, to a Memento for the Original Resource."_

## Proposed link relations

*convertedFrom* - The draft ['XML2RFC' version 3 Vocabulary](https://tools.ietf.org/html/draft-hoffman-xml2rfc-16#section-6.2) seeks to register a `convertedFrom` relation.
