import boto3
import json
import glob
import viriciti_api
import config
from itertools import groupby

routeMapping = {"32": "C Line", "33": "C Limited", "5": "HD Line", "6": "MC Line", "9": "OCA Line", "34": "P Line", "11": "RP Line AM", "12": "RP Line PM", "13": "RWC Line", "17": "S Line AM", "18": "S Line PM", "23": "X Line", "27": "X Express AM", "35": "X Limited AM", "36": "X Limited PM", "28": "Y Line", "1": "Y Express PM", "38": "Y Limited PM", "37": "Y Limited AM"}
invMapping = {v: k for k, v in routeMapping.items()}
buses = ["2001", "2002", "2003", "2201", "2202", "2203", "2204", "2205", "2206", "2207", "2208", "2209", "2210", "3001", "3002", "3003", "3004", "3201", "3204", "3206", "3208", "3210", "3212", "3213", "3214", "3215", "3216", "3405", "3406", "3407", "3408", "3409", "3410", "3411", "3412", "3413", "3414", "3415", "3416", "3417", "3418", "3419", "3420", "3421", "3422", "3423", "3425", "3426", "3427", "3428", "3429", "3430", "3431", "3432", "3433", "3434", "3435", "3436", "3701", "3702", "3703", "3801", "3802", "3803"]

def s3_read(subfolder,localfolder):
    #subfolder and localfolder = 'YYYY-MM-DD'
    bucket_name = 'devine.spot'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=subfolder+'/'):
        output_file = obj.key.split('/')[-1]
        if output_file == "":
            continue
        else:
            s3.Object(bucket_name=bucket.name, key=obj.key).download_file(localfolder+'/'+obj.key.split('/')[-1]+'.json')

def create_dict(keys):
    return dict([(key, []) for key in keys])

def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

if __name__ == '__main__':
    subfolder = '2021-09-21'
    localfolder = subfolder
    print('Reading from S3...')
    s3_read(subfolder,localfolder) # if you have already downloaded the files from s3 comment out this line
    temp_filenames = glob.glob(subfolder+"/*")
    filenames = []
    for i in temp_filenames:
        filenames.append(i.split('/')[-1])
    filenames.sort()
    # Data Structure: {busID:{routeXX:[(starttime1,endtime1), (starttimen,endtimen)], routeYY:[(starttime, endtime)]...}}
    keysRoute = invMapping.keys()
    busesDict = {}
    for b in buses:
        busesDict[b] = create_dict(keysRoute)
    print("Processing the data...")
    for f in filenames:
        data = [json.loads(line) for line in open(subfolder+'/'+f, 'r')]
        for idx,d in enumerate(data[0]['busID']):
            if data[0]['route'][idx] != '777':
                route = routeMapping[data[0]['route'][idx]]
                busesDict[d][route].append(data[0]['timestamp'])
                # print(d, ': ', route)
                # print('---------------')
                for x in busesDict[d]:
                    if x != route:
                        busesDict[d][x].append(-1)
                    else:
                        pass
            else:
                for x in busesDict[d]:
                    busesDict[d][x].append(-1)

    busRoutes = {}
    for b in busesDict:
        busRoutes[b] = {}
        for r in busesDict[b]:
            tmp = busesDict[b][r]
            if all_equal(tmp):
                pass
            else: # generate start times and endtime for each route
                busRoutes[b][r] = []
                tmp = [int(i) for i in tmp]
                i = 0
                starttime = []
                endtime = []
                size = len(tmp)
                for idx, t in enumerate(tmp):
                    if idx == 0:
                        if t != -1:
                            if i % 2 == 0:
                                starttime.append(t)
                            else:
                                endtime.append(t)
                            i += 1
                    elif idx == size - 1:
                        if t != -1:
                            endtime.append(t)
                    else:
                        if t != -1:
                            if i % 2 == 0:
                                starttime.append(t)
                                i += 1
                            else:
                                if tmp[idx + 1] == -1:
                                    endtime.append(t)
                                    i += 1
                busRoutes[b][r] = (starttime,endtime)
    # Saving locally
    with open('ProcessedData/' + subfolder + '.json', 'w') as f:
        json.dump(busRoutes, f)
    # Saving into s3 ProcessedData/
    s3 = boto3.resource('s3')
    s3.Bucket('devine.spot').upload_file('ProcessedData/' + subfolder + '.json', 'ProcessedData/' + subfolder + '.json')
