# Replication-Kuramoto2023EMSE
This repository contains the resources used in our EMSE project (details can be found in the paper).

## Notice
This dataset may be transferred to zenodo.

## Overview
The package includes the following components:

- GithubIssues Dataset: 
    The GithubIssues dataset consists of GitHub issues obtained from popular projects between 2017 and 2022.06. We selected 34 publicly available projects that have more than 10,000 closed issues since 2017. The data collection was performed using PyGitHub and GitHub API v3.

- Script: 
    The get_attribute.py script is provided to retrieve metrics from the dataset. You have the flexibility to customize it according to your requirements. Please refer to the Requirements section below for information on the necessary libraries.

- Manual Coding Results: 
    The results of our manual coding can be found in the manualCoding directory.

## GithubIssues Dataset Structure
The GithubIssues dataset has the following structure:
```
- GithubIssues/
    - Project/_issues.json/
        - issue#:
            - created_at // refers to the time at the issue creation.
            - closed_at // refers to the time at the issue closure.
            - user // includes the reporter info, we use "login" element.
            - body // refers to the issue description.
            - labels // includes issue tags info, we use "name" element.
            - images // refers to the number of images in the issue description.
            - videos // refers to the number of videos in the issue description.
            - ...
            - comments_dict:
                - comment#:
                    - created_at // refers to the time at the comment.
                    - user // includes the commenter info, we use "login" element.
                    - body // refers to the comment description.
                - ...
        - ...
    - ...
```
More metadata info can be found in https://pygithub.readthedocs.io/en/latest/.

## Requirements
Our replication package make use of the list of bots (i.e., groundtruthbots.csv) available at https://github.com/mehdigolzadeh/IdentifyBots_ReplicationPackage.
Please download the file and place it directly under clone with the name groundtruthbots.csv.

To run the get_attribute.py script and work with the GithubIssues dataset, the following libraries are required:

- git-lfs (Note: This library is required before downloading this repository.)
- fasttext
- markdown
- py_gfm
- nltk

Please ensure that these libraries are installed in your Python environment before running the script.

For more detailed information on the project and its findings, please refer to the paper.
