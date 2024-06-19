import pylatex
import os 
def generateReport(GBIS_Area_path):
    dirs = next(os.walk(GBIS_Area_path))[1]
    proc_dirs = [x for x in dirs if "processing_report_" in x]
    results_dir = [x for x in dirs if "INVERSION_Results" in x]
    # dirs = dirs[]
    print(proc_dirs)
    print(results_dir)


if __name__=='__main__':
    generateReport('/uolstore/Research/a/a285/homes/ee18jwc/code/auto_inv/us6000ddge_GBIS_area/')
