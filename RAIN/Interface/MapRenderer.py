#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
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

from RAIN.System import Registry
from RAIN.System import RPCComponent
from RAIN.Messages import Message

import mapnik2 as mapnik

class MapRenderer(RPCComponent.RPCComponent):
    """
    """

    mapsize = 1024, 768
    mapfile = "./RAIN/Static/world_boundaries.xml"
    backgroundColor = '#114B7F'
    foregroundColor = '#6494BF'
    # long/lat in degrees, aka ESPG:4326 and "WGS 84" 
    longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    # can also be constructed as:
    #longlat = mapnik.Projection('+init=epsg:4326')

    merc = mapnik.Projection(
        '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null '
        '+no_defs +over')

    def rpc_renderCoord(self, lat, lon, zoom):
        im = mapnik.Image(self.mapsize[0], self.mapsize[1])

        center = mapnik.Coord(lat, lon)
        transform = mapnik.ProjTransform(self.longlat, self.merc)
        merc_center = transform.forward(center)

        dx = (20037508.34 * 2 * (self.mapsize[0] / 2)) / (256 * (2 ** (zoom)))
        minx = merc_center.x - dx
        maxx = merc_center.x + dx

        self.rendermap.aspect_fix_mode = mapnik.aspect_fix_mode.ADJUST_BBOX_HEIGHT

        merc_bbox = mapnik.Box2d(minx, merc_center.y - 1, maxx, merc_center.y + 1)
        self.rendermap.zoom_to_box(merc_bbox)
        mapnik.render(self.rendermap, im)
        Map = im.tostring('png')

        return (True, Map)

    def rpc_renderCoordOld(self, lat, lon, zoom):
        """
        Renders a map for the given coordinates.
        """
        Map = None

        LandmassShapefile = 'RAIN/Interface/ne_110m_admin_0_countries.shp'

        im = mapnik.Image(self.mapsize[0], self.mapsize[1])
        m = mapnik.Map(self.mapsize[0], self.mapsize[1])

        m.background = mapnik.Color(self.backgroundColor)
        s = mapnik.Style()
        r = mapnik.Rule()
        polygon_symbolizer = mapnik.PolygonSymbolizer(mapnik.Color(self.foregroundColor))
        r.symbols.append(polygon_symbolizer)
        line_symbolizer = mapnik.LineSymbolizer(mapnik.Color('rgb(50%,50%,50%)'), 0.1)
        r.symbols.append(line_symbolizer)
        s.rules.append(r)
        m.append_style('My Style', s)

        ds = mapnik.Shapefile(file=LandmassShapefile)
        layer = mapnik.Layer('world')
        layer.datasource = ds
        layer.styles.append('My Style')
        m.layers.append(layer)

        center = mapnik.Coord(lat, lon)
        transform = mapnik.ProjTransform(self.longlat, self.merc)
        merc_center = transform.forward(center)

        dx = (20037508.34 * 2 * (self.mapsize[0] / 2)) / (256 * (2 ** (zoom)))
        minx = merc_center.x - dx
        maxx = merc_center.x + dx

        m.aspect_fix_mode = mapnik.aspect_fix_mode.ADJUST_BBOX_HEIGHT

        merc_bbox = mapnik.Box2d(minx, merc_center.y - 1, maxx, merc_center.y + 1)
        m.zoom_to_box(merc_bbox)
        mapnik.render(m, im)
        Map = im.tostring('png')

        return (True, Map)

    def rpc_renderArea(self, minlat, minlon, maxlat, maxlon):
        """
        Renders a map for the given coordin
        """
        Map = None

        LandmassShapefile = 'RAIN/Interface/ne_110m_admin_0_countries.shp'

        merc = mapnik.Projection(
            '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null '
            '+no_defs +over')

        # long/lat in degrees, aka ESPG:4326 and "WGS 84" 
        longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        # can also be constructed as:
        #longlat = mapnik.Projection('+init=epsg:4326')

        im = mapnik.Image(self.mapsize)

        m = self.rendermap
        m.srs = merc.params()
        bbox = mapnik.Box2d(minlat, minlon, maxlat, maxlon)
        transform = mapnik.ProjTransform(longlat, merc)
        merc_bbox = transform.forward(bbox)

        m.zoom_to_box(merc_bbox)
        mapnik.render(m, im)
        Map = im.tostring('png')

        return (True, Map)

    def __init__(self):
        self.MR['rpc_renderArea'] = {'minlat': [float, "Minimal latitude of map."],
                                     'minlon': [float, "Minimal longitude of map."],
                                     'maxlat': [float, "Maximal latitude of map."],
                                     'maxlon': [float, "Maximal longitude of map."],
        }
        self.MR['rpc_renderCoord'] = {'lat': [float, "Minimal latitude of map."],
                                      'lon': [float, "Minimal longitude of map."],
                                      'zoom': [float, "Maximal longitude of map."],
        }

        self.rendermap = mapnik.Map(self.mapsize[0], self.mapsize[1])
        mapnik.load_map(self.rendermap, self.mapfile)

        super(MapRenderer, self).__init__()

Registry.ComponentTemplates['MapRenderer'] = [MapRenderer, "Maprenderer component using mapnik"]
