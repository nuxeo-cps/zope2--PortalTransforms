from Products.PortalTransforms.libtransforms.retransform import retransform

class html_to_text(retransform):
    inputs  = ('text/html',)
    output = 'text/plain'

def register():
    return html_to_text("html_to_text",
                       ('<script [^>]>.*</script>(?im)', ''),
                       ('<style [^>]>.*</style>(?im)', ''),
                       ('<head [^>]>.*</head>(?im)', ''),
                       ('<[^>]*>(?i)(?m)', ''),
                       )
