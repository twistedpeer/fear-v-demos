#!/usr/bin/env python3
import os

import django
from django import db
os.environ['DJANGO_SETTINGS_MODULE'] = 'app_main.settings'
django.setup()
from webapp.models import *
from webapp.utils import analyze_hwcoverage

def get_set_properties(covered_sw):
    c_sw = len(covered_sw)
    c_i_inst = 0
    c_i_exec = 0
    tot_time = 0
    for sw in covered_sw:
        nr_instr = sw.instructioncoverage.aggregate(i_exec=Sum('x'), i_inst=Sum('instances'))
        c_i_inst += nr_instr["i_inst"]
        c_i_exec += nr_instr["i_exec"]
        tot_time += sw.time
    return c_sw, c_i_inst, c_i_exec, tot_time

def print_results(selection):
    for s in selection:
        print(" - {}".format(s.name))
    print("-----------------------------------------------------")
    nProgs, nInstrInst, nInstrExec, simTime = get_set_properties(selection)
    print("Cost summary:")
    print(" - # of programs               : {}".format(nProgs))
    print(" - # of instruction instances  : {}".format(nInstrInst))
    print(" - # of instruction executions : {}".format(nInstrExec))
    print(" - total simulation time       : {} us".format(simTime))
    print("-----------------------------------------------------")

def main(argv):
    
    # Greedily calculate set cover /w different optimization criteria
    
    # 1) Minimal # of instruction instances (minimal binary code size)
    setcov_iinst, _ = Software.objects.weighted_set_cover('iinst')
    print("-----------------------------------------------------")
    print("Set cover /w minimal instruction instances:          ")
    print("-----------------------------------------------------")
    print_results(setcov_iinst)
    
    # 2) Minimal # of executed instructions (minimal runtime)
    setcov_iexec, _ = Software.objects.weighted_set_cover('iexec')
    print("\n-----------------------------------------------------")
    print("Set cover /w minimal instruction executions:          ")
    print("-----------------------------------------------------")
    print_results(setcov_iexec)
    
    # 3) Minimal total QEMU simulation runtime
    setcov_time, _ = Software.objects.weighted_set_cover('time')
    print("\n-----------------------------------------------------")
    print("Set cover /w minimal QEMU runtime:                   ")
    print("-----------------------------------------------------")
    print_results(setcov_time)

if __name__ == "__main__":
    main(sys.argv[1:])

