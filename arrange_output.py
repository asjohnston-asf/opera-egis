from collections import defaultdict


with open('data/raster_table.csv') as f:
    lines = f.readlines()

dates = defaultdict(list)
for line in lines:
    key = line.split('_')[6][0:8]
    dates[key].append(line)

for key, value in dates.items():
    value.sort(reverse=True)
    previous_hash = ''
    final_lines = []
    for line in value:
        this_hash = line.split('/')[4][0:49] + line.split('/')[4][66:]
        if this_hash != previous_hash:
            final_lines.append(line)
        else:
            print(this_hash)
        previous_hash = this_hash
    with open(f'data/{key}.csv', 'w') as f:
        f.write('Raster,Name,xMin,yMin,xMax,yMax,nRows,nCols,nBands,PixelType,SRS,DownloadURL,URLDisplay,Polarization,StartDate,EndDate\n')
        f.writelines(final_lines)
