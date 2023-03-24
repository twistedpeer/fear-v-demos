#!/usr/bin/env python3
import os
import xlsxwriter

import django
from django import db
os.environ['DJANGO_SETTINGS_MODULE'] = 'app_main.settings'
django.setup()
from webapp.models import *
from webapp.utils import analyze_hwcoverage

from django.db.models import Min, Max, Avg, Sum, Value, Count, Q
from django.db.models.functions import Coalesce


def setup_workbook_formats(wb):
    global header_merge_fmt
    global header_fmt_first
    global header_fmt
    header_merge_fmt = wb.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#333333',
        'font_color': '#EEEEEE',
        'font_size': 14})
    header_fmt_first = wb.add_format({
        'bold': 1,
        'border': 1,
        'border_color': '#777777',
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#DDDDDD',
        'font_color': '#222222',
        'font_size': 12})
    header_fmt = wb.add_format({
        'bold': 1,
        'border': 1,
        'border_color': '#777777',
        'align': 'right',
        'valign': 'vcenter',
        'fg_color': '#DDDDDD',
        'font_color': '#222222',
        'indent': 1,
        'font_size': 12})

    global footer_fmt_left
    global footer_fmt
    footer_fmt_left = wb.add_format({
        'bold': 1,
        'border': 1,
        'border_color': '#777777',
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#EEEEEE',
        'font_color': '#111111',
        'num_format': '#,##0',
        'font_size': 12})
    footer_fmt = wb.add_format({
        'bold': 1,
        'border': 1,
        'border_color': '#777777',
        'align': 'right',
        'valign': 'vcenter',
        'fg_color': '#EEEEEE',
        'font_color': '#111111',
        'num_format': '#,##0',
        'indent': 1,
        'font_size': 12})

    global cell_fmt_left
    global cell_fmt
    cell_fmt_left = wb.add_format({
        'bold': 0,
        'border': 1,
        'border_color': '#777777',
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#FFFFFF',
        'font_color': '#000000',
        'num_format': '#,##0'})
    cell_fmt = wb.add_format({
        'bold': 0,
        'border': 1,
        'border_color': '#777777',
        'align': 'right',
        'valign': 'vcenter',
        'fg_color': '#FFFFFF',
        'font_color': '#000000',
        'num_format': '#,##0',
        'indent': 1})

def write_header(ws, title, subtitle_0, subtitle_1):
    global row
    global col
    ws.merge_range(row, col, row, col+len(subtitle_0)+len(subtitle_1)-1, title, header_merge_fmt)
    ws.write_row(row+1, col, subtitle_0, header_fmt_first)
    ws.write_row(row+1, col+len(subtitle_0), subtitle_1, header_fmt)
    ws.set_row(row, 28)
    ws.set_row(row+1, 18)
    row += 2

def write_footer(ws, footer_0, footer_1):
    global row
    global col
    ws.write_row(row, col, footer_0, footer_fmt_left)
    ws.write_row(row, col+len(footer_0), footer_1, footer_fmt)
    ws.set_row(row, 18)
    row += 2

def write_data_row(ws, cell_0, cell_1):
    global row
    global col
    ws.write_row(row, col, cell_0, cell_fmt_left)
    ws.write_row(row, col+len(cell_0), cell_1, cell_fmt)
    row += 1

def main(argv):
    global row
    global col

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(argv[0])
    setup_workbook_formats(workbook)
    
    # Current Architecture:
    a = Architecture.objects.first()

    # Liste aller aufgetretenen Killed Exit Codes (aus "qemu/fear5/logger.c")
    killed_codes = [
        #"not killed",
        "signature",
        "non-zero exitcode",
        #"timeout",
        #"exception",
        "ex:0",
        "ex:1",
        "ex:2",
        "ex:3",
        "ex:4",
        "ex:5",
        "ex:6",
        "ex:7",
        #"ex:8", # n/a on FE300 (no U-mode, only M-mode)
        #"ex:9", # n/a on FE300 (no U-mode, only M-mode)
        #"ex:10", # Reserved
        "ex:11",
        "ex:12",
        "ex:13",
        #"ex:14", # Reserved
        "ex:15",
        #"unknown",
        #"interrupt",
        #"missing isa extension",
    ]
    
    # Setup "Mutants" worksheet
    row = 0
    col = 0
    worksheet = workbook.add_worksheet("Mutants")
    worksheet.set_column(0, 13 + len(killed_codes), 23, None)

    # Mutant stats for each software-test:
    write_header(worksheet, "Mutants (by Software)", 
        ["Name", "setcov_unweigthed?", "setcov_min_i_inst?", "setcov_min_i_exec?", "setcov_min_time?"], 
        ["#Killed (Total)", *["#Killed (by {})".format(x) for x in killed_codes], "#NotKilled", "#Timeout", "#Total"])
    # time_min = None
    # time_max = None
    # time_sum = 0

    # m_time_min_min = None
    # m_time_max_max = None
    # m_time_sum_sum = 0

    killed_min = None
    killed_max = None
    killed_sum = 0

    notkilled_min = None
    notkilled_max = None
    notkilled_sum = 0

    timeout_min = None
    timeout_max = None
    timeout_sum = 0

    total_min = None
    total_max = None
    total_sum = 0

    # Calculate all set-covers
    setcov_unweigthed                = Software.objects.filter(arch=a).set_cover()
    setcov_min_i_inst, sc_cost_iinst = Software.objects.filter(arch=a).weighted_set_cover('iinst')
    setcov_min_i_exec, sc_cost_iexec = Software.objects.filter(arch=a).weighted_set_cover('iexec')
    setcov_min_time, sc_cost_time    = Software.objects.filter(arch=a).weighted_set_cover('time')

    print("INFO:    Iterate over all SW and create the XLSX file...")
    for s in Software.objects.filter(arch=a):
        
        print("         - Write row for SW {}...".format(s.name))
        # r = results[s.mutantlist_id]
        
        total_count = s.mutantlist.mutants.count()
        # m_time_min, m_time_max, m_time_avg, m_time_sum = s.mutantlist.mutants.aggregate(min=Min('runtime'), max=Max('runtime'), avg=Avg('runtime'), sum=Sum('runtime')).values()
        # m_time_min, m_time_max, m_time_avg, m_time_sum = 0, 0, 0, 0
        
        notkilled_count = s.mutantlist.mutants.notkilled().count()
        timeout_count = s.mutantlist.mutants.timeout().count()
        killed_count = total_count - timeout_count - notkilled_count

        killed_count_details = s.mutantlist.mutants.aggregate(
                n_signature=Count('detected_error', filter=Q(detected_error="signature")),
                n_non_zero_exitcode=Count('detected_error', filter=Q(detected_error="non-zero exitcode")),
                ex_0=Count('detected_error', filter=Q(detected_error="ex:0")),
                ex_1=Count('detected_error', filter=Q(detected_error="ex:1")),
                ex_2=Count('detected_error', filter=Q(detected_error="ex:2")),
                ex_3=Count('detected_error', filter=Q(detected_error="ex:3")),
                ex_4=Count('detected_error', filter=Q(detected_error="ex:4")),
                ex_5=Count('detected_error', filter=Q(detected_error="ex:5")),
                ex_6=Count('detected_error', filter=Q(detected_error="ex:6")),
                ex_7=Count('detected_error', filter=Q(detected_error="ex:7")),
                #ex_8=Count('detected_error', filter=Q(detected_error="ex:8")), # n/a on FE300 (no U-mode, only M-mode)
                #ex_9=Count('detected_error', filter=Q(detected_error="ex:9")), # n/a on FE300 (no U-mode, only M-mode)
                #ex_10=Count('detected_error', filter=Q(detected_error="ex:10")), # Reserved
                ex_11=Count('detected_error', filter=Q(detected_error="ex:11")),
                ex_12=Count('detected_error', filter=Q(detected_error="ex:12")),
                ex_13=Count('detected_error', filter=Q(detected_error="ex:13")),
                #ex_14=Count('detected_error', filter=Q(detected_error="ex:14")), # Reserved
                ex_15=Count('detected_error', filter=Q(detected_error="ex:15")),
            ).values()

        # time_sum += s.time
        # m_time_sum_sum += m_time_sum
        killed_sum += killed_count
        notkilled_sum += notkilled_count
        timeout_sum += timeout_count
        total_sum += total_count

        # killed stats:
        if killed_min == None or killed_min > killed_count:
            killed_min = killed_count
        if killed_max == None or killed_max < killed_count:
            killed_max = killed_count

        # notkilled stats:
        if notkilled_min == None or notkilled_min > notkilled_count:
            notkilled_min = notkilled_count
        if notkilled_max == None or notkilled_max < notkilled_count:
            notkilled_max = notkilled_count

        # timeout stats:
        if timeout_min == None or timeout_min > timeout_count:
            timeout_min = timeout_count
        if timeout_max == None or timeout_max < timeout_count:
            timeout_max = timeout_count

        # total stats:
        if total_min == None or total_min > total_count:
            total_min = total_count
        if total_max == None or total_max < total_count:
            total_max = total_count
        
        # Mutant information per Test-Software:
        write_data_row(worksheet, [
                                    s.name, 
                                    "{}".format("++++++++" if s in setcov_unweigthed else ""), 
                                    "{}".format("++++++++" if s in setcov_min_i_inst else ""), 
                                    "{}".format("++++++++" if s in setcov_min_i_exec else ""), 
                                    "{}".format("++++++++" if s in setcov_min_time else "")
                                  ], [killed_count, *killed_count_details, notkilled_count, timeout_count, total_count])

    # Bottom area (summary information):
    sw_count = Software.objects.filter(arch=a).count()
    write_data_row(worksheet, ["Min", "", "", "", ""], [killed_min, *["-" for x in killed_codes], notkilled_min, timeout_min, total_min])
    write_data_row(worksheet, ["Max", "", "", "", ""], [killed_max, *["-" for x in killed_codes], notkilled_max, timeout_max, total_max])
    write_data_row(worksheet, ["Avg", "", "", "", ""], [killed_sum/sw_count, *["-" for x in killed_codes], notkilled_sum/sw_count, timeout_sum/sw_count, total_sum/sw_count])
    write_footer(worksheet, ["Total", "", "", "", ""], [killed_sum, *["-" for x in killed_codes], notkilled_sum, timeout_sum, total_sum])

    workbook.close()
    print("INFO: Done writing XLSX file /w permanent fault simulation results")

if __name__ == "__main__":
    main(sys.argv[1:])

