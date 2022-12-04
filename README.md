![Raider logo](./ext/logo.png)

- [Documentation](https://docs.raiderauth.com/en/latest/).
- [Discussions](https://github.com/OWASP/raider/discussions).
- [Issues](https://github.com/OWASP/raider/issues).

# What is Raider

This is a framework initially designed to test and automate the
authentication process for web applications, and by now it has evolved
and can be used for all kinds of stateful HTTP processes. It abstracts
the client-server information exchange as a finite state machine. Each
step comprises one request with inputs, one response with outputs,
arbitrary actions to do on the response, and conditional links to
other stages. Thus, a graph-like structure is created.

Raider's configuration is inspired by Emacs. Hylang is used, which is
LISP on top of Python. LISP is used because of its "Code is Data, Data
is Code" property. It would also allow generating configuration
automatically easily in the future. Flexibility is in its DNA, meaning
it can be infinitely extended with actual code. Since all
configuration is stored in cleartext, reproducing, sharing or
modifying attacks becomes easy.

# Installation

**Raider** is available on PyPi:

```
$ pip install  raider
```

If you would like to test the latest code, you can do so by clonnig
this repository and running it inside poetry:

```
$ git clone https://github.com/OWASP/raider
$ poetry shell
```


