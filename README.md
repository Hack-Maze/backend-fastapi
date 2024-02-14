# HackMaze Backend

### Input variables

The generator (cookiecutter) will ask you for some data, you might want to have at hand before generating the project.

The input variables, with their default values (some auto generated) are:

* `project_name`: The name of the project
* `project_slug`: The development friendly name of the project. By default, based on the project name
* `domain_main`: The domain in where to deploy the project for production (from the branch `production`), used by the load balancer, backend, etc. By default, based on the project slug.
* `domain_staging`: The domain in where to deploy while staging (before production) (from the branch `master`). By default, based on the main domain.

* `docker_swarm_stack_name_main`: The name of the stack while deploying to Docker in Swarm mode for production. By default, based on the domain.
* `docker_swarm_stack_name_staging`: The name of the stack while deploying to Docker in Swarm mode for staging. By default, based on the domain.

* `secret_key`: Backend server secret key. Use the method above to generate it.
* `first_superuser`: The first superuser generated, with it you will be able to create more users, etc. By default, based on the domain.
* `first_superuser_password`: First superuser password. Use the method above to generate it.
* `backend_cors_origins`: Origins (domains, more or less) that are enabled for CORS (Cross Origin Resource Sharing). This allows a frontend in one domain (e.g. `https://dashboard.example.com`) to communicate with this backend, that could be living in another domain (e.g. `https://api.example.com`). It can also be used to allow your local frontend (with a custom `hosts` domain mapping, as described in the project's `README.md`) that could be living in `http://dev.example.com:8080` to communicate with the backend at `https://stag.example.com`. Notice the `http` vs `https` and the `dev.` prefix for local development vs the "staging" `stag.` prefix. By default, it includes origins for production, staging and development, with ports commonly used during local development by several popular frontend frameworks (Vue with `:8080`, React, Angular).
* `smtp_port`: Port to use to send emails via SMTP. By default `587`.
* `smtp_host`: Host to use to send emails, it would be given by your email provider, like Mailgun, Sparkpost, etc.
* `smtp_user`: The user to use in the SMTP connection. The value will be given by your email provider.
* `smtp_password`: The password to be used in the SMTP connection. The value will be given by the email provider.
* `smtp_emails_from_email`: The email account to use as the sender in the notification emails, it would be something like `info@your-custom-domain.com`.
 
* `postgres_password`: Postgres database password. Use the method above to generate it. (You could easily modify it to use MySQL, MariaDB, etc).
* `pgadmin_default_user`: PGAdmin default user, to log-in to the PGAdmin interface.
* `pgadmin_default_user_password`: PGAdmin default user password. Generate it with the method above.
 
* `traefik_constraint_tag`: The tag to be used by the internal Traefik load balancer (for example, to divide requests between backend and frontend) for production. Used to separate this stack from any other stack you might have. This should identify each stack in each environment (production, staging, etc).
* `traefik_constraint_tag_staging`: The Traefik tag to be used while on staging.
* `traefik_public_constraint_tag`: The tag that should be used by stack services that should communicate with the public.

* `flower_auth`: Basic HTTP authentication for flower, in the form`user:password`. By default: "`admin:changethis`".

* `sentry_dsn`: Key URL (DSN) of Sentry, for live error reporting. You can use the open source version or a free account. E.g.: `https://1234abcd:5678ef@sentry.example.com/30`.

* `docker_image_prefix`: Prefix to use for Docker image names. If you are using GitLab Docker registry it would be based on your code repository. E.g.: `git.example.com/development-team/my-awesome-project/`.
* `docker_image_backend`: Docker image name for the backend. By default, it will be based on your Docker image prefix, e.g.: `git.example.com/development-team/my-awesome-project/backend`. And depending on your environment, a different tag will be appended ( `prod`, `stag`, `branch` ). So, the final image names used will be like: `git.example.com/development-team/my-awesome-project/backend:prod`.
* `docker_image_celeryworker`: Docker image for the celery worker. By default, based on your Docker image prefix.
* `docker_image_frontend`: Docker image for the frontend. By default, based on your Docker image prefix.

## How to deploy

This stack can be adjusted and used with several deployment options that are compatible with Docker Compose, but it is designed to be used in a cluster controlled with pure Docker in Swarm Mode with a Traefik main load balancer proxy handling automatic HTTPS certificates, using the ideas from <a href="https://dockerswarm.rocks" target="_blank">DockerSwarm.rocks</a>.

Please refer to <a href="https://dockerswarm.rocks" target="_blank">DockerSwarm.rocks</a> to see how to deploy such a cluster in 20 minutes.

