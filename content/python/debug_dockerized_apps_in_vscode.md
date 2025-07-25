---
title: Debugging dockerized Python apps in VSCode
date: 2023-12-22
tags:
    - Python
    - TIL
---

Despite using VSCode as my primary editor, I never really bothered to set up the native
debugger to step through application code running inside Docker containers. Configuring the
debugger to work with individual files, libraries, or natively running servers is
trivial[^1]. So, I use it in those cases and just resort back to my terminal for debugging
containerized apps running locally. However, after seeing a colleague's workflow in a
pair-programming session, I wanted to configure the debugger to cover this scenario too.

I'm documenting this to save my future self from banging his head against the wall trying to
figure it out again.

## Desiderata

I want to start a web app with `docker compose up` and connect the VSCode debugger to it
from the UI. For this to work, along with the webserver, we'll need to expose a debug server
from the app container which the debugger can connect to.

## App layout

For demonstration, I'll go with a simple containerized starlette[^2] app served with
uvicorn[^3]. However, the strategy will be similar for any web app. Here's the app's
directory structure:

```txt
src
├── __init__.py
├── main.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

In `main.py`, we're exposing an endpoint as follows:

```py
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def homepage(request) -> JSONResponse:
    return JSONResponse({"hello": "world"})


app = Starlette(debug=True, routes=[Route("/", homepage)])
```

The `requirement.txt` lists out the runtime dependencies:

```txt
starlette
uvicorn
```

Then the `Dockerfile` builds the application:

```dockerfile
FROM python:3.12-slim-bookworm
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Finally, we orchestrate the app in a `docker-compose.yml` file:

```yml
# docker-compose.yml
version: "3.9"

services:
  web:
    build:
      context: .
      dockerfile: ./Dockerfile

    # This overrides the CMD in the Dockerfile
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - 8000:8000
```

## Add launch.json

Now, in the `.vscode` folder of the project's root directory, add a file named
`launch.json`. Create the folder if it doesn't exist. You can also do this part manually; to
do so:

- Click on the debugger button and then click on _create a launch.json file_.
- Select the _Python_ debugger.
- Finally, select the _Remote Attach_ debug config.

However, if you dislike clicking around, here's the full content of `launch.json` for you to
copy and paste (into `$PWD/.vscode/launch.json`):

```json
{
   "version":"0.2.0",
   "configurations":[
      {
         "name":"Python: Remote Attach",
         "type":"python",
         "request":"attach",
         "connect":{
            "host":"localhost",
            "port":5678
         },
         "pathMappings":[
            {
               "localRoot":"${workspaceFolder}",
               "remoteRoot":"."
            }
         ],
         "justMyCode":true
      }
   ]
}
```

This instructs the VSCode debugger to attach to a debug server running on `localhost`
through port `5678`. The next section will elaborate on how to run the debug server in a
container.

Launch configuration will vary depending on your project and each project needs to be set up
individually. The official doc[^4] lists out all the supported application types with
example configurations. To avoid having to reconfigure the same app repetitively, tracking
the entire `.vscode` directory via source control is probably a good idea.

## Add docker-compose.debug.yml

Next up, we'll need to update the `command` section of `services.web` in the
`docker-compose.yml` to expose the debug server. The debugpy[^5] tool from Microsoft does
that for us.

However, instead of changing the `docker-compose.yml` file for debugging, we can add a
separate file for it named `docker-compose.debug.yml`. Here's the content of it:

```yml
# docker-compose.debug.yml
version: "3.9"

services:
  web:
    build:
      context: .
      dockerfile: ./Dockerfile
    command:
      - "sh"
      - "-c"
      - |
        pip install debugpy -t /tmp \
        && python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678 \
        -m uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - 8000:8000
      - 5678:5678
```

Here:

- `sh -c`: Selects the shell inside the Docker container.
- `pip install debugpy -t /tmp`: Installs the `debugpy` tool into the `/tmp` directory of
  the container.
- `python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678`: Runs `debugpy`, sets it to
  wait for a client connection and listen on all network interfaces at port 5678.
- `-m uvicorn main:app --host 0.0.0.0 --port 8000`: Starts an uvicorn server hosting the
  application defined in `main:app`, making it accessible on all network interfaces at
  port 8000.

## Start the debugger

Before starting the VScode debugger, go to the project root and run:

```sh
docker compose -f docker-compose.debug.yml up
```

Now click on the debugger button and select the `Python: Remote attach` profile to start
debugging. Hack away!

_P.S.: An altruist on Reddit brought to my attention that a more elaborate version of this,
with prettier screenshots, can be found in the official documentation[^6]._

[^1]:
    [Python debugging in VS Code](https://code.visualstudio.com/docs/python/debugging#_debugging-by-attaching-over-a-network-connection)

[^2]: [starlette](https://www.starlette.io/)

[^3]: [uvicorn](https://www.uvicorn.org/)

[^4]:
    [Debug Python within a container](https://code.visualstudio.com/docs/containers/debug-python)

[^5]: [debugpy](https://github.com/microsoft/debugpy/tree/main/src/debugpy)

[^6]:
    [Python in a container](https://code.visualstudio.com/docs/containers/quickstart-python)
