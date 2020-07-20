import os
import sys
import time
import subprocess
from subprocess import PIPE

USED_CHECKSTYLE_METRICS=[
    'JavaNCSS',
    'CyclomaticComplexity',
    'NPathComplexity',
    'ClassDataAbstractionCoupling',
    'ClassFanOutComplexity',
    'BooleanExpressionComplexity'
]

def get_file_extension(language):
    if language == 'JAVA':
        return 'java'
    raise Exception('Unknown programming language: ', language)

def get_metric(line):
    TYPE_MARKER = 'type:'
    VAL_MARKER = 'val:'
    def get(line, marker):
        marker_idx = line.find(marker)
        return line[(marker_idx + len(marker)):(line.find(' ', marker_idx))]
    mtype = get(line, TYPE_MARKER)
    val = get(line, VAL_MARKER)
    return mtype, int(val)

def create_folder(runId):
    METRICS_FOLDER_PATH = os.getenv("METRICS_FOLDER_PATH")
    dir_path = f"{METRICS_FOLDER_PATH}/{runId}"
    try:
        os.makedirs(dir_path)    
        print("Directory ", dir_path, " created.")
        return dir_path
    except FileExistsError:
        print("Directory ", dir_path, " already exists.") 
        return dir_path

def write_files(submissionIds, codeList, fileExt, folderPath):
    for idx, code in enumerate(codeList):
        with open(f"{folderPath}/{submissionIds[idx]}.{fileExt}", "w") as f:
            f.write(code)

def delete_folder(folderPath):
    files = os.listdir(folderPath)
    for file in files:
        os.remove(f'{folderPath}/{file}')
    os.rmdir(folderPath)
    print('Directory ', folderPath, ' deleted.')

def add_loc(res, submissionIds, codeList):
    locs = [len(code.split('\n')) for code in codeList]
    for idx, sub_id in enumerate(submissionIds):
        if sub_id not in res:
            res[sub_id] = {}
        res[sub_id]['LOC'] = locs[idx]
    return res

def run_checkstyle(folderPath):
    CHECKSTYLE_JAR_PATH = os.getenv("CHECKSTYLE_JAR_PATH")
    CHECKSTYLE_XML_PATH = os.getenv("CHECKSTYLE_XML_PATH")
    args = ['java', '-jar', CHECKSTYLE_JAR_PATH, '-c', CHECKSTYLE_XML_PATH, 'com.puppycrawl.tools.checkstyle.gui.Main', f'{folderPath}/']
    checkstyle_result = subprocess.run(args, stdout=PIPE, stderr=PIPE, check=False)
    stdout = checkstyle_result.stdout.decode(sys.stdout.encoding)
    stderr = checkstyle_result.stderr.decode(sys.stderr.encoding)
    if len(stderr) != 0:
        raise Exception(f'Running checkstyle throwed an error: {stderr}')
    if len(stdout) < 100:
        raise Exception(f'No output produced from checkstyle metrics: {stdout}')
    return stdout.split('\n')

def generate_result_dict(lines, submissionIds):
    res = {}
    for line in lines:
        sub_id = line.split('/')[-1][:36]
        module = line.split(' ')[-1][1:-1]
        if sub_id not in res and sub_id in submissionIds:
            res[sub_id] = {}
        if module in USED_CHECKSTYLE_METRICS:
            m, v = get_metric(line)
            res[sub_id][m] = v
    return res

def run_metrics(submissionIds, codeList, language):
    file_ext = get_file_extension(language)
    run_id = int(time.time())
    folderPath = ''
    lines = []
    res = {}
    try:
        folderPath = create_folder(run_id)
        write_files(submissionIds, codeList, file_ext, folderPath)
        lines = run_checkstyle(folderPath)
        res = generate_result_dict(lines, submissionIds)
        res = add_loc(res, submissionIds, codeList)
        delete_folder(folderPath)
    except:
        delete_folder(folderPath)
        raise
    return res
