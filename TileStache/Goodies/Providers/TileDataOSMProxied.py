import urllib2
from TileStache.Core import KnownUnknown, TheTileLeftANote

def coordinate_bbox(coord, projection):
    """
    """
    ul = projection.coordinateLocation(coord)
    ur = projection.coordinateLocation(coord.right())
    ll = projection.coordinateLocation(coord.down())
    lr = projection.coordinateLocation(coord.down().right())
    
    n = max(ul.lat, ur.lat, ll.lat, lr.lat)
    s = min(ul.lat, ur.lat, ll.lat, lr.lat)
    e = max(ul.lon, ur.lon, ll.lon, lr.lon)
    w = min(ul.lon, ur.lon, ll.lon, lr.lon)
    
    return n, s, e, w

class SaveableResponse:
    """ Wrapper class for XML response that makes it behave like a PIL.Image object.
    
        TileStache.getTile() expects to be able to save one of these to a buffer.
    """
    def __init__(self, data):
        self.data = data
        
    def save(self, out, format):
        if format != 'XML':
            raise KnownUnknown('TileDataOSM only saves .xml tiles, not "%s"' % format)

        out.write(self.data)

class Provider:
    """
    """
    
    def __init__(self, layer, api_root='http://api.openstreetmap.org/api/0.6/map', allowed_zoom=15):
        """
        """
        self.layer = layer
        self.api_root = api_root
        self.allowed_zoom = allowed_zoom

    def getTypeByExtension(self, extension):
        """ Get mime-type and format by file extension.
        
            This only accepts "xml".
        """
        if extension.lower() not in ('osm', 'xml'):
            raise KnownUnknown('Proxied TileDataOSM only makes .xml or .osm tiles, not "%s"' % extension)
    
        return 'text/xml', 'XML'

    def renderTile(self, width, height, srs, coord):
        """ Render a single tile, return a SaveableResponse instance.
        """
        if coord.zoom is not self.allowed_zoom:
            raise TheTileLeftANote(status_code=404, content='This layer only supports zoom %s.' % self.allowed_zoom, emit_content_type=False)

        n, s, e, w = coordinate_bbox(coord, self.layer.projection)
        url = "%s?bbox=%0.7f,%0.7f,%0.7f,%0.7f" % (self.api_root, w, s, e, n)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'OSMTiler/1.0 +http://github.com/osmlab/tiled-osm/')
        body = urllib2.urlopen(req).read()
        
        return SaveableResponse(body)

