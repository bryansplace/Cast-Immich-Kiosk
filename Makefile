# Usage
#make login                        
# authenticate with GHCR
#

#make dev                          
# build and run locally on port 7861

#make down                         
# stop dev container

#make push m="fix signal handler"  
# commit and push to GitHub

#make release v=v1.0.0
# tag and push a versioned release

#make tag                          
# show last tag



.PHONY: login dev down push release tag

# log in to github container registry
login:
	docker login ghcr.io -u bryansplace

# build and run dev container locally on port 7861
dev:
	docker stop immich-kiosk-cast || true
	docker rm immich-kiosk-cast || true
	docker compose -f docker-compose.yaml up --build

# stop dev container
down:
	docker compose -f docker-compose.dev.yaml down

# commit and push to github (triggers Actions build of :latest)
# usage: make push m="your commit message"
push:
	@echo "Last tag: $$(git describe --tags --abbrev=0 2>/dev/null || echo 'none')"
	git add -A
	git commit -m "$(m)"
	git push

# tag a release and push (triggers Actions versioned build)
# usage: make release v=v1.0.0
release:
	@echo "Last tag: $$(git describe --tags --abbrev=0 2>/dev/null || echo 'none')"
	git tag $(v)
	git push origin $(v)

# show last tag
tag:
	@git describe --tags --abbrev=0 2>/dev/null || echo "no tags yet"
