import re
from shutil import move
from os import remove
from sys import stdout

domains = open('cleric_domains.csv', 'r')
domains = list(domains)
line_count = 0
for domain in domains:
    line_count += 1
    per = line_count / float(len(domains)) * 100
    #stdout.write("\rProcessing: %d%%" % per)
    #stdout.flush()

    domain = domain.strip().split(";")[0]
    count = 0

    spell_list = open('all-spells.txt', 'r')
    for line in spell_list:
        if line.startswith('Level: '):
            if re.search('%s Domain \d' % re.escape(domain), line):
                if re.search('%s Domain 0' % re.escape(domain), line):
                    print '%s has a 0-level spell!' % domain
                count += 1
    if count != 9 and count != 18:
        print "%s: %s" % (domain, count)


print " COMPLETE"
