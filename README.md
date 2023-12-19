# Financify

[![Tests](https://github.com/software-students-fall2023/5-final-project-generators/actions/workflows/test.yml/badge.svg)](https://github.com/software-students-fall2023/5-final-project-generators/actions/workflows/test.yml)

# Team Members

* [Aavishkar Gautam](https://github.com/aavishkar6)
* [Avaneesh Devkota](https://github.com/avaneeshdevkota)
* [Seolin Jung](https://github.com/seolinjung)
* [Soyuj Jung Basnet](https://github.com/basnetsoyuj)

# Description

Financify is a web application designed to simplify the process of splitting bills among friends and acquaintances. Tired of the hassle of keeping track of who owes whom after a group dinner, trip, or any shared expenses? Financify has you covered. Financify allows users to easily manage and settle debts, ensuring that everyone pays and gets paid accurately.

## Setup

### Prerequisites

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Running the application

1. Clone the repository
    ```shell
    git clone https://github.com/software-students-fall2023/5-final-project-generators.git
    ```
2. Navigate to the project directory
    ```shell
    cd 5-final-project-generators
    ```
3. Setup the environment variables
    ```shell
    cp .env.example .env
    ```
4. Build the images
    ```shell
    docker-compose build
    ```
5. Run the containers
    ```shell
    docker-compose up -d
    ```
6. Open the application in your browser
    ```shell
    http://localhost:8001
    ```
7. To stop the containers
    ```shell
    docker-compose stop
    ```
   
OR

### Accessing the deployed application

1. Open the application in your browser: [http://165.227.185.104:8001/](http://165.227.185.104:8001/)

## Notes and Links

* Link to the Task Board:
    * [Project Board](https://github.com/orgs/software-students-fall2023/projects/104/views/1?layout=board)
* The Web App is tested using Github Actions on every push to the main branch and approved pull requests.
