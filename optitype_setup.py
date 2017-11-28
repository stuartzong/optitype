import os
import sys
import datetime
import argparse
import pandas as pd
from jinja2 import Environment, FileSystemLoader


def populate_sh_template(TMP_DIR, patient, library, sh_script, fq1, fq2,
                         HLA_REF, project, data_type, run_type):
    jinja2_env = Environment(loader=FileSystemLoader([TMP_DIR]),
                             trim_blocks=True)
    template = jinja2_env.get_template('optitype_template.sh')
    with open(sh_script, 'w') as opf:
        content = template.render(sh_script=sh_script,
                                  patient=patient,
                                  library=library,
                                  fq1=fq1,
                                  fq2=fq2,
                                  HLA_REF=HLA_REF,
                                  project=project,
                                  data_type=data_type,
                                  run_type=run_type)
        opf.write(content)
        print('templated {}'.format(sh_script))
    return sh_script


def make_optitype_scripts(df_patient, data_type, WKDIR, project,
                          TMP_DIR, HLA_REF, run_type):
    for index, row in df_patient.iterrows():
        patient = row.patient
        library = row.library
        fq1 = row.fastq1
        fq2 = row.fastq2
        sh_script = '.'.join([patient, library, data_type, 'optipye', 'sh'])
        sh_script = '/'.join([WKDIR, project, data_type, sh_script])
        populate_sh_template(TMP_DIR,
                             patient,
                             library,
                             sh_script,
                             fq1,
                             fq2,
                             HLA_REF,
                             project,
                             data_type,
                             run_type);


def determine_reference(data_type, DNA_HLA_REF, RNA_HLA_REF):
    if data_type == 'DNA':
        HLA_REF = DNA_HLA_REF
    elif data_type == 'RNA':
        HLA_REF = RNA_HLA_REF
    else:
        sys.exit('ERROR: unrecoginized sequence data type. It must be either DNA or RNA!')
    print('reference is:', HLA_REF)
    return HLA_REF


def make_directory(WKDIR, project, data_type):
    dir1 = '/'.join([WKDIR, project])
    dir2 = '/'.join([WKDIR, project, data_type])
    if not os.path.exists(dir1):
        os.makedirs(dir1)
    if not os.path.exists(dir2):
        os.makedirs(dir2)


def parse_args():
    parser = argparse.ArgumentParser(
        description='setup OptiType!')
    parser.add_argument('-i', '--INPUT_FILE',
                        help='specify input file including headers: patient, library, fastq1, fastq2',
                        required=True)
    parser.add_argument('-p', '--PROJECT',
                        help='specify project name',
                        required=True)
    parser.add_argument('-t', '--DATA_TYPE',
                        help='specify data type, either DNA or RNA',
                        required=True)
    args = parser.parse_args()
    return args


def __main__():
    print('Scripts starts at: {}!'.format(datetime.datetime.now())) 
    args = parse_args()
    f = args.INPUT_FILE
    data_type = args.DATA_TYPE.upper()
    run_type = data_type.lower()
    project = args.PROJECT
    TMP_DIR = '/home/szong/projects/development/optitype'
    RNA_HLA_REF = '/gsc/software/linux-x86_64-centos6/optitype/data/hla_reference_rna.fasta'
    DNA_HLA_REF = '/gsc/software/linux-x86_64-centos6/optitype/data/hla_reference_dna.fasta'

    WKDIR = os.getcwd()
    HLA_REF = determine_reference(data_type, DNA_HLA_REF, RNA_HLA_REF)
    make_directory(WKDIR, project, data_type)

    df_patient = pd.read_csv(f, sep='\t')
    make_optitype_scripts(df_patient, data_type,
                          WKDIR, project,
                          TMP_DIR, HLA_REF, run_type)


if __name__ == '__main__':
    __main__()
