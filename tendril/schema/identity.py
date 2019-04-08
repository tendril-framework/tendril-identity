#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2019 Chintalagiri Shashank
#
# This file is part of tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from six import iteritems
from decimal import Decimal
from tendril.schema.base import SchemaControlledYamlFile
from tendril.config import instance_path
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


class TendrilSignatory(object):
    def __init__(self, parent, name, designation):
        self.parent = parent
        self.name = name
        self.designation = designation

    def __repr__(self):
        return "<TendrilSignatory {0}, {1}>" \
               "".format(self.name, self.designation)


class SchemaObjectSet(object):
    # TODO This needs a more appropriate home, perhaps alongside
    #      SchemaControlledYamlFile, if the import issue can be sorted out
    def __init__(self, content, objtype):
        self.content = {}
        for k, v in iteritems(content):
            self.content[k] = objtype(self, **v)

    def keys(self):
        return self.content.keys()

    def __getitem__(self, item):
        return self.content[item]


class SchemaSelectableObjectSet(SchemaObjectSet):
    # TODO This needs a more appropriate home, perhaps alongside
    #      SchemaControlledYamlFile, if the import issue can be sorted out
    def __init__(self, content, objtype):
        default = content.pop('default')
        super(SchemaSelectableObjectSet, self).__init__(content, objtype)
        self.default = self.content[default]

    def __getitem__(self, item):
        if not item:
            return self.default
        return super(SchemaSelectableObjectSet, self).__getitem__(item)


class TendrilSignatories(SchemaSelectableObjectSet):
    def __init__(self, signatories):
        super(TendrilSignatories, self).__init__(signatories,
                                                 TendrilSignatory)

    def __repr__(self):
        return "<TendrilSignatories {0}>" \
               "".format(','.join(self.content.keys()))


class MultilineString(list):
    # TODO Find a better home for this. Perhaps in t.u.types, and extend
    #      support to TXMultilineString in t.u.c.tally.
    def __init__(self, value):
        super(MultilineString, self).__init__(value)

    def __repr__(self):
        return '\n'.join(self)


class TendrilPersona(SchemaControlledYamlFile):
    supports_schema_name = 'TendrilPersona'
    supports_schema_version_max = Decimal('1.0')
    supports_schema_version_min = Decimal('1.0')

    def __init__(self, *args, **kwargs):
        self._signatory = kwargs.get('signatory', None)
        super(TendrilPersona, self).__init__(*args, **kwargs)

    def elements(self):
        e = super(TendrilPersona, self).elements()
        e.extend([
            ('_ident', ('identity', 'ident'), None),
            ('name', ('identity', 'name'), None),
            ('name_short', ('identity', 'name_short'), None),
            ('phone', ('identity', 'phone'), None),
            ('email', ('identity', 'email'), None),
            ('address', ('identity', 'address'), MultilineString),
            ('address_line', ('identity', 'address_line'), None),
            ('iec', ('identity', 'iec'), None),
            ('pan', ('identity', 'pan'), None),
            ('cin', ('identity', 'cin'), None),
            ('gstin', ('identity', 'gstin'), None),
            ('logo', ('identity', 'logo'), instance_path),
            ('black_logo', ('identity', 'black_logo'), instance_path),
            ('square_logo', ('identity', 'square_logo'), instance_path),
            ('signatories', ('identity', 'signatories'), TendrilSignatories)
        ])
        return e

    def schema_policies(self):
        policies = super(TendrilPersona, self).schema_policies()
        policies.update({})
        return policies

    @property
    def ident(self):
        return self._ident

    @property
    def signatory(self):
        return self.signatories[self._signatory]

    @signatory.setter
    def signatory(self, value):
        if value not in self.signatories.keys():
            raise ValueError("Unrecognized Signatory : {0}".format(value))
        self._signatory = value

    def __repr__(self):
        return "<TendrilPersona {0} {1}>".format(self.ident, self.path)


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_schema('TendrilPersona', TendrilPersona,
                        doc="Schema for Tendril Persona Definition Files")
