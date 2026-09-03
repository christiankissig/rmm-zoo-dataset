# rmm-zoo-dataset — the Relaxed Memory Model Zoo dataset
# Plain data: the src/ tree (one file per model and per edge) compiled into
# models.json, plus the litmus witness tree compiled into litmus.json.
# No bundler, no dependencies — Python 3 for the gate and the generators, and
# herd7 (optional) to run the witnesses.
#
# The site that renders this dataset lives in a separate repository and consumes
# the published artifacts; nothing here knows how the graph is drawn.

DIST   := dist
# Published under the site's origin so the map fetches it same-origin (no CORS).
# The site deploy excludes this prefix, and this deploy only ever writes it.
BUCKET ?= kissig-org-rmm-zoo
PREFIX ?= data
# CloudFront distribution fronting the bucket (alias rmm-zoo.kissig.org).
# Set DISTRIBUTION= (empty) to skip the post-deploy cache invalidation.
DISTRIBUTION ?= E3PXGEAO2HVOM3

# The version is stamped in at build time from the git tag (tools/version.py) —
# models.json and CITATION.cff.in are templates. A local `make build` happily
# stamps a dev version; `make deploy` sets the gate below (target-specific, so it
# reaches the build it depends on) and refuses anything but a clean tagged
# release. ALLOW_DEV=1 lifts that, for a deliberate off-tag publish.
ALLOW_DEV ?=
RELEASE_GATE :=

.PHONY: help version models litmus kater memalloy check build deploy clean

help:
	@echo "rmm-zoo-dataset targets:"
	@echo "  make version          Print the version + date this build would stamp in"
	@echo "  make models           Regenerate models.json from the src/ sources"
	@echo "  make litmus           Regenerate litmus.json from the litmus/ test tree"
	@echo "  make kater            Re-prove the kater-provenance containments (needs docker + the image)"
	@echo "  make memalloy         Re-run the memalloy-provenance comparisons (needs MEMALLOY=<checkout>)"
	@echo "  make check            Verify the dataset: DAG, no contradictions, witness direction, litmus + kater suites"
	@echo "  make build            Stamp the version and assemble the artifacts into $(DIST)/$(PREFIX)/ (runs check first)"
	@echo "  make deploy           Build, sync $(DIST)/$(PREFIX)/ to s3://$(BUCKET)/$(PREFIX)/, invalidate CloudFront"
	@echo "  make clean            Remove $(DIST)/"

# What `make build` would stamp in: the tag on HEAD, or a dev version off it.
version:
	@python3 tools/version.py

# Compile the src/ tree — one file per model, one per edge, plus the shared
# bibliography and property schema — into models.json. Committed, like
# litmus.json, so a consumer gets the built dataset without running the build;
# `make check` fails if the committed copy has fallen behind the sources.
models:
	@python3 tools/gen-models.py

# Bake the litmus/ test tree into litmus.json (committed, so a consumer gets the
# built artifact without running the generator). Re-run whenever tests change.
litmus:
	@python3 tools/gen-litmus.py

# Re-decide every containment recorded as provenance "kater" from its query file.
# Separate target because it wants docker and a ~700MB image; `make check` folds
# it in automatically once the image is local, and skips it otherwise.
kater:
	@bash litmus/kater/run.sh

# Re-decide every comparison recorded as provenance "memalloy". Kept out of
# `make check` deliberately: unlike kater it needs a built source checkout, not
# just a pulled image, and the containment cases run for minutes.
memalloy:
	@MEMALLOY="$(MEMALLOY)" bash litmus/memalloy/run.sh

# Fail-fast gate over models.json + litmus/: acyclicity, no ordered/incomparable
# contradiction, property, cat- and kat-support integrity, every witness directory
# matching its edge's type and direction, every kater claim backed by its query,
# and — where the tools are installed — the litmus and kater suites themselves.
# Preceded by the cheaper structural gate: models.json must be exactly what the
# src/ sources compile to, so nobody edits the generated artifact by hand and
# nobody publishes sources that were never built.
# A build/deploy aborts rather than publish an inconsistent dataset.
check:
	@python3 tools/gen-models.py --check
	@python3 tools/check-consistency.py

# Build == stamp the version into the templates and stage the published files
# under the prefix they are served at, so `aws s3 sync` maps directories to keys
# one-to-one. CITATION.cff is rendered here rather than committed: it is served
# beside the data it cites, so its version can never lag the dataset's.
build: check clean litmus
	@python3 tools/render.py $(DIST)/$(PREFIX) $(RELEASE_GATE)

# Publish the dataset only. --delete is safe here because the destination is the
# data/ prefix itself: it can never reach the site's objects, which live outside
# it. (The site's own deploy is the mirror image — it excludes data/*.)
deploy: RELEASE_GATE := $(if $(strip $(ALLOW_DEV)),,--require-release)
deploy: build
	@echo "Syncing $(DIST)/$(PREFIX)/ -> s3://$(BUCKET)/$(PREFIX)/"
	aws s3 sync $(DIST)/$(PREFIX)/ s3://$(BUCKET)/$(PREFIX)/ --delete \
	    --cache-control "public, max-age=300"
ifneq ($(strip $(DISTRIBUTION)),)
	@echo "Invalidating CloudFront cache ($(DISTRIBUTION)) for /$(PREFIX)/*"
	aws cloudfront create-invalidation --distribution-id $(DISTRIBUTION) --paths "/$(PREFIX)/*" \
	    --query 'Invalidation.{Id:Id,Status:Status}' --output text
endif
	@echo "Done — https://rmm-zoo.kissig.org/$(PREFIX)/models.json"
	@echo "       https://rmm-zoo.kissig.org/$(PREFIX)/CITATION.cff (version-stamped by this deploy)"

clean:
	@rm -rf $(DIST)
