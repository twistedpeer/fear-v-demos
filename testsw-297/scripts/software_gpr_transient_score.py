#!/usr/bin/env python3
import os
import xlsxwriter

import django
from django import db
os.environ['DJANGO_SETTINGS_MODULE'] = 'app_main.settings'
django.setup()
from webapp.models import *
from django.db.models import Min, Max, Avg, Sum, Value, Count, Q

def print_scores(s):
    # exit_codes = ['signature', 'non-zero exitcode', 'ex:0', 'ex:1', 'ex:2', 'ex:3', 'ex:4', 'ex:5', 'ex:6', 'ex:7', 'ex:11', 'ex:12', 'ex:13', 'ex:15']
    totals = s.mutantlist.mutants.aggregate(
            r1_total=Count('detected_error', filter=Q(nr_or_address=1)),
            r2_total=Count('detected_error', filter=Q(nr_or_address=2)),
            r3_total=Count('detected_error', filter=Q(nr_or_address=3)),
            r4_total=Count('detected_error', filter=Q(nr_or_address=4)),
            r5_total=Count('detected_error', filter=Q(nr_or_address=5)),
            r6_total=Count('detected_error', filter=Q(nr_or_address=6)),
            r7_total=Count('detected_error', filter=Q(nr_or_address=7)),
            r8_total=Count('detected_error', filter=Q(nr_or_address=8)),
            r9_total=Count('detected_error', filter=Q(nr_or_address=9)),
            r10_total=Count('detected_error', filter=Q(nr_or_address=10)),
            r11_total=Count('detected_error', filter=Q(nr_or_address=11)),
            r12_total=Count('detected_error', filter=Q(nr_or_address=12)),
            r13_total=Count('detected_error', filter=Q(nr_or_address=13)),
            r14_total=Count('detected_error', filter=Q(nr_or_address=14)),
            r15_total=Count('detected_error', filter=Q(nr_or_address=15)),
            r16_total=Count('detected_error', filter=Q(nr_or_address=16)),
            r17_total=Count('detected_error', filter=Q(nr_or_address=17)),
            r18_total=Count('detected_error', filter=Q(nr_or_address=18)),
            r19_total=Count('detected_error', filter=Q(nr_or_address=19)),
            r20_total=Count('detected_error', filter=Q(nr_or_address=20)),
            r21_total=Count('detected_error', filter=Q(nr_or_address=21)),
            r22_total=Count('detected_error', filter=Q(nr_or_address=22)),
            r23_total=Count('detected_error', filter=Q(nr_or_address=23)),
            r24_total=Count('detected_error', filter=Q(nr_or_address=24)),
            r25_total=Count('detected_error', filter=Q(nr_or_address=25)),
            r26_total=Count('detected_error', filter=Q(nr_or_address=26)),
            r27_total=Count('detected_error', filter=Q(nr_or_address=27)),
            r28_total=Count('detected_error', filter=Q(nr_or_address=28)),
            r29_total=Count('detected_error', filter=Q(nr_or_address=29)),
            r30_total=Count('detected_error', filter=Q(nr_or_address=30)),
            r31_total=Count('detected_error', filter=Q(nr_or_address=31)),
        )
    means = s.mutantlist.mutants.killed().aggregate(
            r1_mean=(100.0/totals['r1_total'])*Count('detected_error', filter=Q(nr_or_address=1)),
            r2_mean=(100.0/totals['r2_total'])*Count('detected_error', filter=Q(nr_or_address=2)),
            r3_mean=(100.0/totals['r3_total'])*Count('detected_error', filter=Q(nr_or_address=3)),
            r4_mean=(100.0/totals['r4_total'])*Count('detected_error', filter=Q(nr_or_address=4)),
            r5_mean=(100.0/totals['r5_total'])*Count('detected_error', filter=Q(nr_or_address=5)),
            r6_mean=(100.0/totals['r6_total'])*Count('detected_error', filter=Q(nr_or_address=6)),
            r7_mean=(100.0/totals['r7_total'])*Count('detected_error', filter=Q(nr_or_address=7)),
            r8_mean=(100.0/totals['r8_total'])*Count('detected_error', filter=Q(nr_or_address=8)),
            r9_mean=(100.0/totals['r9_total'])*Count('detected_error', filter=Q(nr_or_address=9)),
            r10_mean=(100.0/totals['r10_total'])*Count('detected_error', filter=Q(nr_or_address=10)),
            r11_mean=(100.0/totals['r11_total'])*Count('detected_error', filter=Q(nr_or_address=11)),
            r12_mean=(100.0/totals['r12_total'])*Count('detected_error', filter=Q(nr_or_address=12)),
            r13_mean=(100.0/totals['r13_total'])*Count('detected_error', filter=Q(nr_or_address=13)),
            r14_mean=(100.0/totals['r14_total'])*Count('detected_error', filter=Q(nr_or_address=14)),
            r15_mean=(100.0/totals['r15_total'])*Count('detected_error', filter=Q(nr_or_address=15)),
            r16_mean=(100.0/totals['r16_total'])*Count('detected_error', filter=Q(nr_or_address=16)),
            r17_mean=(100.0/totals['r17_total'])*Count('detected_error', filter=Q(nr_or_address=17)),
            r18_mean=(100.0/totals['r18_total'])*Count('detected_error', filter=Q(nr_or_address=18)),
            r19_mean=(100.0/totals['r19_total'])*Count('detected_error', filter=Q(nr_or_address=19)),
            r20_mean=(100.0/totals['r20_total'])*Count('detected_error', filter=Q(nr_or_address=20)),
            r21_mean=(100.0/totals['r21_total'])*Count('detected_error', filter=Q(nr_or_address=21)),
            r22_mean=(100.0/totals['r22_total'])*Count('detected_error', filter=Q(nr_or_address=22)),
            r23_mean=(100.0/totals['r23_total'])*Count('detected_error', filter=Q(nr_or_address=23)),
            r24_mean=(100.0/totals['r24_total'])*Count('detected_error', filter=Q(nr_or_address=24)),
            r25_mean=(100.0/totals['r25_total'])*Count('detected_error', filter=Q(nr_or_address=25)),
            r26_mean=(100.0/totals['r26_total'])*Count('detected_error', filter=Q(nr_or_address=26)),
            r27_mean=(100.0/totals['r27_total'])*Count('detected_error', filter=Q(nr_or_address=27)),
            r28_mean=(100.0/totals['r28_total'])*Count('detected_error', filter=Q(nr_or_address=28)),
            r29_mean=(100.0/totals['r29_total'])*Count('detected_error', filter=Q(nr_or_address=29)),
            r30_mean=(100.0/totals['r30_total'])*Count('detected_error', filter=Q(nr_or_address=30)),
            r31_mean=(100.0/totals['r31_total'])*Count('detected_error', filter=Q(nr_or_address=31)),
        ).values()
    scores = [int(a*b) for a,b in zip(list(means), list(totals.values()))]

    # Skip programs that have completely uncovered GPRs:
    if 0 in scores:
        #print("# INFO: Skip Software {} because at least one GPR is not killed at all!".format(s.name))
        return

    # reg_scores = []
    # for mutants, i in [(s.mutantlist.mutants.filter(nr_or_address=i), i) for i in range(1,32)]:
    # # for mutants, i in [(s.mutantlist.mutants.filter(kind=Mutant.Kind.GPR_TRANSIENT_FLIP, nr_or_address=i), i) for i in range(1,32)]:
    #     total = mutants.count()
    #     killed = mutants.killed().count()
    #     if killed == 0 or total == 0:
    #         print("# INFO: Skip Software {} because faults for GPR {} are not covered at all!".format(s.name, i))
    #         return
    #     mean = 100.0 * killed/total
    #     reg_scores.append(mean)
    # Print per Reg and Aggregated score...
    print("{}, {}, {}".format(s.name, ", ".join(["{}".format(int(x)) for x in scores]), sum(scores)))

print("Test-Sw,R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,R11,R12,R13,R14,R15,R16,R17,R18,R19,R20,R21,R22,R23,R24,R25,R26,R27,R28,R29,R30,R31,Total-Score")
for s in Software.objects.all():
    print_scores(s)

