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

A transaction is a group of reads and writes
lumped together into a logical unit.
Our aim is the entire should transaction should succeed.
If it fails, we rollback the whole transaction and let client retry.
In a way, transaction provides safety guarantees.

Transactions are supposed to provide ACID:
1. **Atomicity**: The whole transaction occurs in an atomic fashion.
  It either succeeds or is wholly aborted, but not left midway.
2. **Consistency**: Data always remains in a consistent state.
  It's more of an application layer invariant
  rather than database layer invariant.
3. **Isolation**: Concurrently running executions are isolated from each other.
  If there two transactions to be committed,
  the final result will be the same as if they had run serially.
  This isolation is also known as *serializability*.
  It typically carries a performance overhead.
  As such, we will look at weaker isolation levels.
4. **Durability**: Any committed transaction's data won't ever be forgotten,
  even if there's a hardware or database crash.
  It involves writing to a non-volatile storage or replication.
  Writing to non-volatile storage may violate availability
  in case of power failures.

Consistency is application logic.
Durability is mostly related to [replication][replication].
As such, we will mainly focus on atomicity and isolation here.

## Weak Isolation levels
Serializability has high performance cost.
We will look at weaker (non-serializable) levels of isolation.

### Read Committed
It makes two guarantees:
1. When you read, you only see data that has been committed (no *dirty reads*).
2. When you write, you only (over) write data that has been committed
  (no *dirty writes*).

#### No dirty reads
Suppose there are two transactions one of which is trying to update two rows
and the other is trying to read the same two rows.
No dirty read implies that the second transaction either sees old value for
both the rows or new values for both the rows.
It can't be the case that one row is old and the other is new.

In this case, write blocks reads.

#### No dirty writes
Suppose there are two transactions both of which are trying to update the same
two rows.
No dirty writes implies that one transaction must be fully committed
(or aborted) before the other transaction can be started.

In this case, write blocks writes.

Note that read committed isolation is not as strong as serializable isolation.
Suppose two transactions are concurrently trying to update a counter
(by first reading its value and writing a value one greater than read value).
A read committed compliant isolation might be something like
the two transactions both first read the counter and
then both write a value.
The final written value will be only one greater than read value.
This happened because read isn't blocking write.

#### Implementation
Dirty writes can be avoided by using row-level locks.
When a transaction wants to update a set of rows,
it acquires a lock for them and releases when the transaction is committed.
As such, no parallel writes can happen.

We can apply a similar strategy to avoid dirty reads.
The problem is
one long running write transaction can force lots of read transactions to wait.
Instead, the database can remember both the old and new value
set by transactions that currently hold the lock.

### Snapshot Isolation and Repeatable Read
Read Committed Isolation is not exhaustive:
consider a scenario where you are transferring $100
from one account to another.
The transaction might look something like you deduct the balance from
one account and add it to another.
If you happen to read the balance of the two accounts in between,
you will be short by $100.
This anomaly is called *nonrepeatable read* or *read skew*.
If you read the balances again, the balances would be as expected.

This might be a real problem if, e.g.,
you want to take snapshot of the entire database.

*Snapshot isolation* is the idea that each transaction reads from a
*consistent snapshot* of the database, i.e.,
any transaction is either committed, aborted or not started at all.
It is particularly useful for creating backups.

#### Implementation
The key principle we follow here is
*readers do not block writers* and *writers do not block readers*.

Towards this end, we give each transaction a unique monotonically increasing
transaction id (``txid``).
All data written during a transaction is tagged with its `txid`.
Each row has multiple different versions representing various
transactions which have modified its value.
Additionally, each version has two more fields, `created_by` and `deleted_by`,
which correspond to the `txid`'s of the transactions which created and deleted
this version.
When we modify a row in transaction `txid`,
we don't actually modify it,
but mark the `deleted_by` of latest version with `txid` and
create a new version with the new values whose
`created_by` is `txid` and `deleted_by` is `nil`.

While reading, we use following visibility rules to determine which
versions to discard:
1. Any write made by a transaction which was in-progress when the current
  transaction started are discarded.
2. Any write made by a later transaction are discarded, even if it has been
  committed.
3. Any writes made by aborted transaction are discarded.
4. All other writes are applicable. If there are multiple versions, pick the
  one with a higher transaction id.

In other words, only consider those transactions which started before this
transaction and have been committed.
In addition, we can have a background GC job which can keep compacting versions
from committed transactions.
To maintain indexes, we need to maintain indexes for each version
(and discard upon GC).

### Preventing Lost Updates
Read Committed and Snapshot Isolation provides good guarantees about
read-only transactions.
However, they are not good enough in cases, e.g.,
two transactions trying increment the same counter.
This is known as *lost update* problem.

One common theme in *lost update* is a *read-modify-write* cycle.
Another example is two users modifying the same wiki page.
We will see a few techniques to resolve them.

1. **Atomic Writes** Make the database write atomic
  (e.g., `UPDATE counter SET value = value + 1 where key = 'foo'`).
  It can be implemented by acquiring an exclusive lock on the object
  being modified.
  This might not be feasible in all situations (e.g. wiki editing).
2. **Explicit Locking** Similar as atomic write but
  have the application developer handle locking.
3. **Automatic Detection** Allow execution in parallel and
  abort a transaction (retry) in case a lost update is detected.
  It can be implemented in conjuction with snapshot isolation implementation.
4. **Compare-and-set** Check the value of a row before updating it atomically
  (e.g. `UPDATE counter SET value = value + 1 where key = 'foo' and value = 42`)
  .

Preventing lost updates can be more problematic in replicated databases as
different nodes can have different copies.
While atomic operations can work if they are commutative,
compare-and-set is not so useful as there is no single node to compare against.
We would need some strategy like manual resolution or last write wins.

### Write Skew and Phantoms
Here, we will another race condition which is more global in nature.
Imagine a scenario of oncall setup where multiple persons can be oncall at
any given time but at least someone must be oncall at any time.
Suppose there are two persons who are oncall at a given time.
They might both chose to go on vacation (as there's someone who still oncall).
But if they both go on vacation, there would be no oncall left.
A similar situation occurs in room scheduling where each room can be booked by
at most one meeting in any given time interval.

This anomaly is called *write skew*.
The approaches discussed in prior section won't work here
as the problem is sort of more global in nature.
You can possibly use a lock, but it must be acquired for multiple rows.

The general pattern is:
1. A read query matching some precondition.
2. Depending on the results (which are based on a precondition),
  some write queries are issued.

The problem is write of one transaction changes other read results returned
in first step based on precondition.
This effect is called a *phantom*.

#### Materializing conflicts
Consider the meeting room booking problem.
Imagine creating a table whose rows correspond to
a particular room for a particular time period (room id X time period).
A transaction trying to create a booking can lock the rows
corresponding to desired time and time period.
It can then check for availability and insert a new booking.
Note that this new table is not holding any information.
It is purely a collection of locks.
This approach is called *materializing conflicts* as it takes a phantom and
turns it into a concrete set of rows.

## Serializability
Serializable Isolation guarantees that even though transactions may execute
concurrently, the end result is the same as if they were executed serially.
We will look at a few serialization techniques.

### Actual Serial Execution
Here, we implement transactions sequentially one at a time
(on a single machine and single core).
This has only been possible in recent years owing to bigger RAM.

This is not situable for transaction which requires
interactive I/O from the user
(as we need to block other transactions).
For multiple read/write in a single transaction,
a lot of time can be spent in network communication between DB and application.
Rather, we introduce another layer between application and storage,
called *stored procedure*.
The application batches all queries belonging to a transaction
and sends it to stored procedure for execution.

Sometimes replication also happens via stored procedure.
In this case, stored procedure must be deterministic.

If the data is to be partitioned, the structure should be such that
each stored procedure touches only a single partition.
Else, we will have to block on multiple partitions which might not be efficient.


### 2 Phase Locking

### Serializable Snapshot Isolation



[replication]: replication
