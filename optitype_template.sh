#! /bin/bash -l
#SBATCH --job-name={{patient}}_{{library}}
#SBATCH -o %x.o%j
#SBATCH -e %x.e%j
#SBATCH --mem=350G
#SBATCH --export=ALL

SAMTOOLS=/gsc/software/linux-x86_64-centos5/samtools-1.0/bin/samtools
RAZERS3=/gsc/software/linux-x86_64-centos6/optitype/razers3
#RNA_HLA_REF=/gsc/software/linux-x86_64-centos6/optitype/data/hla_reference_rna.fasta
#DNA_HLA_REF=/gsc/software/linux-x86_64-centos6/optitype/data/hla_reference_dna.fasta

HLA_REF={{HLA_REF}}
OPTITYPE=/gsc/software/linux-x86_64-centos6/optitype/OptiTypePipeline.py
VIRTUAL_ENV=/projects/epleasance/POG/hpearson/optitype/OptiTypeVE/bin/activate

SECONDS=0
echo "Start processing:{{patient}}_{{library}}!"
echo "Aligning read1 to HLA reference sequences with razers3! Please be patient!"
$RAZERS3 -i 95 -m 1 -dr 0 -o {{patient}}_{{library}}_1.bam $HLA_REF {{fq1}}
echo "Aligning read2 to HLA reference sequences with razers3! Please be patient!"
$RAZERS3 -i 95 -m 1 -dr 0 -o {{patient}}_{{library}}_2.bam $HLA_REF {{fq2}}

echo "Converting filtered bam to fastq format for optitype!"
$SAMTOOLS bam2fq {{patient}}_{{library}}_1.bam  > {{patient}}_{{library}}_1_razer3_filtered.fastq
$SAMTOOLS bam2fq {{patient}}_{{library}}_2.bam  > {{patient}}_{{library}}_2_razer3_filtered.fastq

echo "activate optitype virtual environment!"
source $VIRTUAL_ENV

echo "Running optitype, This may take a few hours. Be patient!"
python $OPTITYPE \
	-i {{patient}}_{{library}}_1_razer3_filtered.fastq {{patient}}_{{library}}_2_razer3_filtered.fastq \
	--{{run_type}} --enumerate 3 -v \
	-o /projects/trans_scratch/validations/optitype/{{project}}/{{data_type}}/{{patient}}_{{library}}
echo "deactivate optitype virtual environment!"

deactivate

if [ $? -eq 0 ];then
    echo "optitype job finished successfully at:" `date`
else
    echo "ERROR? Please review log file for non-zero exit status!"
fi
duration=$SECONDS
echo "It takes $(($duration / 60)) minutes and $(($duration % 60)) seconds to finish the job."
