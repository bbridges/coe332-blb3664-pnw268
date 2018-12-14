# Deploying the Project

This contains two ways to deploy redis, the API, and the workers:

- One docker instance on a single machine.
- Multiple docker instances in a swarm.

It is assume Docker and docker-compose are installed on all machines.

## Single Docker Instance

You can run a basic setup on a single instance by using docker-compose.

Running `docker-compose up` in the top-level directory will start the services
listed in `docker-compose.yml`.

This will map port `:5000` from the api onto the host.

To bring down the services, run `docker-compose down`.

## Multiple Docker Instances

This uses Docker Swarm to spin up services across a manager and worker nodes.

The following ports must be available for Docker Swarm:

- **TCP `:2377`**
- **TCP and UDP `:7946`**
- **UDP `:4789`**

To create a swarm, run the following with the IP for the manager node:

```shell
$ docker swarm init --advertise-addr <manager-ip>
```

Afterwards, use the join command that prints out on the workers nodes you would 
like to attach to the swarm.

Note that this is note strictly required as this can remain a single-node
swarm.

Then, to bring up the services, deploy a new stack using the
`docker-compose.yml` file from the top-level directory:

```shell
$ docker stack deploy --compose-file docker-compose.yml coe332-project
```

This will distribute the services across the manager and worker nodes that
joined.

Note that the API will always be on the manager node, and has it's port exposed
on `:5000`.

The stack can be removed with

```shell
$ docker stack rm coe332-project
```

To change the number of workers (defaulting to 5) you can scale them:

```shell
$ docker stack scale coe332-project_worker=10  # 10 workers now
```
