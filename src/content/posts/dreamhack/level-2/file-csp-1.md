---
title: DreamHack - [file-csp-1 challenge writeup]
published: 2025-11-20
description: Writeup for the file-csp-1 challenge (level 2)
image: ''
tags: [DreamHack, level-2, CSP]
category: Writeups
draft: false
---

## Goal
Write a CSP header that satifies the conditions to obtain the flag.

## Solution
The goal of this problem is to block `a()`, `b()` and allow `c()`, `$(document)` (also the script to load jquery).

The query load script can be allowed easily by using its sha256 hash value.
```python
script-src 'sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8=' 
```

But the `b()` and `c()` has the same nonce value, so we need some ways to distinguish it. 
I read the CSP document, and found [this](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP#strict_csp). Turns out, we can also use hash-based strict CSP like this `script-src 'sha256-{HASHED_SCRIPT}'`. This will be different between `b()` and `c()`.

To get the sha256 value of the final script tag, we must specify exactly the code (including \n, \t), but not including the script tag.
To do so, we can open the console and type the following:
```javascript
document.querySelector('script[nonce="i_am_super_random"]').textContent;
```

The output is:
```
\n\t\tfunction c() { return 'c'; }\n\t\tdocument.write('c: allow me!<br>');\n\t\ttry { $(document); document.write('jquery: allow me!<br>'); } catch (e) {  }\n\t
```

Then we can use [CSP Hash](https://centralcsp.com/features/hashes), paste this code in (remember to replace \n with newline, \t with tab) and we can get the following hash.
```
'sha256-l1OSKODPRVBa1/91J7WfPisrJ6WCxCRnKFzXaOkpsY4='
```

So our payload will be:
```javascript
script-src 'sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8=' 'sha256-l1OSKODPRVBa1/91J7WfPisrJ6WCxCRnKFzXaOkpsY4='
```

Enter this to `/verify` and we obtain the flag.

`FLAG: DH{csp-is-good_XD}`