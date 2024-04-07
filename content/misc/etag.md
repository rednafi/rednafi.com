---
title: Etag, caching, and optimistic concurrency
date: 2024-04-06
tags:
    - API
    - Go
---

The HTTP `ETag` header is pretty slick. It lets your server guide clients on how to:

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

The basic workflow goes as follows:

-   The client makes a `GET` request to the server.
-   The server responds with a `200 OK` status, including the content requested and an
    `ETag` header.
-   The client caches the response locally, along with the `ETag` value.
-   For subsequent requests to the same resource, the client includes the `If-None-Match`
    header with the `ETag` value it has cached.
-   The server checks if the `ETag` value sent by the client matches the current version of
    the resource.
    -   If they match, the server responds with a `304 Not Modified` status, indicating that
        the client's cached version is still valid and the client serves the resource from
        the cache.
    -   If they don't match, the server responds with a `200 OK status`, including the new
        content and a new ETag header, prompting the client to update its cache.

```txt
Client                                 Server
  |                                       |
  |----- GET Request -------------------->|
  |                                       |
  |<---- Response 200 OK + ETag ----------|
  |     (Cache response locally)          |
  |                                       |
  |----- GET Request + If-None-Match ---->|  (If-None-Match == previous Etag)
  |                                       |
  |       Does ETag match?                |
  |<---- Yes: 304 Not Modified -----------|  (No body sent; Use local cache)
  |       No: 200 OK + New ETag ----------|  (Update cached response)
  |                                       |
```

We can test this workflow with GitHub's REST API suite via the GitHub CLI[^5]. If you've
installed the CLI and authenticated yourself, you can make a request like this:

```sh
gh api -i  /users/rednafi
```

This asks for the data associated with the user `rednafi`. The response looks as follows:

```txt
HTTP/2.0 200 OK
ETag: W/"b8fdfabd59aed6e0e602dd140c0a0ff48a665cac791dede458c5109bf4bf9463"

{
  "login":"rednafi",
  "id":30027932,
  ...
}
```

We've truncated the response body and omitted the headers that aren't relevant to our
discussion. You can see that the HTTP status code is `200 OK` and the server has included an
`ETag` header.

The `W/` prefix indicates that a weak validator[^6] is used to validate the content of the
cache. Let's see what happens if we make the same request again while passing the value of
the `ETag` in the `If-None-Match` header.

```sh
gh api -i -H \
    'If-None-Match: W/"b8fdfabd59aed6e0e602dd140c0a0ff48a665cac791dede458c5109bf4bf9463"' \
    /users/rednafi
```

This returns:

```txt
HTTP/2.0 304 Not Modified
ETag: "b8fdfabd59aed6e0e602dd140c0a0ff48a665cac791dede458c5109bf4bf9463"

gh: HTTP 304
```

A few key points to keep in mind:

-   Always wrap your `ETag` values in double quotes when sending them with the
    `If-None-Match` header, just as the spec says[^7].

-   Using the `If-None-Match` header to pass the `ETag` value means that the request is
    considered successful when the `ETag` value from the client doesn't match that of the
    server. When the values match, the server will return `304 Not Modified` with no body.

-   If we're writing a compliant server, when it comes to `If-None-Match`, the spec tells
    us[^8] to use a weak comparison for ETags. This means that the client will still be able
    to validate the cache with weak ETags, even if there have been slight changes to the
    representation of the data.

## Update via `PUT` request with OCC

## A server that enables client-side caching and OCC

[^1]:
    [Optimistic concurrency control](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)

[^2]: [Etag - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag)
[^3]: [If-Match - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Match)
[^4]:
    [If-None-Match - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-None-Match)

[^5]: [GitHub CLI](https://cli.github.com/)
[^6]:
    [Weak validation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests#weak_validation)

[^7]:
    [Double quote in conditional header values](https://www.rfc-editor.org/rfc/rfc7232#section-3.2)

[^8]:
    [Use weak comparison for Etags while caching](https://www.rfc-editor.org/rfc/rfc7232#section-2.3.2)
