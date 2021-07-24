
# [kwitcom/neat_bulk_export](https://github.com/kwitcom/neat_bulk_export)

## Application Setup

### Export folder

I have set `/output` as ***optional paths***, this is because it is the easiest way to get started. While easy to use, it has some drawbacks. 
## Usage

Here are some example snippets to help you get started creating a container.

### docker-compose (recommended, [click here for more info](https://docs.linuxserver.io/general/docker-compose))

```yaml
---

```

### docker cli ([click here for more info](https://docs.docker.com/engine/reference/commandline/cli/))

```bash

```

## Parameters

Container images are configured using parameters passed at runtime (such as those above). These parameters are separated by a colon and indicate `<external>:<internal>` respectively. For example, `-p 8080:80` would expose port `80` from inside the container to be accessible from the host's IP on port `8080` outside the container.

| Parameter | Function |
| :----: | --- |
| `-v /output` | Location of exported file on disk |


## Environment variables from files (Docker secrets)

You can set any environment variable from a file by using a special prepend `FILE__`.

As an example:

```bash

```

Will set the environment variable `PASSWORD` based on the contents of the `/run/secrets/mysecretpassword` file.



## Versions

* **07.24.21:** - Initial Release. 