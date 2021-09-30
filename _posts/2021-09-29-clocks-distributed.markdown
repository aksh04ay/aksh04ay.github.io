---
layout: post
title:  "Clocks in distributed systems"
date: 2021-09-29
tags:
  - distributed
usemathjax: true
---
Clocks and time are ubiquitous on computers.
However, on a distributed system with multiple nodes,
things get tricky: time on different nodes might be out of sync.
Possible causes include (but not limited to) not perfectly accurate hardware
and network delays while trying to sync time.

Some degree of synchronization is achieved by syncing with a main clock
which gets its time from a more accurate source like GPS receiver.
This mechanism is known as Network Time Protocol (NTP).
This is still prone to network lags.

Modern computers have two different types of clock:

1. **Time-of-day clocks** It returns the seconds (or milliseconds) since epoch.
It is periodically synced with NTP.
As such, we may observe oddities like jumping back in time.
2. **Monotonic clocks** These clocks are always guaranteed to move forward.
The absolute values here do not make much sense:
these are useful for measuring durations.
NTP can adjust the frequency with which monotonic clock moves forward
(skewing the clock) but can't reset the time.

Java's `System.currentTimeMillis()` is a time-of-day clock
whereas `System.nanoTime()` is a monotonic clock.

Multiple things can go wrong with clock synchronization and accuracy:
1. Hardware clock in a computer is not accurate and it drifts over time.
2. Too much drift followed by a sync can move the time back or forward.
3. Network delay can limit the efficiency of NTP synchronization.
4. Reliance on an external service (NTP) for clock synchronization.
5. [Leap seconds][leap-seconds], if not properly handled, can mess up a clock.
6. On VMs, hardware clock is virtualized. This can cause problems.
  If a VM is paused and then unpaused, it manifests as jumping forward in time
  from an application's perspective.
7. Users deliberately resetting the time on their devices.

One important use of timestamps is for ordering of events
e.g. in case of assigning an order to transactions on a database.
Two transactions $$t_1$$ and $$t_2$$
(occurring on nodes $$A$$ and $$B$$ respectively) might not be concurrent.
If the clocks on $$A$$ and $$B$$ are out-of-sync,
the transaction ids might be flipped
(i.e. $$t_1.id > t_2.id$$ even though
$$t_1$$ finished before $$t_2$$ started).
If the two transactions are not commutative, the database would be in an
inconsistent state on a third replica $$C$$.

Since the clock reading can never be accurate,
another idea is to report a confidence interval for time.
This can be based on expected clock shift (based on previous shift with NTP),
NTP server's uncertainty and network lag.
Google's spanner uses this idea to implement snapshot isolation:
a causal ordering between two transactions exists only if
the confidence interval of their timestamp based id's do not overlap.
If it does, spanner waits for one transaction to be over.
Furthermore, it deploys a GPS receiver based clock in each datacenter to
minimize the CI width.

[leap-seconds]: https://en.wikipedia.org/wiki/Leap_second
