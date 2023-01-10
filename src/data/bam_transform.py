# This is a bunch of functions that transform BAM files into base-pair coverage files
# These files are then used to generate a file of flanking sequence (+/- x bp) around each base-pair
import os
import pandas as pd
import csv
from tqdm import tqdm

class BamTransform:

    def __init__(self, data_path, app_path, ssheet_path, dry_run=False):
        self.data_path = data_path
        self.app_path = app_path
        self.ssheet_path = ssheet_path
        self.dry_run = dry_run
        # setup all the directories if they don't exist
        if not os.path.exists(self.data_path + '/coverage'):
            os.makedirs(self.data_path + '/coverage')
        if not os.path.exists(self.data_path + '/concatenated'):
            os.makedirs(self.data_path + '/concatenated')
        if not os.path.exists(self.data_path + '/submission'):
            os.makedirs(self.data_path + '/submission')
        if not os.path.exists(self.data_path + '/logs'):
            os.makedirs(self.data_path + '/logs')

        self.ssheet = pd.read_csv(self.ssheet_path, sep='\t')
        print(self.ssheet)
        return None

    def bam_to_cov(self):
        '''
        Convert a set of BAM files into coverage files and concatenate them into a single file. 
        Use bedtools genomecov to generate coverage files.
        '''
        for sample in self.ssheet['SampleName_inExp'].head():
            cmd = f'''#! /usr/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --mem=32000
#SBATCH --account=scripps-dept
#SBATCH --qos=scripps-dept
#SBATCH --time=10:00:00
#SBATCH --output={self.data_path + '/logs/'}slurm-%j.out
module load bedtools;
bedtools genomecov -ibam {self.data_path}/bams/{sample}.bam -d > {self.data_path}/coverage/{sample}.cov;
            '''
            f = open(self.data_path + '/submission/' + sample + '.cov.sh', 'w')
            f.write(cmd)
            f.close()
            if self.dry_run:
                print(f'Script created for {sample}')
            else:
                os.system(f'sbatch {self.data_path}/submission/{sample}.cov.sh')
                # print(f'sbatch {self.data_path}/submission/{sample}.cov.sh')
        return None

    def make_multivcov_bed(self, sizes, outfile):
        '''
        Bedtools multicov needs a BED file of intervals that we are interested in. Here we are making a 
        BED file with each interval corresponding to a bp in the genome. 
        '''
        genome_sizes = {}
        with open(sizes, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                chrom, size = row
                genome_sizes[chrom] = int(size)

        # Open the output BED file for writing
        with open(outfile, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            # Iterate through the chromosomes in the genome sizes dictionary
            for chrom in genome_sizes:
                size = genome_sizes[chrom]
                # Write a BED entry for each base pair in the chromosome
                for i in tqdm(range(size), desc=f"Writing BED entries for {chrom}", leave=False):
                    writer.writerow([chrom, i, i + 1])
        
        return None 
    
    def bam_to_multicov(self):
        '''
        Convert a set of BAM files into coverage files and concatenate them into a single file. 
        Use bedtools multicov to generate coverage files.
        '''
        for sample in self.ssheet['SampleName_inExp']:
            cmd = f'''#! /usr/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --mem=32000
#SBATCH --account=scripps-dept
#SBATCH --qos=scripps-dept
#SBATCH --time=10:00:00
#SBATCH --output={self.data_path + '/logs/'}slurm-%j.out
module load bedtools;

            '''
            f = open(self.data_path + '/submission/' + sample + '.cov.sh', 'w')
            f.write(cmd)
            f.close()
            if self.dry_run:
                print(f'Script created for {sample}')
            else:
                os.system(f'sbatch {self.data_path}/submission/{sample}.cov.sh')
                # print(f'sbatch {self.data_path}/submission/{sample}.cov.sh')
        return None