---
layout: post
title:  "Replication in distributed databases"
date: 2021-09-20
tags:
  - database
  - distributed
usemathjax: true
---
I've been recently been reading [Designing Data-Intensive Applications][ddia],
a treasure to learn more about distributed systems. In this post, I will
discuss about replication issues while designing/using a distributed databases.
While this post by no means is meant to be exhaustive, we will touch upon
state of art techniques and various design considerations you should think
of while designing your application.

There are three major replication strategies (for simplicity, we will assume no
partitioning of the data).

## Single Leader Replication
Single leader node and other nodes are its followers. All write requests are
sent to the leader node. The leader node forwards the writes to the follower
nodes, either synchronously or asynchronously. Read requests can be processed by
any node.

### Synchronous v/s asynchronous
With synchronous replication, all nodes will have an up-to-date copy of the
data.
However, the leader node must block on all nodes.
This isn't ideal when a node dies or there's network congestion.

As a middle ground, one follower node can be synchronous and others
asynchronous.
If the synchronous follower dies or falls behind, some other node can be made
synchronous follower.

### Setting up new followers
We want to ensure there's no downtime. Towards this end, we first take a
snapshot of the DB, copy it to the new node and then process all the changes
that have happened since then (e.g. by reading from a log file).

### Node Outages

#### Follower failure
When the node recovers, it can request all changes that happened since the time
it was offline from the leader node (i.e. leader's log file).

#### Leader failure
This is trickier:
1. Determining leader has failed e.g. by heartbeat.
2. Choose a new leader node by some process or consensus.
3. Clients should send requests to the new leader.
4. Other nodes should start consuming data changes from this new leader.

This process is called *failover*.

- Asynchronous replication can lead to data corruption.
- If leader election is not implemented correctly, there can be multiple
leaders (*split brain*).

### Gotchas
This works well for read heavy systems.
If we add more nodes, it might degrade the performance of a synchronous system.
With asynchronous system, there might be delays in propagation and
the read value from a replica might be stale, before it eventually catchos up.
This effect is called *eventual consistency*.

This might have following consequences:

1. **read-after-write consistency** or **read-your-write consistency**
You submit some data and refresh the page.
The read request to fetch this data now goes to a different replica and
the previous submitted data disappears.
This might also happen when you are using multiple devices.
Possible resolutions:
  - Read recently modified data from leader node. Might make leader very busy.
Can be somewhat obviated by reading from all nodes except those which have a
high lag.
  - Some client side logic to store time of last update and discard any reads
coming from a replica with a stale timestamp.

2. **monotic read consistency**
You read something, refresh the page and the read disappears
(different replica which hasn't been updated).
Monotic read consistency ensures that data once read can't be unread.

3. **consistent prefix reads**
Suppose you are eavesdropping on two people's conversations.
You might read the answer first followed by question later
(different order of write on a replica).
Consistent prefix reads consistency ensures the order of reads is the same
as order of writes.

## Multi Leader Replication
Multi Leader Replication is useful in write heavy system.
In case of multiple datacenters, it makes sense to have a leader in each
datacenter.
Each leader replicates its changes to other datacenters' leader nodes who in
turn propagate it to their follower nodes.

### Write conflicts
Since each leader writes independently (asynchronously), there can be write
conflicts where two leader nodes have conflicting writes. We can make the
writes synchronous but that's akin to single leader replication.

1. Let client handle conflicts, e.g., by always routing their request to the
same leader.
2. Conflict resolution must happen in a convergent way
(all nodes eventually have the same copy of data).
Possible approaches includes:
  - Each write gets a unique ID (e.g. timestamp) and the highest one wins.
  - Each replica gets a unique ID and the write from highest replica one wins.
  - Custom logic to merge the two writes, e.g., concatenation.
  - Application specific code for dealing with merge conflicts.
    This can either happen on write or on read (of the conflict data).

A conflict can also be global in nature
(e.g. a booking system where each room can be booked by at most one user at any
given time). The approaches described above won't work.

### Replication topologies
There can be multiple topologies for leader nodes,
e.g., circular, star or all-to-all.
Care must be taken to avoid infinite writes.
Circular and star topologies are prone to single node failure whereas
all-to-all is prone to network congestion.
Also, we might run into consistent prefix read issues.

## Leaderless Replication
Here, we ditch the notion of leader and each write blocks on multiple nodes.
The write succeeds if some fraction of the write succeeds.
For read, as we might be reading from a stale node, we read from multiple nodes
and keep the one with the latest timestamp.

There are a couple of ways for a node to update its stale state:
1. **Read repair** When a client makes several requests in parallel, it updates
any stale response.
2. **Anti-entropy process**
A background job which keeps updating the stale data.

### Quorom for reads and writes
Suppose there are $$n$$ replicas.
If we wait on $$w$$ replicas to ack their writes and
$$r$$ replicas to ack their reads,
then, to get a up-to-date value on reading, $$w + r > n$$.
This ensures there's at least one replica in common.
Typically, $$n$$ is odd and we set $$w$$ and $$r$$ to $$(n + 1) / 2$$.

Note that this approach fails in the case some most up-to-date snapshot fails
and the data there is loaded from a not so recent snapshot.
In case of concurrent writes/reads, not all replicas would
have been updated and we may end up reading stale data.

#### Sloppy Quorums and Hinted Handoffs
Typically, there exists a set of $$n$$ home nodes where the reads/writes happen.
In case of network interruption, a bunch of those nodes might be available for
write.
In this case, the writes may be processed by non-home nodes.
It might result in a stale read.
This is known as *sloppy quorum*.

When the network heals,
these non-home nodes send the write to appropriate home nodes.
This is called *hinted-handoff*.

This approach can be used for increased write availability.

### Detecting concurrent writes
Leaderless replication, by itself, doesn't guarantee eventual consistency
as different nodes can have different values.
We discuss a few techniques for conflict resolution.

#### Last write wins
The clients also pass a timestamp and the commit with latest timestamp wins.

### "Happens-before" relationship and concurrency
Some writes are truely concurrent (e.g. $$set ~ X=A$$ and $$set ~ X=B$$)
whereas others are causally dependent (e.g. $$set ~ X=A$$ and $$set ~ X=X+1$$).

Suppose there are two users $$X$$ and $$Y$$
trying to add grocery items to the same cart.
$$X$$ adds $$A$$ and the node returns $$([A], 1)$$
($$1$$ being the version here).
$$Y$$ adds $$B$$. Now there's a conflict and the node returns $$([A], [B], 2)$$.
This indicates there's a conflict (which $$B$$ is aware of).
Now, if $$B$$ has to add more items, it can merge $$A$$ and $$B$$.

### Merging concurrently written values
With the last approach, unmerged values are possible.
We can have some client side logic for resolving such conflicts
e.g. by taking a union of all items.
This might not work if a user also wants to delete items.

### Version vectors
Here, we extend causal dependency to multiple nodes by having a version number
per replica (in addition to per key).

[ddia]: https://dataintensive.net/
