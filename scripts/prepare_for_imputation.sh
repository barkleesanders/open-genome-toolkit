#!/usr/bin/env bash
# Convert a consumer DNA export into per-chromosome VCF files ready to upload
# to a free imputation server.
#
# WHY IMPUTATION IS THE STEP THAT MATTERS
#   A consumer DNA chip genotypes roughly 600,000-700,000 positions. A published
#   polygenic score often uses hundreds of thousands to millions of variants, so
#   scoring a raw chip file directly can miss most of the score. Imputation uses
#   a reference panel of sequenced genomes to statistically infer the positions
#   your chip did not measure, taking you from ~600k to tens of millions of
#   variants. Free academic servers do this for you.
#
# WHAT THIS SCRIPT DOES NOT DO
#   It does not reimplement genomics. It drives plink2 and bcftools, which are
#   the established tools, and it fails loudly when a prerequisite is missing
#   rather than producing a file that looks right and is wrong.
#
# THE GENOME BUILD TRAP -- read this before you run anything
#   Coordinates differ between reference builds. Most consumer exports are on
#   GRCh37/hg19. Imputation servers ask which build you are submitting, and
#   choosing wrong yields output that is silently garbage: the file loads, the
#   numbers compute, and every position is misaligned. Confirm your build from
#   your export's own header before submitting. Do not guess.
#
# Usage:
#   scripts/prepare_for_imputation.sh raw_export.txt output_dir/
#   scripts/prepare_for_imputation.sh --check     # prerequisites only

set -euo pipefail

die() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
warn() { printf '\033[33mwarning:\033[0m %s\n' "$*" >&2; }
info() { printf '\033[36m==>\033[0m %s\n' "$*"; }

check_prereqs() {
  local missing=0
  info "checking prerequisites"
  for tool in plink2 bcftools bgzip; do
    if command -v "$tool" >/dev/null 2>&1; then
      printf '  ok      %-10s %s\n' "$tool" "$(command -v "$tool")"
    else
      printf '  MISSING %-10s\n' "$tool"
      missing=1
    fi
  done
  if [ "$missing" -eq 1 ]; then
    cat >&2 <<'EOF'

Install the missing tools:
  macOS (Homebrew):   brew install plink2 bcftools htslib
  Debian/Ubuntu:      sudo apt install plink2 bcftools tabix
  conda/bioconda:     conda install -c bioconda plink2 bcftools htslib

plink2 homepage:   https://www.cog-genomics.org/plink/2.0/
bcftools homepage: https://samtools.github.io/bcftools/
EOF
    return 1
  fi
  return 0
}

detect_build() {
  # Consumer exports state their reference build in the comment header.
  # Reporting what the file says beats assuming.
  local f="$1" header
  header=$(head -c 8000 "$f" 2>/dev/null | grep '^#' || true)
  if grep -qiE 'build 3[78]|grch38|hg38' <<<"$header"; then
    echo "GRCh38"
  elif grep -qiE 'build 3[67]|grch37|hg19' <<<"$header"; then
    echo "GRCh37"
  else
    echo "UNKNOWN"
  fi
}

if [ "${1:-}" = "--check" ]; then
  check_prereqs && printf '\n\033[32mAll prerequisites present.\033[0m\n'
  exit $?
fi

RAW="${1:-}"
OUTDIR="${2:-}"
[ -n "$RAW" ] && [ -n "$OUTDIR" ] || die "usage: $0 <raw_export.txt> <output_dir/>  (or --check)"
[ -f "$RAW" ] || die "no such file: $RAW"

check_prereqs || die "install the missing tools above, then re-run"

BUILD=$(detect_build "$RAW")
info "reference build declared by your file: $BUILD"
if [ "$BUILD" = "UNKNOWN" ]; then
  warn "could not read a build from the file header."
  warn "Find it before submitting -- an imputation run on the wrong build is silently wrong."
  warn "Most consumer exports from the last decade are GRCh37/hg19, but verify yours."
fi

mkdir -p "$OUTDIR"
cd "$OUTDIR"
OUTDIR_ABS="$PWD"
RAW_ABS="$(cd "$(dirname "$RAW")" && pwd)/$(basename "$RAW")"

info "converting export to plink binary format"
# --23file reads the 23andMe layout directly. AncestryDNA and MyHeritage
# exports must be converted to that layout first; normalize_raw_dna.py plus a
# small awk step does this, see references/dna-analysis-pipeline.md.
plink2 --23file "$RAW_ABS" --make-bed --out genome_raw --silent \
  || die "plink2 could not read this file. If it is not a 23andMe-format export, see references/dna-analysis-pipeline.md"

info "applying basic quality control"
# Drop unplaced/mitochondrial contigs and any position the chip failed to call.
# --snps-only removes indels, which imputation servers reject.
plink2 --bfile genome_raw \
       --snps-only just-acgt \
       --chr 1-22 \
       --geno 0.1 \
       --make-bed --out genome_qc --silent \
  || die "quality-control step failed"

info "splitting into per-chromosome VCF files"
for chr in $(seq 1 22); do
  plink2 --bfile genome_qc --chr "$chr" --recode vcf bgz --out "chr${chr}" --silent 2>/dev/null || {
    warn "chromosome $chr produced no output (no variants after QC) -- skipping"
    rm -f "chr${chr}".* 2>/dev/null || true
    continue
  }
  printf '  chr%-2s %s\n' "$chr" "$(ls -lh "chr${chr}.vcf.gz" 2>/dev/null | awk '{print $5}')"
done

info "sorting and indexing"
for f in chr*.vcf.gz; do
  [ -e "$f" ] || continue
  bcftools sort "$f" -Oz -o "sorted_$f" 2>/dev/null && mv "sorted_$f" "$f"
  bcftools index -f "$f" 2>/dev/null || warn "could not index $f"
done

count=$(ls chr*.vcf.gz 2>/dev/null | wc -l | tr -d ' ')
[ "$count" -gt 0 ] || die "no VCF files were produced -- check the errors above"

cat <<EOF

$(printf '\033[32mDone.\033[0m') ${count} per-chromosome VCF files are in: ${OUTDIR_ABS}

NEXT STEP -- upload to a free imputation server
  Both servers below are run by academic groups, require a free account, and
  process your data on their infrastructure. Read their terms first: you are
  sending your genome to a third party.

    TOPMed Imputation Server    https://imputation.biodatacatalyst.nhlbi.nih.gov/
    Michigan Imputation Server  https://imputationserver.sph.umich.edu/

  When you submit, you must select the reference build. Your file declares:
  ${BUILD}
  If that says UNKNOWN, resolve it before submitting.

  Results come back as per-chromosome dose.vcf.gz files, usually password
  protected, with the password emailed separately. Expect hours, not minutes.

  If you would rather not send your genome to a server, imputation can be run
  locally with Beagle or Minimac4 plus a public reference panel. It is slower
  and needs far more disk and RAM. See references/dna-analysis-pipeline.md.
EOF
