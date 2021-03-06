import sys
import json
import logging
import time
import os.path
import re
import requests
import os
from knobs import Knobs
from metrics import Metrics
from multiprocessing import Process
from fabric.api import (env, local, task, lcd, run)
from fabric.state import output as fabric_output

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
Formatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")  # pylint: disable=invalid-name

# print the log
ConsoleHandler = logging.StreamHandler(sys.stdout)  # pylint: disable=invalid-name
ConsoleHandler.setFormatter(Formatter)
LOG.addHandler(ConsoleHandler)

# Fabric environment settings
env.hosts = ['localhost']
fabric_output.update({
    'running': True,
    'stdout': True,
})

with open('driver_config.json', 'r') as f:
    CONF = json.load(f)


@task
def check_disk_usage():
    partition = CONF['database_disk']
    disk_use = 0
    cmd = "df -h {}".format(partition)
    out = local(cmd, capture=True).splitlines()[1]
    m = re.search('\d+(?=%)', out)  # pylint: disable=anomalous-backslash-in-string
    if m:
        disk_use = int(m.group(0))
    LOG.info("Current Disk Usage: %s%s", disk_use, '%')
    return disk_use


@task
def restart_database():
    if CONF['database_type'] == 'postgres':
        cmd = 'sudo service postgresql restart'
    else:
        raise Exception("Database Type {} Not Implemented !".format(CONF['database_type']))
    local(cmd)


@task
def drop_database():
    if CONF['database_type'] == 'postgres':
        cmd = "PGPASSWORD={} dropdb -e --if-exists {} -U {}".\
              format(CONF['password'], CONF['database_name'], CONF['username'])
    else:
        raise Exception("Database Type {} Not Implemented !".format(CONF['database_type']))
    local(cmd)


@task
def create_database():
    if CONF['database_type'] == 'postgres':
        cmd = "PGPASSWORD={} createdb -e {} -U {}".\
              format(CONF['password'], CONF['database_name'], CONF['username'])
    else:
        raise Exception("Database Type {} Not Implemented !".format(CONF['database_type']))
    local(cmd)


@task
def change_conf():
    next_conf = 'next_config'
    if CONF['database_type'] == 'postgres':
        cmd = 'sudo python3 PostgresConf.py {} {}'.format(next_conf, CONF['database_conf'])
    else:
        raise Exception("Database Type {} Not Implemented !".format(CONF['database_type']))
    local(cmd)


@task
def load_oltpbench():
    cmd = "./oltpbenchmark -b {} -c {} --create=true --load=true".\
          format(CONF['oltpbench_workload'], CONF['oltpbench_config'])
    with lcd(CONF['oltpbench_home']):  # pylint: disable=not-context-manager
        local(cmd)


@task
def run_oltpbench():
    cmd = "./oltpbenchmark -b {} -c {} --execute=true -s 5 -o outputfile".\
          format(CONF['oltpbench_workload'], CONF['oltpbench_config'])
    with lcd(CONF['oltpbench_home']):  # pylint: disable=not-context-manager
        local(cmd)


@task
def run_oltpbench_bg():
    cmd = "./oltpbenchmark -b {} -c {} --execute=true -s 5 -o outputfile > {} 2>&1 &".\
          format(CONF['oltpbench_workload'], CONF['oltpbench_config'], CONF['oltpbench_log'])
    with lcd(CONF['oltpbench_home']):  # pylint: disable=not-context-manager
        local(cmd)


@task
def run_controller():
    cmd = 'sudo gradle run -PappArgs="-c {} -d output/" --no-daemon'.\
          format(CONF['controller_config'])
    with lcd("../controller"):  # pylint: disable=not-context-manager
        local(cmd)


@task
def stop_controller():
    pid = int(open('../controller/pid.txt').read())
    cmd = 'sudo kill -2 {}'.format(pid)
    with lcd("../controller"):  # pylint: disable=not-context-manager
        local(cmd)


@task
def save_dbms_result():
    t = int(time.time())
    files = ['knobs.json', 'metrics_after.json', 'metrics_before.json', 'summary.json']
    for f_ in files:
        f_prefix = f_.split('.')[0]
        cmd = 'cp ../controller/output/{} {}/{}__{}.json'.\
              format(f_, CONF['save_path'], t, f_prefix)
        local(cmd)


@task
def free_cache():
    cmd = 'sync; sudo bash -c "echo 1 > /proc/sys/vm/drop_caches"'
    local(cmd)


@task
def upload_result():
    cmd = 'python3 ../../server/website/script/upload/upload.py \
           ../controller/output/ {} {}/new_result/'.format(CONF['upload_code'],
                                                           CONF['upload_url'])
    local(cmd)


@task
def get_result():
    cmd = 'python3 ../../script/query_and_get.py {} {} 5'.\
          format(CONF['upload_url'], CONF['upload_code'])
    local(cmd)


def _ready_to_start_controller():
    return (os.path.exists(CONF['oltpbench_log']) and
            'Warmup complete, starting measurements'
            in open(CONF['oltpbench_log']).read())


def _ready_to_shut_down_controller():
    pid_file_path = '../controller/pid.txt'
    return (os.path.exists(pid_file_path) and os.path.exists(CONF['oltpbench_log']) and
            'Output into file' in open(CONF['oltpbench_log']).read())


def start_recording():
    cmd = "./run_tuner.sh"
    with lcd(CONF['ostune_client_home']):
        local(cmd)

def parse_result():
    result_str=open(CONF['loop_result']).read()
    start=result_str.find(" = ")+3
    end=result_str.find("requests/sec")-1
    return float(result_str[start:end])

def write_knobs():
    cmd = "./get_knobs.sh"
    with lcd(CONF['ostune_client_home']):
        local(cmd)

def parse_vm_swapiness():
    result_str=open(CONF['vm_swapiness']).read()
    start=result_str.find(" = ") + 3
    end=len(result_str)
    return int(result_str[start:end])

def post_results(knobs: Knobs, metrics: Metrics):
    dictToSend = { 'metrics':json.dumps(metrics.serialize()),'knobs':json.dumps(knobs.serialize())}
    print(json.loads(json.dumps(dictToSend)))
    res = requests.post(CONF['tuner_url'], json=json.loads(json.dumps(dictToSend)))
    return res.json()

def get_first_recommendation():
    res = requests.get(CONF['tuner_create'])
    return res.json()

def apply_recommendation(knobs: Knobs):
    cmd = f'sudo sysctl -w vm.swappiness={knobs.vmSwapiness}'
    os.system(cmd)
    return 0

@task
def loop():
    max_disk_usage = 80

    start_recording()
    throughput = parse_result()
    LOG.info('Throughput = %.4f',throughput)
    write_knobs()
    vm_swapiness=parse_vm_swapiness()
    knobs = Knobs(vmSwapiness=vm_swapiness)
    metrics = Metrics(throughput=throughput)
    recommendation = post_results(knobs,metrics)
    knobs = Knobs(vmSwapiness=json.loads(recommendation)["vm.swapiness"])
    apply_recommendation(knobs)

@task
def run_loops(max_iter=100):
    for i in range(int(max_iter)):
        LOG.info('The %s-th Loop Starts / Total Loops %s', i + 1, max_iter)
        first_recommendation=get_first_recommendation()
        LOG.info(f'initial_recommendation = {first_recommendation}')
        knobs = Knobs(vmSwapiness=json.loads(first_recommendation)["vm.swapiness"])
        apply_recommendation(knobs)
        loop()
        LOG.info('The %s-th Loop Ends / Total Loops %s', i + 1, max_iter)
