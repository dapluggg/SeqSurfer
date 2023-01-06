# This is a bunch of functions that transform BAM files into base-pair coverage files
# These files are then used to generate a file of flanking sequence (+/- x bp) around each base-pair
import os


class BamTransform:

    def __init__(self, data_path, app_path, ssheet, dry_run=False):
        self.data_path = data_path
        self.app_path = app_path
        self.ssheet = ssheet
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
        
        return None

    def bam_to_cov(self, bam_list):
        '''
        Convert a set of BAM files into coverage files and concatenate them into a single file. 
        Use bedtools genomecov to generate coverage files.
        '''
        print('test')
        for sample in bam_list:
            cmd = f'''#! /usr/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --mem=32000
#SBATCH --account=scripps-dept
#SBATCH --qos=scripps-dept
#SBATCH --time=10:00:00
#SBATCH --output={self.data_path + '/logs/'}slurm-%j.out
module load bedtools;
bedtools genomecov -ibam {sample} -d > {self.data_path}/coverage/{sample}.cov;
            '''
            f = open(self.data_path + '/submission/' + sample + '.cov.sh', 'w')
            f.write(cmd)
            f.close()
            if self.dry_run:
                print(f'Script created for {sample}')
            else:
                os.system(f'sbatch {self.data_path} + "/submission/" + sample + ".cov.sh"')
                
        return None