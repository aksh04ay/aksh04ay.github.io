---
layout: post
title:  "Resources for system design interview preparation"
date: 2024-06-09
tags:
  - system-design
usemathjax: true
---

I was recently looking at prep material for system design interviews. Enumerating the ones I found useful:

1. [System Design primer][sd-primer] - A condensed introduction to various topics relevant to System Design. This could be your baby steps for system design interview prep. The repo also has resources for a few specific system design questions, but I feel they could use some more work.
2. [Grokking the System Design Interview][grokking] - A first hand introduction of what to really expect in a system design interview. It provides a basic blueprint to approach a system design problem and then delves into multiple examples. While a lot of the material presented here makes sense, I feel it still lacks the correct structure to a system design problem.
3. [System Design Interview – An insider's guide][alex-yu] (Both Volume [I][alex-yu] & [II][alex-yu-2]) - Perhaps the most famous & comprehensive guide for System Design interview prep. Highly recommended (See this [review][alex-yu-review] of the book on pragmatic engineer's blog). I think the first volume skimps a few things which are needed if you are going for senior levels. The second volume is more complete. Must read.
4. [Designing Data-Intensive Applications (aka DDIA book)][ddia] - Brilliantly written book. It's not directly related to interview prep, but goes into a lot of depth of building distributed systems. The text is well written and easy to follow. If you have a couple of weeks to spare, it's a must read book. The chapters on storage (B+ v/s LSM trees), replication, partition, transactions and consistency/consensus are highly recommended. I think this book should be read even if you are not prepping for interviews.
5. [Acing the System Design Interview][acing-sd] - This book is along the lines of System Design Interview book and is more recent. It's broadly divided into 2 parts - the first part is more theoretical concepts and the second part looks at more concrete examples. I liked the first part, but felt there was lot of cruft in the second part and could have probably used fewer number of pages. In any case, most of the examples presented herein is subsumed by the more famous System Design Interview book.
6. [System Design Interview Channel][sd-interview-yt] - This is a youtube channel. While there are not many videos, the ones the author has posted are of top quality. Makes sense to go through all the videos.
7. [Jordan has no life][jordan] - Another youtube channel. It's not a full blow system design interview - the author talks of multiple building blocks of a system design (think  event driven architecture, CDC, CDN, pubsub, etc.). Useful to brush up these topics. More recently, you will find videos on concrete system design problems.
8. [Hello Interview][hello-interview] - A more recent resource by an ex-Meta employee. I would rate its solutions to be of the highest quality. I think technically knowing about a system design problem is just first part of battle. The remaining part is how you present it in a time constrained interview setting. I don't think any other resource does justice to the presentation aspect. Hello interview goes into the right depth from an interview perspective - too little may mean you are not comprehensive enough and too much may mean you are wasting too much time. Also, some of their comments on level specific knowledge is really useful. It helped me gauge what really separates a software engineer at a mid v/s senior v/s staff level from a System Design perspective.

Sounds a lot? I agree! If you are razor focussed on interviews, you can start with System Design Interview book and branch from there.

Besides, what you do at work should be the real playground for system design experience (obviously!). From my experience, this holds true in a smaller enviroment where you are handle things end to end. In a larger setting, you tend to focus too deep into the problem at hand. Anyhow, I digress!

I plan to write more articles on system design interview prep - so stay tuned. Got more recommendations? Get in touch!

[sd-primer]: https://github.com/donnemartin/system-design-primer
[grokking]: https://www.designgurus.io/course/grokking-the-system-design-interview
[alex-yu]: https://a.co/d/4yNCXje
[alex-yu-2]: https://a.co/d/10cZQg2
[alex-yu-review]: https://blog.pragmaticengineer.com/system-design-interview-an-insiders-guide-review/
[ddia]: https://dataintensive.net/
[acing-sd]: https://www.manning.com/books/acing-the-system-design-interview
[sd-interview-yt]: https://www.youtube.com/@SystemDesignInterview
[jordan]: https://www.youtube.com/@jordanhasnolife5163
[hello-interview]: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
