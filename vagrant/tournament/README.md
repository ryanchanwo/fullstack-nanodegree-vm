# Tournament

# Introduction

This tournament system is a small assignment given as part of the [**Intro to Relational
Databases**][udacity_course] course on [Udacity](https://www.udacity.com/).

From the **Project Overview**:

> In this project, you’ll be writing a Python module that uses the PostgreSQL database to
> keep track of players and matches in a game tournament.
>
> You will develop a database schema to store the game matches between players. You will
> then write a Python module to rank the players and pair them up in matches in a tournament.

[udacity_course]: https://www.udacity.com/course/intro-to-relational-databases--ud197

# Installation

You will need [Vagrant](https://www.vagrantup.com/) to launch the VM. More instructions
are available with the course. In brief summary however:

## Entering the VM

```bash
git clone git@github.com:ryanchanwo/fullstack-nanodegree-vm.git
cd fullstack-nanodegree-vm/vagrant
vagrant up
vagrant ssh
```

## Setting up the database

The database needs to be manually setup with a few simple commands.

```bash
cd /vagrant/tournament
psql
```

```sql
\i tournament.psql
```

## Running the tests

To ensure the system is working as expected, the course provides a few basic test
cases that can be run from the command line.

```bash
python tournament_test.py
```

Successfully passing the tests should be indicated by the following statement:

```
Success!  All tests pass!
```

# Afterthoughts

I would highly recommend the course for anybody wanting to begin some gentle learning of
relational databases and SQL. There are numerous quizes throughout the course to keep you
interested, and the final assignment (this project) is _challenging enough_.
