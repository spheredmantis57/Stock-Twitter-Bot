# Stock Twitter Bot

## Introduction
This project is to make take a stock ticker and tweet statistics to a twitter account.

## Table of Contents
Provide a table of contents to help users navigate through the README.

1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
4. [How it Works](#how-it-works)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

NOTE: This can be ran directly from python, but you can make an executable

In the top-level directory:
```sh
make
```

There will now be a release folder that holds your executable

To clean up:
```sh
make clean
```

## Usage

usage: main.py [-h] --log LOG --config CONFIG --mode {AMC,GME} [--ndebug]

Arguments:
-  -h, --help        show this help message and exit
-  --log LOG         The path to the log file
-  --config CONFIG   The path to the config json
-  --mode {AMC,GME}  Choose the ticker to get data for
-  --ndebug          Will actually send the tweet

## Configuration

1. Look at the TOP-LEVEL/twitter/.config_TEMPLATE.json for the lay out of how the config file should be.
2. Set up a twitter bot account
    1. Create a new twitter account
    2. In the Settings, click "Your Account"
    3. Click "Account Information"
    4. Click "Automation" and read/agree
    5. Following what you just read, link the human account to your twitter account
    6. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) to sign up for a free developer account
3. From the default project made, click the default App and navigate the the Apps "Keys and Tokens
4. Fill in your config json with the keys and tokens

## How it Works
Upon execution, stock statistics will be pulled, formatted, and tweeted. You can make this a job to have it tweet at desired days and times.

In Linux, starting it as a chon job to run every weekday at 0830:
```sh
sudo crontab -e
# 1 for nano
# Put following line in:
30 8 * * 1-5 [PROGRAM FULL PATH AND ARGS]
# Save and Close
```

## Contact Information
Github: [spheredmantis57](https://github.com/spheredmantis57)
LinkedIn: [Randall Dowling](https://www.linkedin.com/in/randall-dowling/)
