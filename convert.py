import os
import sys
import click 
import csv
import pprint
import glob
import xlsxwriter

from collections import defaultdict



def calc_average_one_file(filename, skip):
    
    print("Process ", filename)
    result = defaultdict(dict)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="\t")
        line_count = 0
        
        for i in range(skip):
            next(csv_reader, None)
        channels = next(csv_reader)
        units = next(csv_reader)
   
        
        for row in csv_reader:
            for i, el in enumerate(row):
                if i < 2:
                    continue
                channel = channels[i]
                unit = units[i]
                result[channel]["unit"] = unit
                if "size" not in result[channel]:
                    result[channel]["size"] = 0
                result[channel]["size"] += 1
                if "sum" not in result[channel]:
                    result[channel]["sum"] = 0

                result[channel]["sum"] += float(el)
        result_row = []
        for key, val in result.items():
            result_row.append(val["sum"] / val["size"] ) 
        return channels[2:], units[2:], result_row 
        
    
        
@click.command()
@click.option('--path', prompt='The path',
              help='Location of files')
@click.option('--prefix', prompt='The file prefix pattern',
              help='File prefix pattern')
@click.option('--skip', default=2,
              help='Number header lines to skip')

def main(path, prefix, skip):
    result_rows = []
    for name in glob.glob(f"{path}\{prefix}*"): 
        channels, units, result_row = calc_average_one_file(name, skip)
        result_rows.append(result_row)

    print(channels)
    output_filename = "average.csv"
    with open(output_filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(channels)
        csvwriter.writerow(units)
        for row in result_rows:
            csvwriter.writerow(row)


    output_filename = "average.xlsx"
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet()


    for i, item in enumerate(channels):
        worksheet.write(0, i,     item)
    for i, item in enumerate(units):
        worksheet.write(1, i, item)

    for y, row in enumerate(result_rows):
        for x, item in enumerate(row):
            if isinstance(item, float) and not item == float("inf"):
                worksheet.write(y + 2, x, item)
    workbook.close()

            
            

if __name__ == '__main__':
    main()