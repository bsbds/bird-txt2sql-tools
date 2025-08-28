# text to sql tools

## Usage

### Download `dev_databases`

Download from [google drive
](https://drive.google.com/file/d/13VLWIwpw5E3d5DUkMvzw7hvHE67a4XkG/view?usp=sharing)

extract and place `MINIDEV/dev_databases` in the root folder of this project

### Generate Bird Dataset Subset

``` sh
./run_gen.sh 3 5 2
```

This command generates a subset of the bird dataset with 3 simple questions, 5 moderate questions, and 2 challenging questions, following the original distribution in the BIRD dataset.


### Agent Setup

Implement and execute your agent using the [bird_runner](./bird_runner/README.md). This will generate an `output.json` in the root path.

### Run Evaluation

Execute this script to evaluate your agent's performance against the generated dataset.

``` sh
./run_evaluation.sh
```
