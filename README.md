# COE 332 - Project

- Bradley Bridges - blb3664
- Paige Williams - pnw268

[![Build Status](https://travis-ci.com/bbridges/coe332-blb3664-pnw268.svg?branch=master)](https://travis-ci.com/bbridges/coe332-blb3664-pnw268)

## Directory Layout

- `project/` - Python source files for the API and worker
- `bin/` - Startup scripts for the `Dockerfile`s.
- `test/` - Contains unit and integration tests from previous homeworks.

## Building

Run `make` to build and tag the API and worker containers.

## Documentation

See https://bbridges.github.io/coe332-blb3664-pnw268 for user documentation and
[DEPLOYING.md](./DEPLOYING.md) for deployment documentation.

## API Spec

The API spec is defined in [openapi.yaml](./openapi.yaml) and generated with
[ReDoc](https://github.com/Rebilly/ReDoc). You can view it at
https://bbridges.github.io/coe332-blb3664-pnw268 via GitHub Pages. (The
generated output is not checked into the repository)

### Building

To build the HTML API spec output, you'll need to install `redoc-cli` with
`npm`. (This requires Node.js.)

```sh
$ npm install -g redoc-cli
```

To serve the contents and have them rebuild on changes, you can run

```sh
$ redoc-cli serve openapi.yaml --watch
```

and view the HTML at http://localhost:8080.

To build a static HTML file, you can use

```sh
$ redoc-cli bundle openapi.yaml
```

and it will generate a file called `redoc-static.html`.

This process is automated with [Travis CI](https://travis-ci.com) on each push
to master and the static output is hosted with GitHub Pages.
