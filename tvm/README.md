
# TVM AI
This project contains a multi-agent AI system powered by [CrewAI](https://docs.crewai.com/introduction) and [FastAPI](https://fastapi.tiangolo.com/). The goal of this project is to rewrite texts using AI with the help of templates and make this accessible using an API.

## Installation
Ensure you have Python >=3.10 <3.13 installed on your system, any other version will result in unexpected errors. This project uses UV for dependency management and package handling, offering a seamless setup and execution experience.

### Installing UV
First, if you haven't already, install uv:

**On windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex
```

**On MacOS/Linux:**

Using curl
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Alternatively using wget
```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

If you run into any issues, refer to [UV's installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more information.

### Installing CrewAI
Run the following command to install CrewAI
```bash
uv tool install crewai
```

If you encounter a PATH warning, run this command to update your shell:
```bash
uv tool update-shell
```

If you encounter the chroma-hnswlib==0.7.6 build error (fatal error C1083: Cannot open include file: 'float.h') on Windows, install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) with Desktop development with C++.

To verify that crewai is installed, run:
```bash
uv tool list
```

You should see something like:
```
crewai v0.102.0
- crewai
```

#### Updating
If you need to update crewai, run:
```bash
uv tool install crewai --upgrade
```

### Installing dependencies
This project uses UV for dependency management. To setup a venc and install all dependencies run:
```bash
crewai install
```

## Setup environment variables
This projects includes a .env.dist, this documents includes examples of possible entries. At a minimum, an LLM must be specified, a random secret value added, the allowed origins set, and a database connection string provided.

## Run the application
First activate the venv by runnning:
```bash
.venv\Scripts\activate
```

To start the application run:
```bash
cd src/tvm
```
```bash
uvicorn main:app
```