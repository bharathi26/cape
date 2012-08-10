#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#      Simple Thrust Control Virtual Component (SRCVC)
#    Copyright (C) 2011-2012  riot <riot@hackerfleet.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ANRV.System import Registry
from ANRV.System import RPCComponent
from ANRV.Messages import Message

import mapnik2 as mapnik

class MapRenderer(RPCComponent.RPCComponent):
    """
    """

    def rpc_renderMap(self, minlat, minlon, maxlat, maxlon):
        """
        Renders a map for the given coordinates.
        """
        Map = None

        SizeX, SizeY = 600,300
        BackgroundColor = '#114B7F'
        ForegroundColor = '#6494BF'
        LandmassShapefile = 'ANRV/Interface/ne_110m_admin_0_countries.shp'


        merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')

        # long/lat in degrees, aka ESPG:4326 and "WGS 84" 
        longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        # can also be constructed as:
        #longlat = mapnik.Projection('+init=epsg:4326')

        im = mapnik.Image(SizeX,SizeY)
        m = mapnik.Map(SizeX,SizeY)
        

        m.background = mapnik.Color(BackgroundColor)
        s = mapnik.Style()
        r = mapnik.Rule()
        polygon_symbolizer = mapnik.PolygonSymbolizer(mapnik.Color(ForegroundColor))
        r.symbols.append(polygon_symbolizer)
        line_symbolizer = mapnik.LineSymbolizer(mapnik.Color('rgb(50%,50%,50%)'),0.1)
        r.symbols.append(line_symbolizer)
        s.rules.append(r)
        m.append_style('My Style',s)

        ds = mapnik.Shapefile(file=LandmassShapefile)
        layer = mapnik.Layer('world')
        layer.datasource = ds
        layer.styles.append('My Style')
        m.layers.append(layer)

        m.srs = merc.params()
        bbox = mapnik.Box2d(minlat, minlon, maxlat, maxlon)
        transform = mapnik.ProjTransform(longlat, merc)
        merc_bbox = transform.forward(bbox)

        m.zoom_to_box(merc_bbox)
        mapnik.render(m, im)
        Map = im.tostring('png')


        return (True, Map)

    def __init__(self):
        self.MR['rpc_renderMap'] = {'minlat': [float, "Minimal latitude of map."],
                                    'minlon': [float, "Minimal longitude of map."],
                                    'maxlat': [float, "Maximal latitude of map."],
                                    'maxlon': [float, "Maximal longitude of map."],
                                   }
        super(MapRenderer, self).__init__()

Registry.ComponentTemplates['MapRenderer'] = [MapRenderer, "Maprenderer component using mapnik"]
