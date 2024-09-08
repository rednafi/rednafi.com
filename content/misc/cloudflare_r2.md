---
title: Adopting Cloudflare R2 for asset management
date: 2024-09-08
tags:
    - Networking
---

Roughly five years ago, when I first started writing here, this blog had so few readers that
asset optimization wasn't even on my radar. I write in plain Markdown, which Hugo turns into
HTML artifacts with some stylings. Whenever I push to the mainline, GitHub Actions deploys
the HTML files to GitHub Pages. Fonts, CSS, and JS assets are all served from the same
origin, and with GitHub's default caching, I didn't feel the need to complicate things with
CDNs.

This straightforward setup has worked great for the past few years. But one thing I’ve
always struggled with is managing the images on this blog. There aren't many—just a few
screenshots—but they've been scattered everywhere. Some are hosted on Imgur, some are buried
deep in GitHub issues, and others are strewn across various repositories. There’s no
streamlined process; I did whatever seemed easiest. This made updating images a bit of a
hassle, as there wasn’t a single place where all the images were neatly stored.

Now, with an encouragingly increasing number of visitors, I've noticed that the latency in
loading the images have gone up. So I wanted to do a few things to optimize the asset
management:

-   Adopt a CDN to centralize all the static assets like fonts, images, CSS, JS for easier
    management.
-   Add a caching layer since most of the stylings don't change that often.

It's not a lot of work but I've been dreading the idea of consolidating all these images and
updating the references in the Markdown. These are the tasks that LLMs shine in and I wanted
to see how much of the gruntwork I could do using GPT-4o. My workplace pays for OpenAI
enterprize plan but not for Claude and I'm not seeing much of a difference between the
capablilites of these two. So gippity it is!

The first step was to look for a place to stash all the static files. AWS S3 comes to mind
first.

## Why not S3

I love S3 and have been using it for years. It's so prevalent now that the S3 API has become
the de facto standard for object storage. It's a familiar tool I wanted to consider first.
However, a few things annoy me:

-   How cumbersome it is to get started with AWS.
-   How difficult authentication and permissions are.
-   How complicated the pricing model is, making it tough to predict costs in case of a
    sudden traffic spike.
-   How much fiddling I'd have to do to create a public bucket under my own custom
    subdomain. I wanted to serve the content from `https://blob.rednafi.com` instead of some
    generic AWS URL.
-   Egress bandwidth fees feel like extortion.
-   Reading AWS docs pro bono feels like torture.

So unless it's for work, I tend to avoid the big clouds like a plague in general. Plus,
other than the domain, hosting the site costs me zero dollars and it generates zero dollars
in revenue. I want to maintain the status quo on both ends. So I went looking for something
else.

## Discovering Cloudflare R2

My domain is already registered with Cloudflare and I use the Workers for all kinds of fun
little projects. However, until today, I've never looked into R2, it's blob storage
offering. Turns out, it's pretty neat and maintains S3 API compatibility. Also, there's no
egress bandwidth fee and the pricing model is trivially simple. Their free tier is extremely
generous. As of now, it offers 10 GB storage, 1 million class A operation (writes and list),
and 10 million class B operations (read) per months for free. That's all there is to the
pricing model.

The UI is minimal and unlike the big clouds, the docs are actually readable. It took me 4
clicks just to create a public bucket and assign a custom subdomain so that I could serve my
assets from the following paths:

-   https://blog.rednafi.com/static/css/
-   https://blog.rednafi.com/static/js/
-   https://blog.rednafi.com/static/images/
-   https://blog.rednafi.com/static/fonts/

A configured bucket looks like this:

![configured r2 bucket][img_1]

## Making ChatGPT do the grunt work of consolidating the images

## Adding the cache layer

[img_1]: https://blog.rednafi.com/static/images/cloudflare_r2/img_1.png
