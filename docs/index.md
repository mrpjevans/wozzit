## Wozzit

A simple communication system for the Internet of Things (or anything you want)

- [Message Schema](schema.md)
- [Server](server.md)
- [Python Message Class Reference](msgref.md)
- [Python Server Class Reference](serverref.md)

### The Problem

These days just about anything can be connected to the Internet: Doorbells, central heating, fridges, toasters, banana stands\*. So why is it so difficult to get these things talking to each other without five different 'cloud' accounts and an overly-complicated IFTTT script? After all, if I want to have my coffee machine switch on if the garage door is opened on a Thursday after 4pm, why shouldn't I? \*\*

I was looking for a simple standard for devices, who may not know of each other's existence, to communicate directly or via controlled points. No cloud, no accounts. Although some solution exists, such as Mozilla's Things project, everything I looked at seemed way too over-engineered.

### A Solution

Wozzit is a set of standards for devices to talk to each other. The goal is to provide a simple non-prescriptive method of communication between devices that do not necessarily know of each others existence. To achieve this, Wozzit is comprised of **Messages** and **Servers**.

Wozzit does not dictate which markup you use for a message or what protocol is used to deliver that message. The only requirement is that it complies with a very simple set of rules so anyone can figure out how to communicate with your device.

#### Messages

The Wozzit Messages schema is an agreement on what a message should contain. To provide maximum flexibility, there are very few rules, mainly centring around negotiation. Messages have schemas which determines what they contain. Anyone is free to create their own schemas. All that is asked is that you follow a simple naming convention to keep schema names unique.

Wozzit does not prescribe a particular markup syntax for a message. You can use JSON, YAML, XML, in fact anything that supports nested keypairs. If you're particularly stubborn, an INI file would be possible and completely acceptable.

##### Example

The following is an example Wozzit Message in JSON format:

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "wozzit.example",
		"version": 1,
		"payload": {
			"message": "Hello, world"
		}
	}
}
```

The requirements are:

* Everything in enclosed in a 'wozzit' object (allows for other data to piggyback)
* Defines which protocol version the message is using (semantic versioning)
* Defines a schema of 'wozzit.example'
* Defines which version of the schema is in use (determined by the schema)
* Defines a payload, the content of which is entirely based on the schema

So, a message can contain any data you like in the 'payload' section so long as it adheres to the given schema and version. What the payload contains is completely up to the provider. In the example above, it's just a keypair of 'message' and the string 'Hello, world'. It could be anything so long as it can be represented in the markup used.

#### Server

If we want to exchange messages, we'll need a protocol for doing that. Again, Wozzit attempts to be as non-prescriptive as possible. The initial implementation uses HTTP and JSON for the message format. However, there's no reason to avoid implementations in MQTT, UDP, carrier pigeon, anything. So long as the schema is adhered to at the other end (and they can support the protocol of course), you can communicate.

The server can be configured with any number of rules which can dictate which peers or schemas it will receive messages from and what to do with the received message. Built-in functions include forwarding to another server instance, sending emails or showing desktop alerts. Typically, a callback function is provided by the implementor which can do, well, whatever you can image.

Currently a HTTP server has been implemented which defaults to port 10207.

### Real-World Example

A microcontroller (e.g. Microbit or ESP8266) is using an implementation of wozzit in MicroPython. This provides easy methods for creating compliant messages and sending them to an upstream server. The microcontroller is monitoring a security reed-switch stuck to a doorframe. When the door opens, the MicroPython code detects this. Upon opening, the code sends the following Wozzit Message:

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "wozzit.switch",
		"version": 1,
		"payload": {
			"open": true
		}
	}
}
```

The 'wozzit.switch' schema states that the payload only contains one keypair 'open' which is _true_ if the switch is open or _false_ is the switch is closed.

Here's the code for generating and then sending this message:

```python
import wozzit

msg = wozzit.Message()
msg.schema = "wozzit.switch"
msg.payload = {"status": True}

svr = wozzit.Server()
svr.send(msg=msg, to="http://some.wozzit.server.somewhere:10207/")
```

Upon receiving the message, the wozzit server instance can do what ever it likes. It can forward the message to another server, send an email or run a provided callback.

For example (using Python)

```python
import wozzit

# Define a callback function to do print a message when the door opens of closes
def myCallback(msg):
	if msg.payload['state'] == True:
		print "Door is open!"
	else:
		print "Door is closed!"

# Create a new server instance with defaults
server = wozzit.Server()

# Attach the callback function to any
# incoming message with a schema of 'wozzit.switch'
server.addListener(match={schema: 'wozzit.switch'}, callback=myCallback):

# Start the HTTP server on port 10207
server.listen()
```

Now, when the door opens, the server will receive the message, parse it and output to the console.

--

\* Ok, not banana stands. Yet.

\*\* Primarily because drinking coffee after 4pm is a really bad idea but hey, it might be decaf. Which is an even worse idea.