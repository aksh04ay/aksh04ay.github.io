---
layout: post
title:  "Transactions in distributed databases"
date: 2021-09-22
tags:
  - database
  - distributed
usemathjax: true
---
As a follow up to [this][replication] post on replication,
I'll discuss transactions in distributed databases.

What is transaction? Why transaction?

ACID in transaction context

E.g. where atomicity and isolation is violated.
Single v/s multi object and why multi is needed.

## Weak Isolation levels

### Read Committed

#### No dirty reads
#### No dirty writes
#### Implementation

### Snapshot Isolation and Repeatable Read

#### Implementation?

### Preventing Lost Updates

#### Atomic Writes
#### Explicit Locking
#### Automatic Detection
#### Compare-and-set

### Write Skew and Phantoms

## Serializability

### Actual Serial Execution

### 2 Phase Locking

### Serializable Snapshot Isolation



[replication]: replication
