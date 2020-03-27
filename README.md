# WWT Squid Proxy Server

This repository contains setup for a backend component of the [AAS]
[WorldWide Telescope] web services.

[AAS]: https://aas.org/
[WorldWide Telescope]: http://worldwidetelescope.org/

In particular, the core WWT operates a web proxy to allow the interactive web
client to fetch data from remote servers in the cases when the web browser
would prohibit direct access, because of:

- [CORS] restrictions
- insecure content (`http://`) being loaded from a secure origin (`https://`)

[CORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

This web proxy is implemented as a Docker container running a specially
configured version of the [Squid] proxy server. This proxy is itself
reverse-proxied through an [Azure Application Gateway] so that everything can
be served from the core domain.

[Squid]: http://www.squid-cache.org/
[Azure Application Gateway]: https://azure.microsoft.com/en-us/services/application-gateway/


## Building / Installation

This isn't really software that "install" yourself. The output artifact of
this repository is a Docker image that you obtain with the command:

```
docker build -t aasworldwidetelescope/proxy:latest .
```

The main purpose of this pipeline is to automate the build and publication of
this image through the `azure-pipelines.yml` file. The image ultimately
emerges as
[aasworldwidetelescope/proxy](https://hub.docker.com/repository/docker/aasworldwidetelescope/proxy).
A webhook is configured there to update the running service on Azure.


## Contributions

Contributions are welcome! See [the WorldWide Telescope contributors’ guide]
for applicable information. We use a standard workflow with issues and pull
requests. All participants in this repository and the WWT communities must
abide by the [WWT Code of Conduct].

[the WorldWide Telescope contributors’ guide]: https://worldwidetelescope.github.io/contributing/
[WWT Code of Conduct]: https://worldwidetelescope.github.io/code-of-conduct/


## Legalities

The files in this repository are copyright the .NET Foundation, licensed under
the [MIT License](./LICENSE).


## Acknowledgments

`wwt-squid-proxy` is part of the AAS WorldWide Telescope system, a
[.NET Foundation] project managed by the non-profit
[American Astronomical Society] (AAS). Work on WWT has been supported by the
AAS, the US [National Science Foundation] (grants [1550701] and [1642446]),
the [Gordon and Betty Moore Foundation], and [Microsoft].

[.NET Foundation]: https://dotnetfoundation.org/
[American Astronomical Society]: https://aas.org/
[National Science Foundation]: https://www.nsf.gov/
[1550701]: https://www.nsf.gov/awardsearch/showAward?AWD_ID=1550701
[1642446]: https://www.nsf.gov/awardsearch/showAward?AWD_ID=1642446
[Gordon and Betty Moore Foundation]: https://www.moore.org/
[Microsoft]: https://www.microsoft.com/
