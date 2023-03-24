#!/usr/bin/env python3
import os
import xlsxwriter

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'app_main.settings'
django.setup()
from webapp.models import *
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
        'font_color': '#000000'})
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

    # Setup "Registers" worksheet
    row = 0
    col = 0
    worksheet = workbook.add_worksheet("Registers")
    worksheet.set_column(0, 0, 8, None)
    worksheet.set_column(1, 4, 12, None)

    a = Architecture.objects.first()

    # GPR: Individual information
    write_header(worksheet, "GPR (General Purpose Register)", ["Number"], ["#Reads", "#Writes", "#Sum"])
    for n in Gpr.objects.filter(subset__arch=a).values_list('number',flat=True):
        cov_gpr = GprCoverage.objects.filter(software__arch=a, register__number=n).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet, [n], cov_gpr)
    cov_stats_gpr = GprCoverage.objects.filter(software__arch=a).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
    write_footer(worksheet, ["Total"], cov_stats_gpr)

    # CSR: Individual information
    write_header(worksheet, "CSR (Control and Status Register)", ["Address"], ["#Reads", "#Writes", "#Sum"])
    for n in Csr.objects.filter(subset__arch=a).values_list('number',flat=True).distinct():
        cov_csr = CsrCoverage.objects.filter(software__arch=a, register__number=n).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet, ["0x{:03X}".format(n)], cov_csr)
    cov_stats_csr = CsrCoverage.objects.filter(software__arch=a).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
    write_footer(worksheet, ["Total"], cov_stats_csr)

    row = 0
    col = 0
    worksheet2 = workbook.add_worksheet("Memory")
    worksheet2.set_column(0, 0, 18, None)
    worksheet2.set_column(1, 5, 12, None)

    # MM-CSR: Individual information
    write_header(worksheet2, "Memory-Mapped CSRs (Device CSRs)", ["Device", "Address"], ["#Reads", "#Writes", "#Sum"])
    for mmcsr in DeviceCsr.objects.filter(device__arch=a).all():
        cov_mmcsr = DeviceCsrCoverage.objects.filter(software__arch=a, register__number=mmcsr.number).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet2, [mmcsr.device.name, "0x{:08X}".format(mmcsr.number)], cov_mmcsr)
    cov_stats_mmcsr = DeviceCsrCoverage.objects.filter(software__arch=a).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
    write_footer(worksheet2, ["Total", ""], cov_stats_mmcsr)

    # Device Memory: Individual information
    write_header(worksheet2, "Device Memory Regions", ["Device", "From", "To"], ["#Reads", "#Writes", "#Sum"])
    for mreg in MemoryRegion.objects.filter(arch=a).exclude(device=None).all():
        cov_mreg = MemoryRegionCoverage.objects.filter(software__arch=a, memory_region__pk=mreg.pk).exclude(memory_region__device=None).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet2, [mreg.device.name, "0x{:08X}".format(mreg.addr_from), "0x{:08X}".format(mreg.addr_to)], cov_mreg)
    cov_stats_device_mem = MemoryRegionCoverage.objects.filter(software__arch=a).exclude(memory_region__device=None).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
    write_footer(worksheet2, ["Total", "", ""], cov_stats_device_mem)

    # Core Memory: Individual information
    write_header(worksheet2, "Core Memory Regions", ["Name", "From", "To"], ["#Reads", "#Writes", "#Sum"])
    for mreg in MemoryRegion.objects.filter(arch=a, device=None).all():
        cov_mreg = MemoryRegionCoverage.objects.filter(software__arch=a, memory_region__pk=mreg.pk, memory_region__device=None).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet2, [mreg.name, "0x{:08X}".format(mreg.addr_from), "0x{:08X}".format(mreg.addr_to)], cov_mreg)
    cov_stats_core_mem = MemoryRegionCoverage.objects.filter(software__arch=a, memory_region__device=None).aggregate(r=Coalesce(Sum('r'), 0), w=Coalesce(Sum('w'), 0), sum=Coalesce(Sum('x'), 0)).values()
    write_footer(worksheet2, ["Total", "", ""], cov_stats_core_mem)

    row = 0
    col = 0
    worksheet3 = workbook.add_worksheet("Instructions")
    worksheet3.set_column(0, 0, 18, None)
    worksheet3.set_column(1, 5, 12, None)

    # Instructions
    cov_stats_insn = InstructionCoverage.objects.filter(software__arch=a).aggregate(instances=Coalesce(Sum('instances'), 0), executions=Coalesce(Sum('x'), 0)).values()
    write_header(worksheet3, "Instructions", ["Name", "Subset", "Format"], ["#Instances" ,"#Executions"])
    for insn in Instruction.objects.filter(subset__arch=a).all():
        cov_insn = InstructionCoverage.objects.filter(software__arch=a, instruction__pk=insn.pk).aggregate(instances=Coalesce(Sum('instances'), 0), executions=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet3, [insn.name, insn.subset.name, insn.fmt], cov_insn)
    write_footer(worksheet3, ["Total", "", ""], cov_stats_insn)

    # Instructions (grouped by subset)
    write_header(worksheet3, "Instructions (by Subset)", ["Subset"], ["#Instances" ,"#Executions"])
    for subset in Instruction.objects.filter(subset__arch=a).values_list('subset__name', flat=True).distinct():
        cov_stats_insn_subset = InstructionCoverage.objects.filter(software__arch=a, instruction__subset__name=subset).aggregate(instances=Coalesce(Sum('instances'), 0), executions=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet3, [subset], cov_stats_insn_subset)
    write_footer(worksheet3, ["Total"], cov_stats_insn)

    # Instructions (grouped by format)
    write_header(worksheet3, "Instructions (by Format)", ["Format"], ["#Instances" ,"#Executions"])
    for fmt in Instruction.objects.filter(subset__arch=a).values_list('fmt', flat=True).distinct():
        cov_stats_insn_format = InstructionCoverage.objects.filter(software__arch=a, instruction__fmt=fmt).aggregate(instances=Coalesce(Sum('instances'), 0), executions=Coalesce(Sum('x'), 0)).values()
        write_data_row(worksheet3, [fmt], cov_stats_insn_format)
    write_footer(worksheet3, ["Total"], cov_stats_insn)

    workbook.close()

if __name__ == "__main__":
    main(sys.argv[1:])

