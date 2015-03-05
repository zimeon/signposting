"""HTML wrapper to use a MarkDown file with RevealJS
"""

import os.path
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class HtmlWrapper(object):
    """Provide HTML wrapper for Markdown files for JS-Reveal
    """

    def __init__(self, base_dir, verbose=False):
        self.verbose = verbose
        # User files
        self.base_dir=base_dir
        # Package data
        self.data_dir = os.path.join(os.path.dirname(__file__),'data')
        self.template_dir = os.path.join(os.path.dirname(__file__),'templates')

    def wrapper_url(self,url):
        """Check whether we should provide a wrapper for url, return nothing
        if not, else wrapper url
        """
        if url.endswith('.md'):
            rjp_url = url + ".html"
            return(rjp_url)
        return(None)
    
    def source_url(self,url):
        """Return markdown source url if this is a wrapper url
        
        Returns None if this isn't a wrapper url
        """
        if url.endswith('.md.html'):
            surl = url.replace('.md.html','.md')
            if os.path.exists(surl):
                return(surl)
        return(None)

    def wrapper(self,path):
        """Return StringIO object that is HTML wrapper for Markdown
        """
        template_file = os.path.join(self.template_dir,"default.tpl")
        if (self.verbose):
            print "loading template %s" % (template_file)
        template = open(template_file).read()
        # Populate arguments for template
        args = { 'title': self.get_title(path),
                 'md_file': os.path.basename(path) }
        # Fill template and return
        f = StringIO()        
        f.write( template.format(**args) )
        return(f)

    def get_title(self,path):
        """Extract title from Markdown

        Returns string, will be '(presentation)' if not title found
        """
        md = open(path);
        for line in md.readlines():
            m = re.match("#\s+(\S.*\S)",line)
            if (m):
                return(m.group(1))
        return('(presentation)')
        
