#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
    Damage Calculator for my character, Krag
    Written by Christopher Durien Ward

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

from weapons.shield import shield_attack
from weapons.gore import gore_attack
from weapons.boulder import throw_boulder
import xml.etree.ElementTree as ET
import re


#For making text all colorful and easier to read.
class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def stat_grabber(character_sheet):
    relevent_stats = {}
    character_sheet = ET.parse(character_sheet)
    root = character_sheet.getroot()
    for node in root.findall("./data/node"):
        #Calc HD and ECL
        if node.attrib['name'] == "Class":
            class_to_parse = node.text
            class_to_parse = class_to_parse.split("/")
            relevent_stats['hd'] = 0
            for class_name in class_to_parse:
                result = re.search("(\d+)$", class_name)
                if result.group(1):
                    relevent_stats['hd'] += int(result.group(1))
            continue

        if node.attrib['name'] == "Size":
            relevent_stats['size'] = node.text
            continue

        if node.attrib['name'].endswith("Mod"):
            relevent_stats[node.attrib['name']] = node.text
            continue

        if node.attrib['name'] == "MABBase":
            relevent_stats['bab'] = node.text
            break

    return relevent_stats


###############
# MAIN METHOD #
###############

character_sheet = "../../character-sheets/Krag.xml"
relevent_stats = stat_grabber(character_sheet)
print relevent_stats

char_stats = {}

char_stats['HD'] = int(relevent_stats['hd'])
char_stats['StrMod'] = int(relevent_stats['StrMod'])
char_stats['ConMod'] = int(relevent_stats['ConMod'])
if relevent_stats['StrTempMod']:
    char_stats['StrMod'] = int(relevent_stats['StrTempMod'])
char_stats['BAB'] = int(relevent_stats['bab'])

STR_check_size = {
    'Fine': -16,
    'Diminutive': -12,
    'Tiny': -8,
    'Small': -4,
    'Medium': 0,
    'Large': 4,
    'Huge': 8,
    'Gargantuan': 12,
    'Colossal': 16}
attack_based_size = {
    'Fine': 8,
    'Diminutive': 4,
    'Tiny': 2,
    'Small': 1,
    'Medium': 0,
    'Large': -1,
    'Huge': -2,
    'Gargantuan': -4,
    'Colossal': -8}

#Use a dict for these
char_stats['StrSizeMod'] = int(STR_check_size[relevent_stats['size']])
char_stats['AttackSizeMod'] = int(attack_based_size[relevent_stats['size']])

char_stats['ShieldEnchance'] = 1
char_stats['BoulderRange'] = 50
char_stats['MoraleAttack'] = 0
char_stats['MoraleDmg'] = 0

char_stats['PowerAttack'] = 0
char_stats['Charging'] = False

char_stats['AutoRoll'] = False
char_stats['AutoRoll'] = raw_input('Auto roll dice?(y|n) ')
if char_stats['AutoRoll'].lower().startswith('y'):
    char_stats['AutoRoll'] = True

rage_used = False
rage_started = False
rage_rounds = -1
fatigued = False

total_damage = {}
cleave_damage = {}

print colorz.PURPLE
print "############################################"
print "#      WELCOME! TO KRAG'S DAMAGE CALC!     #"
print "############################################"

round_num = 1

while True:
    char_stats['Charging'] = False

    print "\n%sCombat round #%d%s" % (colorz.BLUE, round_num, colorz.YELLOW)

    #Charging?
    if not fatigued:
        char_stats['Charging'] = raw_input('Are you charging? (y|n) ')
        if char_stats['Charging'].lower().startswith('y'):
            char_stats['Charging'] = True

    #Power attack?
    char_stats['PowerAttack'] = int(raw_input('How many points to power attack? (Max %s) '
                                    % char_stats['BAB']))
    if char_stats['PowerAttack'] > char_stats['BAB']:
        print "%sToo many points!%s" % (colorz.RED, colorz.ENDC)
        quit()

    #Let's rage!
    print colorz.YELLOW
    if not rage_used:
        answer = raw_input('Would you like to rage? (y|n) ')
        if answer.lower().startswith('y'):
            rage_started = True
            rage_used = True
            char_stats['StrMod'] += 2
            char_stats['ConMod'] += 2
            rage_rounds = 3 + char_stats['ConMod']

    # TODO: Implement Bear Mode
    if rage_started:
        pass

    #Choose your attacks!
    while(True):

        print colorz.GREEN
        attack = raw_input('\nWhat is your attack? (shield|gore|boulder|death move|none) ')
        if attack.lower() == 'shield':
            total_damage['shield'], cleave_damage['shield'] \
                = shield_attack(char_stats)

        elif attack.lower() == 'gore':
            total_damage['gore'], cleave_damage['gore'] \
                = gore_attack(char_stats)

        elif attack.lower() == 'boulder':
            if char_stats['Charging']:
                print "%sCan't throw boulder while charging.\n" % colorz.RED
            else:
                total_damage['boulder'] = throw_boulder(char_stats)

        elif attack.lower() == 'death move':
            str_roll = general_dc_roll("STR check", total_mod=char_stats['StrMod'])
            if str_roll > char_stats['StrMod'] + 1:
                print "%sDeath move successful!%s" % (colorz.RED, colorz.YELLOW)
                if char_stats['MoraleAttack'] < 1:
                    char_stats['MoraleAttack'] = 1
                if char_stats['MoraleDmg'] < 1:
                    char_stats['MoraleDmg'] = 1

        elif attack.lower() == 'none':
            break

        print colorz.YELLOW
        again = raw_input('\nAnother attack? (y|n) ')
        if again.lower().startswith('n'):
            break

    # Decrement my rage counter
    if rage_started:
        rage_rounds -= 1
        if rage_rounds == 0:
            rage_started = False
            print "%sYou are now fatigued!%s" % (colorz.RED, colorz.YELLOW)
            char_stats['StrMod'] -= 3
            char_stats['ConMod'] -= 2
            fatigued = True


    #Print out damage summary!
    print "\n\n%s####Damage done this round####" % colorz.RED
    if total_damage:
        print "\nRegular Damage: "
        if 'shield' in total_damage:
            print "-Shield:"
            for target in total_damage['shield'].keys():
                print "--%s: %d" % (target, total_damage['shield'][target])

            if not total_damage['shield']:
                print "-- None"

        if 'gore' in total_damage:
            print "-Gore: %d" % total_damage['gore']

        if 'boulder' in total_damage:
            print "-Boulder: %d" % total_damage['boulder']

    if cleave_damage:
        print "\nCleave Damage: "
        if 'shield' in cleave_damage:
            print "-Shield:"
            for target in cleave_damage['shield'].keys():
                print "--%s: %d" % (target, cleave_damage['shield'][target])

            if not cleave_damage['shield']:
                print "-- None"

        if 'gore' in cleave_damage:
            print "-Gore: %d" % cleave_damage['gore']
    print colorz.YELLOW

    again = raw_input('Continue? (y|n) ')
    if again.lower().startswith('n'):
        break

print colorz.ENDC
