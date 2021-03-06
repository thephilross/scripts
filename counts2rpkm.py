#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1"
__author__  = "Philipp Ross"
__contact__ = "philippross369@gmail.com"
__license__ = "Apache v2.0"

# import modules
import os
import sys
import argparse
import subprocess

def main():

	parser = argparse.ArgumentParser(description = "htseq-count raw counts to rpkm values")
	parser.add_argument("-b", "--bam", dest = "bam", help = "BAM file from which counts were generated")
	parser.add_argument("-c", "--counts", dest = "counts", help = "Counts file generated by htseq-count for input bam file")
	parser.add_argument("-g", "--gtf", dest = "gtf", help = "GFF/GTF file that was used as annotation for generating counts")
	parser.add_argument("-i", "--id", dest = "gene_id", help = "If not GTF file what id column should be used for gene id", default = "gene_id") 
	args = parser.parse_args()

	# check for samtools
	p = subprocess.Popen("which samtools", shell=True, stdout=subprocess.PIPE)
	out, err = p.communicate()
	if out is None:
		print >> sys.stderr, "samtools executable not found in your path! Abort!"
		sys.exit(1)
	# get number of mapped reads
	if args.bam:
		p = subprocess.Popen("samtools view -F 4 -c " + args.bam, shell=True, stdout=subprocess.PIPE)
		out, err = p.communicate()
		mapped_reads = int(out)

	# set delimiter based on file format
	if args.gtf:
		if args.gtf.endswith(".gtf"):
			delim = " "
		elif args.gtf.endswith(".gff"):
			delim = "="
	
	if args.gene_id:
		idattr = args.gene_id

	# compute transcript length
	transcript_lengths = dict()
	if args.gtf:
		with open(args.gtf) as gtf:
			for line in gtf:
				line = line.split("\t")
				start = int(line[3])
				end = int(line[4])
				attributes = line[8]
				if attributes.count(idattr) < 1:
					sys.stderr.write("The gene identifier %s can't be found" % (idattr))
					sys.exit(1)
				else:
					attributes = attributes.split(";")
					for attribute in attributes:
						if idattr in attribute:
							gene = attribute.split(delim)[-1].replace("\"", "")
					if gene not in transcript_lengths.keys():
						transcript_lengths[gene] = end - start
					elif gene in transcript_lengths.keys():
						transcript_lengths[gene] += end - start

	if args.counts:
		with open(args.counts) as counts:
			for line in counts:
				line = line.split("\t")
				gene = line[0]
				count = int(line[1])
				if "__" in gene:
					rpkm = count
				else:
					rpkm = (float(count) / transcript_lengths[gene]) * (1.0 / mapped_reads) * (10**9)
				print >> sys.stdout, "%s\t%s" % (gene, str(rpkm))
	

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		sys.stderr.write("User interrupt! Ciao!\n")
		sys.exit(0)
