import os
import csv
import pandas as pd

def split(filehandler, delimiter=',', row_limit=1000,
          output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    import csv
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = next(reader)
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)

directory = './geocode'
split(open('./bulk_all.csv', 'r'),row_limit=9999,output_path=directory)
for idx,filename in enumerate(os.listdir(directory)):
    if filename.endswith('.csv'):
        try:
            cmd = 'curl --form addressFile=@./geocode/'+filename+' --form returntype=locations --form benchmark=Public_AR_Current https://geocoding.geo.census.gov/geocoder/locations/addressbatch --output ./geocode/result_'+filename
            print(cmd)
            print(os.system(cmd))
        except:
            print('Error'+filename)

#Build result list
results = []
for idx,filename in enumerate(os.listdir(directory)):
    if 'result' in filename:
        results.append(filename)
         
#fix headers
for filename in results:
    with open(directory+'/'+filename, newline='') as inFile, open(directory+'/n'+filename, 'w', newline='') as outfile:
        r = csv.reader(inFile)
        w = csv.writer(outfile)
        next(r, None)  # skip the first row from the reader, the old header
        # write new header
        w.writerow(['Idx', 'Address', 'Match', 'Match_type','Addres_m','Loc','ID','Side'])
        # copy the rest
        for row in r:
            w.writerow(row)

#combine all files in the list
combined_csv = pd.concat([pd.read_csv(directory+'/n'+f) for f in results])
combined_csv.to_csv(directory+'/combined_results.csv', index=True, encoding='utf-8-sig')


