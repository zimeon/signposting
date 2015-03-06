# graphserver.py - a playpen for signposting scenarios

`graphserver.py` is a stand-alone web server that make sets of dummy
web resources with content-negotiation, HTTP Link headers, mime types,
HTML links and images that match the [scenarios](scenarios.md) for
[signposting the scholarly web](README.md). It does this by parsing
the [GraphViz]() `dot` files used to generate the graphs. In order for
this to work a number for formatting rules must be followed in these
`dot` files.

This server is written in Python and based around the standard
[SimpleHTTPServer](https://docs.python.org/2/library/SimpleHTTPServer)
module. This is experimental code that is *not suitable for 
production use or for expose outside of a firewall*. Buyer beware! 

## Graph formatting rules

Web graphs of links and content negotiation rules are directed graphs
and can be expressed as [GraphViz]() `digraph` entries in `dot` files.
This code assumes that there will be one `digraph` per file with the 
following general form:

```
digraph JOURNAL1 {
  DOI [ style=filled ]
  DOI -> "Splash Page" [ style=dashed, label="conneg 303\ntext/html" ]
  DOI -> RDF [ style=dashed, label="conneg 303\ntext/turtle" ]
  "Splash Page" -> PDF  [ style=dashed, label="HTML\nlink" ]
  "Splash Page" -> HTML  [ style=dashed, label="HTML\nlink" ]
  "Splash Page" -> DOI [ label="canonical\ndescribes" ]
  PDF -> "Splash Page" [ label="collection" ]
  HTML -> "Splash Page" [ label="collection" ]
  PDF -> HTML [ label="alternate\ntext/html" ]
  HTML -> PDF [ label="alternate\napplication/pdf" ]
  HTML -> IMG [ style=dashed label="HTML\nimg" ]
}
```

Features are:

  * The first line starts the graph and gives it a name `JOURNAL1`. This name is used in the URI patterns as the first component, e.g. <http://localhost:9876/JOURNAL1>
  * The second line defines properties of the node (resource) `DOI`. We use `style=filled` to indicate non-information resources. It is not usually necessary to make separate statements about nodes because they are created when referenced in edge statements and are labelled with their name
  * The remaining lines define edges where the `label` attribute says what type of link it is:
    * Content negotiation is indicated with `conneg 303\ntext/html` where `303` is the redirect code to use and `text/html` is the MIME type to be used in an `Accept` header to select this option., HTTP links, HTML links, and HTML image inclusion). A linebreak `\n` may be used in place of a space to improve formatting of the graph.
    * An HTML link is indicated with `HTML\nlink` and a link will be displayed on the HTML representation of the node. The `style=dashed` attribute is used to differentiate HTML links from HTTP links.
    * An HTML image inclusion is indicated with `HTML\nimg` and a link to an image will be displayed on the HTML representation of the node. The `style=dashed` attribute is used to differentiate HTML links from HTTP links.
    * An HTTP Link is indicated with `canonical describes` or `alternate text/html` type entries. The first has two untyped links: `Link: <...>; rel="canonical"` and `Link: <...>; rel="described"`. There may be one or more rel type entries. The second gives a single link where the type of the destination specified: `Link: <...>; rel="alterante"; type="text/html"`. There may be one or more rel type entries as with the first type, but all with have the destination MIME type specified.

Resource types are inferred from the node names. There is not any consistency checking with the types specified in links to these nodes.

## Running `graphserver.py`

In case there have been any changes to the `*.dot` files, run `make` to build the `*.svg` output. The run `./graphserver.py` read the `*.dot` files and start a server at <http://localhost:9876/>:

```
simeon@RottenApple signposting>make; ./graphserver.py 
dot -Tsvg journal_with_pdf_html.dot > journal_with_pdf_html.svg
Loading /Users/simeon/src/signposting/arxiv_no_item.dot...
Loading /Users/simeon/src/signposting/arxiv_plan.dot...
Loading /Users/simeon/src/signposting/dlib_article.dot...
Loading /Users/simeon/src/signposting/journal_with_pdf_html.dot...
Loading /Users/simeon/src/signposting/multiple_resolution_by_html.dot...
Loading /Users/simeon/src/signposting/plos_with_component_image.dot...
Serving HTTP on 127.0.0.1 port 9876...
127.0.0.1 - - [06/Mar/2015 22:25:24] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [06/Mar/2015 22:25:24] "GET /css/graphserver.css HTTP/1.1" 200 -
127.0.0.1 - - [06/Mar/2015 22:25:29] "GET /JOURNAL1/ HTTP/1.1" 200 -
127.0.0.1 - - [06/Mar/2015 22:25:29] "GET /JOURNAL1/svg HTTP/1.1" 200 -
^C
```
