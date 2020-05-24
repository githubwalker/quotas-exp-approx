#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy
import argparse
import re
import math
import csv
import enum


# type of exports
class QuotasFileType(enum.Enum):
    CSV = 'CSV'
    QUIK = 'QUIK'

    def __init__(self, strVal):
        self.val = strVal


re_parse = re.compile(r'^\s*([^\d\s]+)\s+(\d{4})\s+(\d+(\.\d+){0,1})\s*$')

month2num_dict = {
    'Январь': 0,
    'Янв.': 0,
    'Февраль': 1,
    'Февр.': 1,
    'Март': 2,
    'Апрель': 3,
    'Апр.': 3,
    'Май': 4,
    'Июнь': 5,
    'Июль': 6,
    'Август': 7,
    'Авг.': 7,
    'Сентябрь': 8,
    'Сент.': 8,
    'Октябрь': 9,
    'Окт.': 9,
    'Ноябрь': 10,
    'Нояб.': 10,
    'Декабрь': 11,
    'Дек.': 11
}


def month2num(strmonth):
    if strmonth in month2num_dict:
        return month2num_dict[strmonth]

    raise Exception("month {} is not found in {}".format(strmonth, month2num_dict))


def yearmonth2num(year, strmonth):
    return (int(year) - 2000) * 12 + month2num(strmonth)



def ParseQuikQuotas(fname):
    quotas = []

    with open(fname) as f:
        for line in f.readlines():
            parsed = re_parse.match(line)
            if parsed:
                month = parsed.group(1)
                year = parsed.group(2)
                rate = parsed.group(3)
                quotas.append((yearmonth2num(year, month), float(rate)))

    return quotas


"""
<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
USDRUB,D,20020501,000000,31.0800000,31.2300000,31.0800000,31.2300000,0
USDRUB,D,20020502,000000,30.9900000,31.2400000,30.9900000,31.2400000,0
"""


def ParseCsvFile(file_name, val_name):
    quotas = []

    with open(file_name) as f:
        reader = csv.DictReader(f)
        i = 0
        for row in reader:
            quotas.append((i, float(row[val_name])))
            i += 1

    return quotas


def df2percents(df):
    return (df-1)*100.0


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--quotas-fname', dest='quotasfname', help='quotas filename', required=True)
    parser.add_argument('--type', dest='file_type', help='file type', required=True)

    args = parser.parse_args()
    if not args:
        parser.print_help()

    quota_file_type = QuotasFileType(args.file_type)

    if quota_file_type == QuotasFileType.QUIK:
        quotas = ParseQuikQuotas(args.quotasfname)
    else:
        quotas = ParseCsvFile(args.quotasfname, '<CLOSE>')

    #here apply ln
    ln_quotas = [ math.log(itm[1]) for itm in quotas]

    x = numpy.array([itm[0] for itm in quotas])
    y = numpy.array(ln_quotas)
    A = numpy.vstack([x, numpy.ones(len(x))]).T

    # ax + b
    a, b = numpy.linalg.lstsq(A, y)[0]

    y_appr = numpy.array([math.exp(a*itm[0] + b) for itm in quotas])
    numpy.array(itm[1] for itm in quotas)
    y_quotas = [ itm[1] for itm in quotas ]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.plot(x, y_quotas, 'o', label='Original data', markersize=2)
    plt.plot(x, y_appr, 'r', label='Fitted line')

    ax.text(3, 8,
            '1 trading day discount factor = %f (%f%%)\n'
            '250 trading days df (~1 year) = %f (%f%%)'
            % (math.exp(a), df2percents(math.exp(a)), math.exp(250*a), df2percents(math.exp(250*a))),
            style='italic', bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

    plt.show()
    return


if __name__ == "__main__":
    main()



