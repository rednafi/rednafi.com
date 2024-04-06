---
title: Etag, caching, and optimistic concurrency
date: 2024-04-06
tags:
    - API
    - Go
---

The HTTP `Etag` header is pretty slick. It lets your server guide clients on how to:

-   Cache the response of a `GET` endpoint.
-   Update some resource via `PUT` requests without any locks, enacting _optimistic
    concurrency control (OCC)_[^1].

In the first case, your clients can be more frugal about making requests to the server while
serving the users when the underlying resource doesn't change.

Meanwhile, in the second case, you can avoid in-flight conflicts while attempting to update
a resource. Suppose a client is trying to update a resource on the server. It'll first need
to read the current state of the resource and then proceed to update it.

What happens if another client updates the resource on the server after the first client has
read the state but before it had the chance to update? In this scenario, the first client
shouldn't be allowed to update the resource, since the state it read has become outdated.
The first client should either give up or retry the request to update the resource.

The use of an Etag header combined with a conditional header can gracefully resolve this
in-flight conflict.

To achieve these two things, you'll need to fiddle with the Etag header along with some
conditional headers like `If-Match` and `If-None-Match`. Their interaction can get fairly
confusing. Every time I need to deal with this, I end up spending some time going through
the relevant MDN docs[^2][^3][^4] just to jog my memory. At this point, I've done it enough
times that taking the time to write this piece feels justified.

## Cache the response of a `GET` endpoint

## Update via `PUT` request with OCC

## A server that enables client-side caching and OCC

[^1]:
    [Optimistic concurrency control](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)

[^2]: [Etag - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag)
[^3]: [If-Match - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Match)
[^4]:
    [If-None-Match - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-None-Match)
