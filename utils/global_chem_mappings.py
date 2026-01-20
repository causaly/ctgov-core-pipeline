#!/usr/bin/python
# -*- coding: utf-8 -*-

# this script defines global abbreviations for chemical elements and molecules
# single letter elements are not considered
# elements whose symbol is typically associated with a different concept are also omitted

global_chem2text = dict()

# special substances and events
global_chem2text['fat'] = 'body fats'
global_chem2text['nap'] = 'napping'

# molecules
global_chem2text['H2'] = 'hydrogen'
global_chem2text['O2'] = 'oxygen'
global_chem2text['N2'] = 'nitrogen'

# actinides
#global_chem2text['Ac'] = 'actinium'
#global_chem2text['Am'] = 'americium'
#global_chem2text['Bk'] = 'berkelium'
#global_chem2text['Cf'] = 'californium'
#global_chem2text['Cm'] = 'curium'
#global_chem2text['Es'] = 'einsteinium'
#global_chem2text['Fm'] = 'fermium'
#global_chem2text['Lr'] = 'lawrencium'
#global_chem2text['Md'] = 'mendelevium'
#global_chem2text['Np'] = 'neptunium'
#global_chem2text['No'] = 'nobelium'
#global_chem2text['Pu'] = 'plutonium'
#global_chem2text['Pa'] = 'protactinium'
#global_chem2text['Th'] = 'thorium'
#global_chem2text['U'] = 'uranium'

# alkali earth metals
global_chem2text['Ba'] = 'barium'
global_chem2text['Be'] = 'beryllium'
global_chem2text['Ca'] = 'calcium'
global_chem2text['Mg'] = 'magnesium'
global_chem2text['Ra'] = 'radium'
global_chem2text['Sr'] = 'strontium'

# alkali metals
global_chem2text['Cs'] = 'cesium'
global_chem2text['Fr'] = 'francium'
global_chem2text['Li'] = 'lithium'
#global_chem2text['K'] = 'potassium'
global_chem2text['Rb'] = 'rubidium'
global_chem2text['Na'] = 'sodium'

# halogens
#global_chem2text['At'] = 'astatine'
global_chem2text['Br'] = 'bromine'
global_chem2text['Cl'] = 'chlorine'
#global_chem2text['F'] = 'fluorine'
#global_chem2text['I'] = 'iodine'

# lanthanides
#global_chem2text['Ce'] = 'cerium'
#global_chem2text['Dy'] = 'dysprosium'
#global_chem2text['Er'] = 'erbium'
#global_chem2text['Eu'] = 'europium'
#global_chem2text['Gd'] = 'gadolinium'
#global_chem2text['Ho'] = 'holmium'
#global_chem2text['La'] = 'lanthanum'
#global_chem2text['Lu'] = 'lutetium'
#global_chem2text['Nd'] = 'neodymium'
#global_chem2text['Pr'] = 'praseodymium'
#global_chem2text['Pm'] = 'promethium'
#global_chem2text['Sm'] = 'samarium'
#global_chem2text['Tb'] = 'terbium'
#global_chem2text['Tm'] = 'thulium'
#global_chem2text['Yb'] = 'ytterbium'

# metalloids (metals)
global_chem2text['Sb'] = 'antimony'
global_chem2text['Ge'] = 'germanium'
global_chem2text['Po'] = 'polonium'

# metalloids (nonmetals)
#global_chem2text['As'] = 'arsenic'
#global_chem2text['B'] = 'boron'
global_chem2text['Si'] = 'silicon'
global_chem2text['Te'] = 'tellurium'

# metals
#global_chem2text['Al'] = 'aluminum'
#global_chem2text['Bi'] = 'bismuth'
global_chem2text['Ga'] = 'gallium'
#global_chem2text['In'] = 'indium'
global_chem2text['Pb'] = 'lead'
global_chem2text['Tl'] = 'thallium'
global_chem2text['Sn'] = 'tin'

# noble gasses
global_chem2text['Ar'] = 'argon'
global_chem2text['He'] = 'helium'
global_chem2text['Kr'] = 'krypton'
global_chem2text['Ne'] = 'neon'
global_chem2text['Rn'] = 'radon'
global_chem2text['Xe'] = 'xenon'

# nonmetals
#global_chem2text['C'] = 'carbon'
#global_chem2text['H'] = 'hydrogen'
#global_chem2text['N'] = 'nitrogen'
#global_chem2text['O'] = 'oxygen'
#global_chem2text['P'] = 'phosphorus'
global_chem2text['Se'] = 'selenium'
#global_chem2text['S'] = 'sulfur'

# transactinides
#global_chem2text['Bh'] = 'bohrium'
#global_chem2text['Ds'] = 'darmstadtium'
#global_chem2text['Db'] = 'dubnium'
#global_chem2text['Hs'] = 'hassium'
#global_chem2text['Mt'] = 'meitnerium'
#global_chem2text['Rg'] = 'roentgenium'
#global_chem2text['Rf'] = 'rutherfordium'
#global_chem2text['Sg'] = 'seaborgium'

# transition metals
global_chem2text['Cd'] = 'cadmium'
global_chem2text['Cr'] = 'chromium'
#global_chem2text['Co'] = 'cobalt'
global_chem2text['Cu'] = 'copper'
global_chem2text['Au'] = 'gold'
global_chem2text['Hf'] = 'hafnium'
global_chem2text['Ir'] = 'iridium'
global_chem2text['Fe'] = 'iron'
global_chem2text['Mn'] = 'manganese'
global_chem2text['Hg'] = 'mercury'
global_chem2text['Mo'] = 'molybdenum'
global_chem2text['Ni'] = 'nickel'
global_chem2text['Nb'] = 'niobium'
global_chem2text['Os'] = 'osmium'
global_chem2text['Pd'] = 'palladium'
global_chem2text['Pt'] = 'platinum'
#global_chem2text['Re'] = 'phenium'
global_chem2text['Rh'] = 'rhodium'
global_chem2text['Ru'] = 'ruthenium'
global_chem2text['Sc'] = 'scandium'
global_chem2text['Ag'] = 'silver'
global_chem2text['Ta'] = 'tantalum'
global_chem2text['Tc'] = 'technetium'
global_chem2text['Ti'] = 'titanium'
#global_chem2text['W'] = 'tungsten'
#global_chem2text['V'] = 'vanadium'
#global_chem2text['Y'] = 'yttrium'
global_chem2text['Zn'] = 'zinc'
global_chem2text['Zr'] = 'zirconium'

