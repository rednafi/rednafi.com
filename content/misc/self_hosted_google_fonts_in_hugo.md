---
title: Self-hosted Google Fonts in Hugo
date: 2023-09-14
tags:
    - Meta
    - TIL
---

This [site] is built with [Hugo] and served via [GitHub pages]. Recently, I decided to
change the font here to make things more consistent across different devices. However, I
didn't want to go with Google Fonts for a few reasons:

* CDN is another dependency.
* Hosting static assets on GitHub Pages has served me well.
* Google Fonts tracks users and [violates] GDPR in Germany. Google Analytics does that too.
But since I'm using the latter anyway, this might come off a bit apocryphal.
* I wanted to get a few extra Lighthouse points.

Turns out, it's pretty easy to host the fonts yourself.

## Download the fonts

I found this fantastic [webfont helper tool] that allows you to search for any Google font
and download it. You can specify the font style, thickness, and browser support status. I've
used it to download Inter for text and JetBrains Mono for code snippets, targeting only
modern browsers. You might want to pick *Legacy Support* if you need compatibility with
older browsers and *Historic Support* for the really old ones.

![download google fonts][image_1]

After downloading, unzip the file and place the fonts in the `/static/fonts` folder in your
root directory. If you've selected the *Modern Browsers* option, then the fonts will come in
web-optimized `woff2` format. Sweet!

## Paste the CSS

While downloading the fonts, you may have already noticed that the helper tool also
generates the CSS snippet required to link the fonts from the host storage. Here's a sample:

```css
/* schibsted-grotesk-regular - latin */
@font-face {
  font-display: swap;
  font-family: 'Schibsted Grotesk';
  font-style: normal;
  font-weight: 400;
  src: url('../fonts/schibsted-grotesk-v3-latin-regular.woff2')
    format('woff2');
}

/* schibsted-grotesk-italic - latin */
@font-face {
  font-display: swap;
  font-family: 'Schibsted Grotesk';
  font-style: italic;
  font-weight: 400;
  src: url('../fonts/schibsted-grotesk-v3-latin-italic.woff2')
    format('woff2');
}

/* truncated */
```

Copy the generated CSS and paste it somewhere in your `header.css` or
`assets/css/extended/header-override.css` file if you're overriding a theme. Edit the `src`
attribute to reflect your font's path:

```css
@font-face {
    font-display: swap;
    font-family: 'Schibsted Grotesk';
    font-style: normal;
    font-weight: 400;
    /* url('../fonts/schibsted-grotesk-v3-latin-regular.woff2'); */
    src: url('/fonts/schibsted-grotesk-v3-latin-regular.woff2')
      format('woff2');
}
```

Here, you'll need to change `../fonts/<rest>` to `/fonts/<rest>`, and Hugo will take care of
the rest. Notice there's no `/static` prefix in the font's path. Find this blog's
[header-override.css] if you're facing any trouble while doing it. Serve your website
locally and ensure that the fonts are being loaded and displayed correctly. Deploy!

[violates]: https://rewis.io/urteile/urteil/lhm-20-01-2022-3-o-1749320/
[hugo]: https://gohugo.io/
[github pages]: https://pages.github.com/
[webfont helper tool]: https://gwfh.mranftl.com/fonts
[image_1]: https://user-images.githubusercontent.com/30027932/267879992-c61a4008-d05f-45f4-9cee-ca7435bd2459.png
[header-override.css]: https://github.com/rednafi/rednafi.com/blob/main/assets/css/extended/header-override.css
[site]: https://github.com/rednafi/rednafi.com/