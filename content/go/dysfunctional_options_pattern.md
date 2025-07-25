---
title: Dysfunctional options pattern in Go
date: 2024-03-06
tags:
    - Go
---

Ever since Rob Pike published the text on the [functional options pattern], there's been no
shortage of blogs, talks, or comments on how it improves or obfuscates configuration
ergonomics.

While the necessity of such a pattern is quite evident in a language that lacks default
arguments in functions, more often than not, it needlessly complicates things. The situation
gets worse if you have to maintain a public API where multiple configurations are controlled
in this manner.

However, the pattern solves a valid problem and definitely has its place. Otherwise, it
wouldn’t have been picked up by pretty much every other library, whether it's [Ngrok] or the
[Elasticsearch agent].

If you have no idea what I'm talking about, you might want to give my previous write-up on
[configuring options] a read.

## Functional options pattern

As a recap, here's how the functional options pattern works. Let's say, you need to allow
the users of your API to configure something. You can expose a struct from your package
that'll be passed to some other function to tune its behavior. For example:

```go
package src

type Config struct {
    // Required
    Foo, Bar string

    // Optional
    Fizz, Bazz int
}

func Do(config *Config) {
    // Do something with the config values
}
```

Then the `Config` struct will be imported, initialized, and passed to the `Do` function by
your API users:

```go
package main

import ".../src"

func main() {
    // Initialize the config and pass it to the Do function
    config := &src.Config{
        Foo: "hello",
        Bar: "world",
        Fizz: 0,
        Bazz: 42,
    }

    // Call Do with the initialized Config struct
    src.Do(config)
}
```

This is one way of doing that, but it's generally discouraged since it requires you to
expose the internals of your API to the users. So instead, a library usually exposes a
factory function that'll do the struct initialization while keeping the struct and fields
private. For instance:

```go
package src

type config struct { // Notice that the struct and fields are now private
    // Required
    foo, bar string

    // Optional
    fizz, bazz int
}

// Public factory function
func NewConfig(foo, bar string, fizz, bazz int) config {
    return config{foo, bar, fizz, bazz}
}

func Do(c *config){}
```

The API consumers will now use `NewConfig` to produce a configuration and then pass the
struct instance to the `Do` function as follows:

```go
package main

import ".../src"

func main() {
    // Initialize the config with the NewConfig factory
    c := &src.NewConfig("hello", "world", 0, 42)

    // Call Do with the initialized Config struct
    src.Do(c)
}
```

This approach is better as it keeps the internal machinery hidden from users. However, it
doesn't allow for setting default values for some configuration attributes; all must be set
explicitly. What if your users want to override the values of multiple attributes? This
leads your configuration struct to be overloaded with options, making the `NewConfig`
function demands numerous positional arguments.

This setup isn't user-friendly, as it forces API users to explicitly pass all these options
to the `NewConfig` factory. Ideally, you'd initialize `config` with some default values,
offering users a chance to override them. But, Go doesn't support default values for
function arguments, which compels us to be creative and come up with different workarounds.
Functional options pattern is one of them.

Here's how you can build your API to leverage the pattern:

```go
package src

type config struct {
    // Required
    foo, bar string

    // Optional
    fizz, bazz int
}

type option func(*config)

// The value of each optional configuration attribute can be overridden with
// an associated function
func WithFizz(fizz int) option {
    return func(c *config) {
        c.fizz = fizz
    }
}

func WithBazz(bazz int) option {
    return func(c *config) {
        c.bazz = bazz
    }
}

func NewConfig(foo, bar string, opts ...option) config {
    // First fill in the options with default values
    c := config{foo, bar, 10, 100}

    // Now allow users to override the optional configuration attributes
    for _, opt := range opts {
        opt(&c)
    }
    return c
}

func Do(c *config) {}
```

Then you'd use it as follows:

```go
package main

import ".../src"

func main() {
    c := &src.NewConfig("hello", "world", src.WithFizz(1), src.WithBazz(2))
    src.Do(c)
}
```

Functional options pattern relies on functions that modify the configuration struct's state.
These modifier functions, or option functions, are defined to accept a pointer to the
configuration struct `*config` and then directly alter its fields. This direct manipulation
is possible because the option functions are closures, which means they capture and modify
the variables from their enclosing scope, in this case, the `config` instance.

In the `NewConfig` factory, the variadic parameter `opts ...option` allows for an arbitrary
number of option functions to be passed. Here, `opts` represents the optional configurations
that the users can override if they want to.

The `NewConfig` function iterates over this slice of option functions, invoking each one
with the `&c` argument, which is a pointer to the newly created `config` instance. The
config instance is created with default values, and the users can use the `With*` functions
to override them.

## Curse of indirection

That's a fair bit of indirection just to allow API users to configure some options. I don't
know about you, but multi-layered higher-order functions hurt my brain. It's quite slow as
well.

All this complexity could have been avoided if Go allowed default arguments in functions.
Your configuration factory could simply grab the default values from the keyword arguments
and pass them to the underlying struct. The idea that supporting default arguments in
functions would lead to a parameter explosion seems unfounded, especially when the
alternative requires gymnastics like the functional option pattern.

Also, the multiple layers of indirection hinder API discoverability. Trying to discover
modifier functions by hovering your cursor over the factory function's return value in the
IDE won't be very helpful, as these functions are defined at the package level.

So, if you need to configure multiple structs in this manner, the explosion of their
respective package-level modifiers make it even harder for the user to know which function
they'll need to use to update a certain configuration attribute.

Recently, I've spontaneously stumbled upon a fluent-style API to manage configurations that
don't require so many layers of indirection and lets you expose optional configuration
attributes. Let's call it **dysfunctional options pattern**.

## Dysfunctional options pattern

The idea is quite similar to how the API with functional options pattern is constructed.
Here's the complete implementation:

```go
package src

type config struct {
    // Required
    foo, bar string

    // Optional
    fizz, bazz int
}

// Each optional configuration attribute will have its own public method
func (c *config) WithFizz(fizz int) *config {
    c.fizz = fizz
    return c
}

func (c *config) WithBazz(bazz int) *config {
    c.bazz = bazz
    return c
}

// This only accepts the required options as params
func NewConfig(foo, bar string) *config {
    // First fill in the options with default values
    return &config{foo, bar, 10, 100}
}

func Do(c *config) {}
```

You'd use the API as follows:

```go
package main

import ".../src"

func main() {
    // Initialize the struct with only the required options and then chain
    // the option methods to update the optional configuration attributes
    c := src.NewConfig("hello", "world").WithFizz(0).WithBazz(42)
    src.Do(c)
}
```

Similar to the previous pattern, we have modifiers here too. However, instead of being
higher order functions, the modifiers are methods on `config` and return a pointer to the
struct.

The `NewConfig` factory function instantiates the `config` struct with some default values
and returns the struct pointer like the modifiers. This enables us to chain the `WithFizz`
and `WithBazz` modifiers on the returned value of `NewConfig` and update the values of the
optional configuration attributes.

Apart from simplicity and the lack of magic, you can hover over the return type of the
factory and immediately know about the supported modifier methods.

I did a [rudimentary benchmark] of the two approaches and was surprised that the second one
was roughly ~76x faster on Go 1.22!

Here's an example of the [pattern in the wild].

_P.S. This is indeed a lightweight spin on what OO languages call the builder pattern.
However, I didn't call it that because there's no mandatory `.Build()` method to be called
at the end of the method chain._

<!-- Resources -->
<!-- prettier-ignore-start -->

[functional options pattern]:
    https://commandcenter.blogspot.com/2014/01/self-referential-functions-and-design.html

<!-- functional options pattern in ngrok -->
[ngrok]:
    https://github.com/ngrok/ngrok-api-go/blob/ec1a3e91cae94c70f0e5c31b95aed5a1d6dd65b7/client_config.go

<!-- functional options pattern in elasticsearch agent -->
[elasticsearch agent]:
    https://github.com/elastic/elastic-agent/blob/4aeba5b3fcf0d72924c70ff2127996a817b83a23/pkg/testing/fetcher_http.go

<!-- configuring options in go - rednafi -->
[configuring options]:
    /go/configure_options

<!-- benchmarking functional vs dysfunctional options pattern -->
[rudimentary benchmark]:
    https://gist.github.com/rednafi/08fe371ed31072ab0bd96bf51611660a

<!-- dysfunctional options pattern in the wild -->
[pattern in the wild]:
    https://github.com/rednafi/fork-sweeper/blob/80e1f7c76a2efcb7d1b65d6b12303c590bb74c2c/src/cli.go#L172

<!-- prettier-ignore-end -->
